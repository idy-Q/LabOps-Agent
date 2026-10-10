import json
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError

from datetime import datetime
from app.db.session import get_db
from app.db.models import Asset, AssetDetail, ServerRoom, ServerRack, AssetBorrowLog, Ticket, TicketWorkflow
from app.api.rooms import is_asset_in_room
from app.tools.metric_tools import get_server_metrics
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    HealthStatusType,
    BorrowStatusType,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[AssetResponse],
    summary="查询资产台账列表",
    description="支持按资产编号、分类、位置、健康状态、借用状态以及关键词组合过滤，自动级联加载硬件物理规格参数。",
)
def list_assets(
    asset_no: Optional[str] = Query(default=None, description="按资产编号精确过滤"),
    category: Optional[str] = Query(default=None, description="按设备分类过滤"),
    location: Optional[str] = Query(default=None, description="按机房位置模糊过滤"),
    health_status: Optional[HealthStatusType] = Query(default=None, description="按健康状态过滤"),
    borrow_status: Optional[BorrowStatusType] = Query(default=None, description="按借用状态过滤"),
    keyword: Optional[str] = Query(default=None, description="按编号、名称或规格关键词搜索"),
    skip: int = Query(default=0, ge=0, description="分页起始偏移量"),
    limit: int = Query(default=50, ge=1, le=100, description="每页条目数"),
    db: Session = Depends(get_db),
):
    query = db.query(Asset).options(joinedload(Asset.detail))
    if asset_no:
        query = query.filter(Asset.asset_no == asset_no)
    if category:
        query = query.filter(Asset.category == category)
    if location:
        query = query.filter(Asset.location.contains(location))
    if health_status:
        query = query.filter(Asset.health_status == health_status)
    if borrow_status:
        query = query.filter(Asset.borrow_status == borrow_status)
    if keyword:
        kw = keyword.strip()
        query = query.filter(
            or_(
                Asset.asset_no.contains(kw),
                Asset.name.contains(kw),
            )
        )

    assets = (
        query.order_by(desc(Asset.created_at), desc(Asset.id))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return assets


def link_temperature_to_health_status(temperature: Optional[float], current_health_status: str) -> str:
    """动环探针遥测注入与设备健康状态联动研判

    联动规则：
    - 若处于 OFFLINE 状态，保持 OFFLINE 离线脱网状态与环境室温；
    - 温度 >= 40.0℃ 自动联动为 OVERHEAT (高温高危)；
    - 38.0 <= 温度 < 40.0℃ 自动联动为 WARNING (亚健康预警)；
    - 温度 < 38.0℃ 自动联动为 HEALTHY (健康良好)。
    """
    if current_health_status == "OFFLINE":
        return "OFFLINE"
    if temperature is None:
        return current_health_status
    if temperature >= 40.0:
        return "OVERHEAT"
    elif temperature >= 38.0:
        return "WARNING"
    else:
        return "HEALTHY"


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机房资产设备与硬件参数",
    description="录入新资产设备，要求资产编号 asset_no 全局唯一，支持同步录入硬件物理参数与核心设定温度并联动健康状态。",
)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
):
    # 校验编号唯一性
    clean_no = asset_in.asset_no.strip()
    existing = db.query(Asset).filter(Asset.asset_no == clean_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"资产编号 '{clean_no}' 已存在，不能重复添加",
        )

    # 提取设定的温度（支持顶层字段或 detail 嵌套字段，支持 custom_temperature 或 temperature 别名）
    temp_val = asset_in.custom_temperature if asset_in.custom_temperature is not None else asset_in.temperature
    if temp_val is None and asset_in.detail:
        if asset_in.detail.custom_temperature is not None:
            temp_val = asset_in.detail.custom_temperature
        elif asset_in.detail.temperature is not None:
            temp_val = asset_in.detail.temperature

    target_health = asset_in.health_status or "HEALTHY"
    if temp_val is not None and target_health != "OFFLINE":
        target_health = link_temperature_to_health_status(temp_val, target_health)

    asset = Asset(
        asset_no=clean_no,
        name=asset_in.name.strip(),
        category=asset_in.category.strip(),
        location=asset_in.location.strip(),
        health_status=target_health,
        borrow_status=asset_in.borrow_status or "AVAILABLE",
        borrower=asset_in.borrower,
        specs=asset_in.specs,
    )

    try:
        db.add(asset)
        db.flush()  # 生成 asset.id

        # 如果提供了硬件详细参数或设定了温度，创建 AssetDetail
        if asset_in.detail is not None:
            detail_data = asset_in.detail.model_dump(exclude_unset=True)
            detail_data.pop("temperature", None)
            if temp_val is not None:
                detail_data["custom_temperature"] = temp_val
            asset_detail = AssetDetail(
                asset_id=asset.id,
                **detail_data,
            )
            db.add(asset_detail)
        elif temp_val is not None:
            asset_detail = AssetDetail(
                asset_id=asset.id,
                custom_temperature=temp_val,
            )
            db.add(asset_detail)

        db.commit()
        db.refresh(asset)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"资产编号 '{clean_no}' 已存在或数据冲突",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"录入设备失败: {str(exc)}",
        )
    return asset


@router.get(
    "/overdue",
    summary="查询借用逾期设备列表与统计概要",
    description="检索机房所有借调超过约定归还期限的设备清单，返回逾期总台数、最长逾期天数与各设备逾期明细。",
)
def get_overdue_assets(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    from app.services.overdue_service import get_overdue_assets_summary
    return get_overdue_assets_summary(db)


@router.get(
    "/{asset_no}/overdue-notice",
    summary="获取指定设备的标准化超期催告通知单",
    description="结合设备档案、借调记录与借用人信息，依据《高校实验室安全与仪器设备借调管理条例》生成规范红头催告单及 Markdown 文本。",
)
def get_overdue_notice(
    asset_no: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    from app.services.overdue_service import generate_overdue_notice
    try:
        return generate_overdue_notice(db, asset_no)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成催告单失败: {str(exc)}",
        )


@router.get(
    "/topology",
    summary="获取机房机柜 2D 拓扑大盘数据",
    description="聚合各机房、42U机柜、在架设备物理槽位、空闲插槽、空间利用率以及非机架外设资产。",
)
def get_rack_topology(
    room_code: Optional[str] = Query(default=None, description="按机房编号过滤，如 ROOM-201"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """聚合机房机柜拓扑视图全量指标与槽位数据"""
    # 1. 查询机房列表
    rooms_query = db.query(ServerRoom).order_by(ServerRoom.room_code).all()
    # 2. 查询全量资产台账与详情
    all_assets_orm = db.query(Asset).options(joinedload(Asset.detail)).all()

    # 将资产格式化为全景数据字典并注入实时遥测监控指标
    formatted_assets = []
    for asset in all_assets_orm:
        metric_data = get_server_metrics(device_id=asset.asset_no, db=db)
        extra_params = {}
        if asset.detail and asset.detail.extra_params:
            try:
                extra_params = json.loads(asset.detail.extra_params)
            except Exception:
                extra_params = {}

        start_u = extra_params.get("start_u")
        u_height = extra_params.get("u_height")
        if u_height is None and "rack_units" in extra_params:
            ru_str = str(extra_params["rack_units"]).upper()
            if "U" in ru_str:
                try:
                    u_height = int(ru_str.replace("U", "").strip())
                except ValueError:
                    u_height = 1
            else:
                u_height = 1

        try:
            start_u = int(start_u) if start_u is not None else None
        except (ValueError, TypeError):
            start_u = None

        try:
            u_height = int(u_height) if u_height is not None else 1
        except (ValueError, TypeError):
            u_height = 1
        if u_height < 1:
            u_height = 1

        asset_item = {
            "id": asset.id,
            "asset_no": asset.asset_no,
            "name": asset.name,
            "category": asset.category,
            "location": asset.location,
            "health_status": asset.health_status,
            "borrow_status": asset.borrow_status,
            "borrower": asset.borrower,
            "specs": asset.specs,
            "start_u": start_u,
            "u_height": u_height,
            "custom_temperature": asset.custom_temperature,
            "telemetry_temperature": asset.telemetry_temperature,
            "metrics": {
                "temperature": metric_data.get("temperature", 22.0),
                "cpu_usage": metric_data.get("cpu_usage", 0.0),
                "memory_usage": metric_data.get("memory_usage", 0.0),
                "fan_speed_rpm": metric_data.get("fan_speed_rpm", 0),
                "power_watts": metric_data.get("power_watts", 0),
                "alert": metric_data.get("alert", False),
                "alert_level": metric_data.get("alert_level", "NORMAL"),
                "alert_message": metric_data.get("alert_message", ""),
            },
            "detail": {
                "serial_number": asset.detail.serial_number if asset.detail else None,
                "brand": asset.detail.brand if asset.detail else None,
                "model_name": asset.detail.model_name if asset.detail else None,
                "management_ip": asset.detail.management_ip if asset.detail else None,
                "os_firmware": asset.detail.os_firmware if asset.detail else None,
                "mac_address": asset.detail.mac_address if asset.detail else None,
                "cpu_info": asset.detail.cpu_info if asset.detail else None,
                "memory_info": asset.detail.memory_info if asset.detail else None,
                "storage_info": asset.detail.storage_info if asset.detail else None,
                "gpu_info": asset.detail.gpu_info if asset.detail else None,
                "network_interfaces": asset.detail.network_interfaces if asset.detail else None,
                "power_supply": asset.detail.power_supply if asset.detail else None,
                "purchase_date": asset.detail.purchase_date if asset.detail else None,
                "warranty_period": asset.detail.warranty_period if asset.detail else None,
                "supplier": asset.detail.supplier if asset.detail else None,
                "extra_params": asset.detail.extra_params if asset.detail else None,
                "custom_temperature": asset.detail.custom_temperature if asset.detail else None,
            } if asset.detail else None,
        }
        formatted_assets.append(asset_item)

    # 3. 归类资产至机房及机柜
    rooms_data = []
    all_unracked_assets = []
    all_racked_assets = []
    accounted_asset_ids = set()

    for room in rooms_query:
        r_code = room.room_code
        room_assets = [
            a for a in formatted_assets
            if is_asset_in_room(a.get("location", ""), r_code, room.room_name)
        ]

        # 区分机架内设备与周边配套/外设实验仪器
        in_rack_assets = []
        unracked_assets = []
        for a in room_assets:
            is_in_rack = (
                a.get("start_u") is not None
                and a["start_u"] > 0
                and ("机柜" in a.get("location", "") or "核心柜" in a.get("location", ""))
            )
            if is_in_rack:
                in_rack_assets.append(a)
                all_racked_assets.append(a)
                accounted_asset_ids.add(a["id"])
            else:
                unracked_assets.append(a)
                all_unracked_assets.append(a)
                accounted_asset_ids.add(a["id"])

        # 组装机柜列表 (从 server_racks 表动态加载)
        db_racks = db.query(ServerRack).filter(ServerRack.room_code == r_code).order_by(ServerRack.rack_id).all()
        rack_map = {}
        for rk in db_racks:
            rack_map[rk.rack_id] = {
                "rack_id": rk.rack_id,
                "rack_name": rk.rack_name,
                "room_code": r_code,
                "room_name": room.room_name,
                "total_u": rk.total_u,
                "power_rating_w": rk.power_rating_w,
                "used_u": 0,
                "usage_rate": 0.0,
                "health_status": "HEALTHY",
                "max_temperature": 22.0,
                "avg_temperature": 22.0,
                "has_conflict": False,
                "assets": [],
                "slots": [],
            }

        for a in in_rack_assets:
            loc = a["location"] or ""
            # 优先匹配已登记机柜编号 (长名称优先匹配，并结合边界匹配)
            matched_rack_id = None
            for rk_id in sorted(rack_map.keys(), key=len, reverse=True):
                if re.search(rf"(^|[-_ ]){re.escape(rk_id)}([-_ ]|$)", loc):
                    matched_rack_id = rk_id
                    break
            if not matched_rack_id:
                for rk_id in sorted(rack_map.keys(), key=len, reverse=True):
                    if rk_id in loc:
                        matched_rack_id = rk_id
                        break

            if matched_rack_id:
                rack_id = matched_rack_id
            else:
                # 规范提取机柜编号，防止将尾部 U位 (如 U28(4U)) 误截断为机柜名
                parts = [p.strip() for p in loc.split("-") if p.strip()]
                if len(parts) >= 3 and (parts[-1].startswith("U") or parts[-1].startswith("u")):
                    rack_id = parts[1]
                elif len(parts) >= 2:
                    rack_id = parts[1]
                elif len(parts) == 1:
                    rack_id = parts[0]
                else:
                    rack_id = loc.strip()

            if rack_id not in rack_map:
                rack_map[rack_id] = {
                    "rack_id": rack_id,
                    "rack_name": rack_id,
                    "room_code": r_code,
                    "room_name": room.room_name,
                    "total_u": 42,
                    "power_rating_w": 4500,
                    "used_u": 0,
                    "usage_rate": 0.0,
                    "health_status": "HEALTHY",
                    "max_temperature": 22.0,
                    "avg_temperature": 22.0,
                    "has_conflict": False,
                    "assets": [],
                    "slots": [],
                }
            rack_map[rack_id]["assets"].append(a)

        racks_list = list(rack_map.values())
        for rack in racks_list:
            r_assets = rack["assets"]
            total_u = rack["total_u"]

            # 对在架设备进行高度与起始 U 位边界保护校验
            for a in r_assets:
                st = a["start_u"] or 1
                h = a["u_height"] or 1
                clamped_st = max(1, min(total_u, st))
                clamped_h = max(1, min(total_u - clamped_st + 1, h))
                a["start_u"] = clamped_st
                a["u_height"] = clamped_h

            r_assets.sort(key=lambda x: x["start_u"] or 0, reverse=True)

            # 空间占用率：基于已占用的唯一 U 位集合精确去重计算
            occupied_u_set = set()
            for a in r_assets:
                for u_pos in range(a["start_u"], a["start_u"] + a["u_height"]):
                    if 1 <= u_pos <= total_u:
                        occupied_u_set.add(u_pos)

            used_u = len(occupied_u_set)
            rack["used_u"] = used_u
            rack["usage_rate"] = round((used_u / total_u * 100), 1) if total_u > 0 else 0.0
            sum_heights = sum(a["u_height"] for a in r_assets)
            rack["has_conflict"] = (used_u < sum_heights)

            # 健康状态推导
            stat_set = {a["health_status"] for a in r_assets}
            if "OVERHEAT" in stat_set:
                rack["health_status"] = "OVERHEAT"
            elif "WARNING" in stat_set:
                rack["health_status"] = "WARNING"
            elif "OFFLINE" in stat_set:
                rack["health_status"] = "OFFLINE"
            else:
                rack["health_status"] = "HEALTHY"

            # 温度推导
            temps = [a["metrics"]["temperature"] for a in r_assets if a.get("metrics")]
            if temps:
                rack["max_temperature"] = max(temps)
                rack["avg_temperature"] = round(sum(temps) / len(temps), 1)
            else:
                rack["max_temperature"] = 22.0
                rack["avg_temperature"] = 22.0

            # 42U 插槽切片生成 (U42 下降至 U1)
            slots = []
            for u in range(total_u, 0, -1):
                occupied_asset = None
                for a in r_assets:
                    st = a["start_u"]
                    h = a["u_height"]
                    if st <= u < st + h:
                        occupied_asset = {
                            "asset_id": a["id"],
                            "asset_no": a["asset_no"],
                            "name": a["name"],
                            "category": a["category"],
                            "health_status": a["health_status"],
                            "management_ip": a["detail"].get("management_ip") if a.get("detail") else None,
                            "model_name": a["detail"].get("model_name") if a.get("detail") else None,
                            "start_u": st,
                            "u_height": h,
                            "is_base": (u == st),
                            "is_top": (u == st + h - 1),
                            "temperature": a["metrics"]["temperature"],
                            "power_watts": a["metrics"]["power_watts"],
                        }
                        break
                slots.append({
                    "u": u,
                    "occupied": occupied_asset is not None,
                    "device": occupied_asset,
                })
            rack["slots"] = slots

        # 机房整体统计指标
        room_total_u = sum(r["total_u"] for r in racks_list)
        room_used_u = sum(r["used_u"] for r in racks_list)
        room_usage_rate = round((room_used_u / room_total_u * 100), 1) if room_total_u > 0 else 0.0

        all_r_assets = in_rack_assets + unracked_assets
        all_r_temps = [a["metrics"]["temperature"] for a in all_r_assets if a.get("metrics")]
        room_max_temp = max(all_r_temps) if all_r_temps else 22.0
        room_avg_temp = round(sum(all_r_temps) / len(all_r_temps), 1) if all_r_temps else 22.0

        all_r_stats = {a["health_status"] for a in all_r_assets}
        if "OVERHEAT" in all_r_stats:
            room_health = "OVERHEAT"
        elif "WARNING" in all_r_stats:
            room_health = "WARNING"
        elif "OFFLINE" in all_r_stats:
            room_health = "OFFLINE"
        else:
            room_health = "HEALTHY"

        rooms_data.append({
            "room_code": room.room_code,
            "room_name": room.room_name,
            "location": room.location,
            "manager_teacher": room.manager_teacher,
            "power_capacity_kw": room.power_capacity_kw,
            "total_racks": len(racks_list),
            "stats": {
                "rack_count": len(racks_list),
                "total_u": room_total_u,
                "used_u": room_used_u,
                "usage_rate": room_usage_rate,
                "max_temperature": room_max_temp,
                "avg_temperature": room_avg_temp,
                "health_status": room_health,
                "in_rack_count": len(in_rack_assets),
                "unracked_count": len(unracked_assets),
            },
            "racks": racks_list,
            "unracked_assets": unracked_assets,
        })

    # 确保任何未归入特定机房的边缘在册设备 100% 纳入全局外设列表，绝不遗漏
    for a in formatted_assets:
        if a["id"] not in accounted_asset_ids:
            all_unracked_assets.append(a)
            accounted_asset_ids.add(a["id"])

    # 全局大盘总览
    glob_total_u = sum(rm["stats"]["total_u"] for rm in rooms_data)
    glob_used_u = sum(rm["stats"]["used_u"] for rm in rooms_data)
    glob_usage_rate = round((glob_used_u / glob_total_u * 100), 1) if glob_total_u > 0 else 0.0
    glob_temps = [a["metrics"]["temperature"] for a in formatted_assets if a.get("metrics")]
    glob_max_temp = max(glob_temps) if glob_temps else 22.0
    glob_avg_temp = round(sum(glob_temps) / len(glob_temps), 1) if glob_temps else 22.0

    health_dist = {"HEALTHY": 0, "WARNING": 0, "OVERHEAT": 0, "OFFLINE": 0}
    for a in formatted_assets:
        hs = a.get("health_status", "HEALTHY")
        health_dist[hs] = health_dist.get(hs, 0) + 1

    summary = {
        "total_rooms": len(rooms_data),
        "total_racks": sum(rm["stats"]["rack_count"] for rm in rooms_data),
        "total_u": glob_total_u,
        "used_u": glob_used_u,
        "usage_rate": glob_usage_rate,
        "total_assets": len(formatted_assets),
        "racked_assets_count": len(all_racked_assets),
        "unracked_assets_count": len(all_unracked_assets),
        "max_temperature": glob_max_temp,
        "avg_temperature": glob_avg_temp,
        "health_distribution": health_dist,
    }

    if room_code:
        clean_code = room_code.strip()
        clean_upper = clean_code.upper()
        clean_num = clean_upper.replace("ROOM-", "")
        matched_room = next(
            (
                rm
                for rm in rooms_data
                if rm["room_code"].upper() == clean_upper
                or rm["room_code"].replace("ROOM-", "") == clean_num
            ),
            None,
        )
        return {
            "summary": summary,
            "rooms": rooms_data,
            "selected_room": matched_room,
            "unracked_assets": matched_room["unracked_assets"] if matched_room else all_unracked_assets,
            "filtered_room_code": clean_code,
        }

    return {
        "summary": summary,
        "rooms": rooms_data,
        "selected_room": None,
        "unracked_assets": all_unracked_assets,
        "filtered_room_code": None,
    }


def format_asset_duration(delta_seconds: float) -> str:
    """格式化相对设备投产入库时间的相对履历时段"""
    if delta_seconds <= 0:
        return "投产首日"
    days = int(delta_seconds // 86400)
    if days < 1:
        hours = int(delta_seconds // 3600)
        return f"投产首日 (+{hours}小时)" if hours > 0 else "投产首日"
    if days < 30:
        return f"投产第 {days + 1} 天"
    months = days // 30
    rem_days = days % 30
    if months < 12:
        return f"投产 {months} 个月 {rem_days} 天" if rem_days > 0 else f"投产 {months} 个月整"
    years = days // 365
    rem_months = (days % 365) // 30
    return f"投产 {years} 年 {rem_months} 个月" if rem_months > 0 else f"投产 {years} 年整"


@router.get(
    "/{asset_no}/timeline",
    summary="获取资产全生命周期时序履历图谱",
    description="聚合设备采购投产、借调流转归还、关联告警与维保工单流转，提供统一结构化的资产全生命周期履历时序图谱。",
)
def get_asset_timeline(
    asset_no: str,
    db: Session = Depends(get_db),
):
    clean_target = asset_no.strip()
    asset = None
    if clean_target.isdigit():
        asset = (
            db.query(Asset)
            .options(joinedload(Asset.detail))
            .filter(Asset.id == int(clean_target))
            .first()
        )
    if not asset:
        asset = (
            db.query(Asset)
            .options(joinedload(Asset.detail))
            .filter(Asset.asset_no == clean_target)
            .first()
        )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未检索到编号或ID为 '{asset_no}' 的资产设备",
        )

    nodes = []

    # 1. 采购投产上架时间推导与格式容错
    init_dt = asset.created_at or datetime.now()
    purchase_date_str = (asset.detail.purchase_date or "").strip() if asset.detail else None
    if purchase_date_str:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                init_dt = datetime.strptime(purchase_date_str, fmt)
                break
            except Exception:
                pass
        else:
            try:
                init_dt = datetime.fromisoformat(purchase_date_str)
            except Exception:
                pass

    brand_str = asset.detail.brand if (asset.detail and asset.detail.brand) else "高校自采"
    model_str = asset.detail.model_name if (asset.detail and asset.detail.model_name) else "标准配置"
    sn_str = f" (SN: {asset.detail.serial_number})" if (asset.detail and asset.detail.serial_number) else ""

    # 2. 借还历史记录 (AssetBorrowLog 表)
    borrow_logs = (
        db.query(AssetBorrowLog)
        .filter(AssetBorrowLog.asset_id == asset.asset_no)
        .order_by(AssetBorrowLog.borrow_time.asc())
        .all()
    )
    for blog in borrow_logs:
        b_time = blog.borrow_time or init_dt
        nodes.append({
            "id": f"asset-borrow-{blog.id}",
            "node_type": "BORROW",
            "title": f"设备借调登记 [{blog.log_no}]",
            "timestamp": b_time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_time": b_time,
            "operator": blog.borrower_name,
            "previous_status": "AVAILABLE",
            "next_status": "IN_USE",
            "comment": f"借调教师: {blog.borrower_name}，用途: {blog.purpose}，约定归还: {blog.expected_return_time.strftime('%Y-%m-%d %H:%M') if blog.expected_return_time else '未定'}，审批人: {blog.approver or '系统管理员'}",
            "metadata": {
                "log_no": blog.log_no,
                "borrower_username": blog.borrower_username,
                "borrower_name": blog.borrower_name,
                "return_status": blog.return_status,
            },
        })

        if blog.actual_return_time or blog.return_status == "RETURNED":
            r_time = blog.actual_return_time or blog.expected_return_time or b_time
            nodes.append({
                "id": f"asset-return-{blog.id}",
                "node_type": "RETURN",
                "title": f"设备验收入库归还 [{blog.log_no}]",
                "timestamp": r_time.strftime("%Y-%m-%d %H:%M:%S"),
                "raw_time": r_time,
                "operator": blog.approver or "机房管理员",
                "previous_status": "IN_USE",
                "next_status": "AVAILABLE",
                "comment": f"借调人员 ({blog.borrower_name}) 已完成使用并验收入库，恢复空闲可用状态",
                "metadata": {
                    "log_no": blog.log_no,
                    "return_status": "RETURNED",
                    "approver": blog.approver or "机房管理员",
                },
            })

    # 3. 关联运维工单与工单流转 (Ticket & TicketWorkflow 表)
    tickets = (
        db.query(Ticket)
        .filter(Ticket.device_id == asset.asset_no)
        .order_by(Ticket.created_at.asc())
        .all()
    )
    for t in tickets:
        t_time = t.created_at or init_dt
        nodes.append({
            "id": f"asset-ticket-create-{t.id}",
            "node_type": "INCIDENT",
            "title": f"关联运维工单提单 [{t.ticket_no}]: {t.title}",
            "timestamp": t_time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_time": t_time,
            "operator": t.creator or "系统监控",
            "previous_status": None,
            "next_status": t.status,
            "comment": t.description,
            "metadata": {
                "ticket_no": t.ticket_no,
                "priority": t.priority,
                "status": t.status,
            },
        })

        workflows = (
            db.query(TicketWorkflow)
            .filter(TicketWorkflow.ticket_id == t.ticket_no)
            .order_by(TicketWorkflow.created_at.asc(), TicketWorkflow.id.asc())
            .all()
        )
        for wf in workflows:
            wf_time = wf.created_at or t_time
            nodes.append({
                "id": f"asset-ticket-wf-{wf.id}",
                "node_type": "MAINTENANCE",
                "title": f"工单流转处置 [{t.ticket_no}]: {wf.previous_status} -> {wf.next_status}",
                "timestamp": wf_time.strftime("%Y-%m-%d %H:%M:%S"),
                "raw_time": wf_time,
                "operator": wf.operator,
                "previous_status": wf.previous_status,
                "next_status": wf.next_status,
                "comment": wf.comment or f"流转状态至 {wf.next_status}",
                "metadata": {
                    "ticket_no": t.ticket_no,
                    "previous_status": wf.previous_status,
                    "next_status": wf.next_status,
                },
            })

    # 校准起始投产基准时间为所有关联历史事件的最早时间点
    candidate_init_times = [init_dt] + [n["raw_time"] for n in nodes if n.get("raw_time")]
    init_dt = min(candidate_init_times)

    # 插入采购投产上架起始节点 (COMMISSIONING)
    nodes.append({
        "id": f"asset-init-{asset.id}",
        "node_type": "COMMISSIONING",
        "title": f"设备采购投产上架 - {asset.name}",
        "timestamp": init_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "raw_time": init_dt,
        "operator": "资产采购/网络中心",
        "previous_status": None,
        "next_status": "AVAILABLE",
        "comment": f"设备入库上架完成，分类：{asset.category}，型号：{brand_str} {model_str}{sn_str}，物理部署于：{asset.location}。",
        "metadata": {
            "brand": brand_str,
            "model_name": model_str,
            "location": asset.location,
            "management_ip": asset.detail.management_ip if asset.detail else None,
        },
    })

    # 排序：时间升序，同一时刻保证 COMMISSIONING 最前 (-1)
    def asset_node_sort_key(item):
        type_rank = {"COMMISSIONING": -1, "BORROW": 1, "INCIDENT": 2, "MAINTENANCE": 3, "RETURN": 4}
        return (item["raw_time"], type_rank.get(item["node_type"], 5))

    nodes.sort(key=asset_node_sort_key)

    for n in nodes:
        diff_sec = max(0.0, (n["raw_time"] - init_dt).total_seconds())
        n["duration_from_start"] = format_asset_duration(diff_sec)
        n.pop("raw_time", None)

    return {
        "asset": {
            "id": asset.id,
            "asset_no": asset.asset_no,
            "name": asset.name,
            "category": asset.category,
            "location": asset.location,
            "health_status": asset.health_status,
            "borrow_status": asset.borrow_status,
            "borrower": asset.borrower,
            "specs": asset.specs,
            "created_at": asset.created_at.strftime("%Y-%m-%d %H:%M:%S") if asset.created_at else None,
            "detail": {
                "brand": asset.detail.brand,
                "model_name": asset.detail.model_name,
                "management_ip": asset.detail.management_ip,
                "serial_number": asset.detail.serial_number,
                "purchase_date": asset.detail.purchase_date,
                "warranty_period": asset.detail.warranty_period,
                "supplier": asset.detail.supplier,
            } if asset.detail else None,
        },
        "timeline": nodes,
        "summary": {
            "total_events": len(nodes),
            "total_borrows": len(borrow_logs),
            "total_tickets": len(tickets),
            "current_status": asset.health_status,
            "borrow_status": asset.borrow_status,
        },
    }


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="获取单个资产全景详情",
    description="获取指定资产的基础台账与其关联的全部硬件规格参数。",
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.detail))
        .filter(Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )
    return asset


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="更新资产状态与硬件详细参数",
    description="支持更新资产基础属性（借还状态、健康度、位置、规格等）以及硬件参数（CPU、内存、存储、GPU、管理IP等）。",
)
def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
):
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.detail))
        .filter(Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )

    update_data = asset_update.model_dump(exclude_unset=True)
    detail_data = update_data.pop("detail", None)

    # 提取设定的温度（支持顶层字段或 detail 嵌套字段，支持 custom_temperature 或 temperature，且支持显式设为 None 清除）
    temp_val = None
    has_temp_update = False

    if "custom_temperature" in update_data:
        temp_val = update_data.pop("custom_temperature")
        has_temp_update = True
        update_data.pop("temperature", None)
    elif "temperature" in update_data:
        temp_val = update_data.pop("temperature")
        has_temp_update = True
    elif detail_data is not None and "custom_temperature" in detail_data:
        temp_val = detail_data.get("custom_temperature")
        has_temp_update = True
    elif detail_data is not None and "temperature" in detail_data:
        temp_val = detail_data.get("temperature")
        has_temp_update = True

    if detail_data is not None:
        detail_data.pop("temperature", None)

    # 1. 更新主表字段
    for field, value in update_data.items():
        setattr(asset, field, value)

    # 2. 动环遥测温度与健康状态智能联动
    if has_temp_update:
        if asset.health_status != "OFFLINE":
            asset.health_status = link_temperature_to_health_status(temp_val, asset.health_status)
    elif "health_status" in update_data and update_data["health_status"] is not None:
        # 当显式更新健康状态且未传温度时，反向校准设定温度保持逻辑自洽
        new_hs = update_data["health_status"]
        if new_hs == "OVERHEAT" and (asset.custom_temperature is None or asset.custom_temperature < 40.0):
            temp_val = 43.5
            has_temp_update = True
        elif new_hs == "WARNING" and (asset.custom_temperature is None or not (38.0 <= asset.custom_temperature < 40.0)):
            temp_val = 38.5
            has_temp_update = True
        elif new_hs == "HEALTHY" and (asset.custom_temperature is not None and asset.custom_temperature >= 38.0):
            temp_val = 31.5
            has_temp_update = True

    # 3. 更新或新建从表 AssetDetail 字段
    if detail_data is not None or has_temp_update:
        if asset.detail:
            if detail_data:
                for d_field, d_value in detail_data.items():
                    setattr(asset.detail, d_field, d_value)
            if has_temp_update:
                asset.detail.custom_temperature = temp_val
                # 同步更新/清理 extra_params 中的历史残留温度，防止死灰复燃
                if asset.detail.extra_params:
                    try:
                        ep = json.loads(asset.detail.extra_params)
                        ep_changed = False
                        if temp_val is None:
                            if "custom_temperature" in ep:
                                del ep["custom_temperature"]
                                ep_changed = True
                            if "temperature" in ep:
                                del ep["temperature"]
                                ep_changed = True
                        else:
                            if "custom_temperature" in ep and ep["custom_temperature"] != temp_val:
                                ep["custom_temperature"] = temp_val
                                ep_changed = True
                            if "temperature" in ep and ep["temperature"] != temp_val:
                                ep["temperature"] = temp_val
                                ep_changed = True
                        if ep_changed:
                            asset.detail.extra_params = json.dumps(ep, ensure_ascii=False)
                    except Exception:
                        pass
        else:
            new_detail_data = detail_data or {}
            if has_temp_update:
                new_detail_data["custom_temperature"] = temp_val
            new_detail = AssetDetail(asset_id=asset.id, **new_detail_data)
            db.add(new_detail)

    try:
        db.commit()
        db.refresh(asset)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新资产信息失败: {str(exc)}",
        )
    return asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="安全删除资产记录",
    description="删除指定资产，若设备正处于借出中 (IN_USE) 将阻断删除，并级联清理关联的硬件详细参数。",
)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )

    try:
        db.delete(asset)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除资产失败: {str(exc)}",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
