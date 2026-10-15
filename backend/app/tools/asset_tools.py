import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_

from app.db.models import Asset, AssetDetail, AssetBorrowLog, UserNotification, User
from app.tools.registry import tool

VALID_HEALTH_STATUSES = {"HEALTHY", "WARNING", "OVERHEAT", "OFFLINE"}
VALID_BORROW_STATUSES = {"AVAILABLE", "IN_USE", "MAINTENANCE"}


def resolve_asset(
    identifier: str,
    db: Optional[Session] = None,
) -> Optional[Asset]:
    """智能资产解析器：根据资产编号全称、口语简称、后缀编号或设备名称解析目标 Asset 实体。

    支持例如：
    - "DEV-LAB-106" -> 精确匹配
    - "LAB-106" / "lab-106" -> 自动补全 DEV- 前缀
    - "106" -> 后缀编号匹配 DEV-LAB-106
    - "201" -> DEV-SRV-201
    - "ARM综合开发实验箱" -> 名称模糊匹配 DEV-LAB-106
    """
    if not identifier:
        return None
    raw = str(identifier).strip()
    if not raw:
        return None

    import re
    # 仅去除末尾纯语气助词与紧跟在代码/数字后的量词（例如 "lab-106啊" -> "lab-106", "106号机" -> "106"）
    cleaned = re.sub(r"[啊呀呢吧哦吗了呗呐]+$", "", raw).strip()
    cleaned = re.sub(r"(?<=[0-9A-Za-z])(?:号机|号|台|机)$", "", cleaned).strip()
    if not cleaned:
        cleaned = raw

    if db is None:
        return None

    # 1. 严格不区分大小写匹配 asset_no
    asset = db.query(Asset).filter(Asset.asset_no.ilike(cleaned)).first()
    if asset:
        return asset

    # 2. 补全 DEV- 前缀
    if not cleaned.upper().startswith("DEV-"):
        asset = db.query(Asset).filter(Asset.asset_no.ilike(f"DEV-{cleaned}")).first()
        if asset:
            return asset

    # 3. 后缀匹配（如 106 匹配 DEV-LAB-106，201 匹配 DEV-SRV-201）
    asset = db.query(Asset).filter(Asset.asset_no.ilike(f"%-{cleaned}")).first()
    if asset:
        return asset

    # 4. 编号子串包含匹配
    asset = db.query(Asset).filter(Asset.asset_no.ilike(f"%{cleaned}%")).first()
    if asset:
        return asset

    # 5. 设备名称精确/模糊匹配
    asset = db.query(Asset).filter(Asset.name.ilike(f"%{cleaned}%")).first()
    if asset:
        return asset

    # 6. 如果清理后的 cleaned 未匹配到，尝试用原始 raw 再匹配一次名称
    if cleaned != raw:
        asset = db.query(Asset).filter(Asset.name.ilike(f"%{raw}%")).first()
        if asset:
            return asset

    return None



@tool(name="query_assets", description="查询机房设备资产台账，支持按资产编号、名称、机房位置模糊搜索，或按设备分类与健康状态精确过滤")
def query_assets(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    health_status: Optional[str] = None,
    borrow_status: Optional[str] = None,
    limit: int = 10,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """查询资产设备台账列表

    :param keyword: 关键词（模糊匹配资产编号、设备名称、位置或规格配置）
    :param category: 设备分类 (服务器, 网络设备, 实验教学, 配电温控)
    :param health_status: 健康状态 (HEALTHY, WARNING, OVERHEAT, OFFLINE)
    :param borrow_status: 借用状态 (AVAILABLE, IN_USE, MAINTENANCE)
    :param limit: 最多返回条目数，默认 10
    :param db: 数据库会话 (由系统自动注入)
    :return: 匹配的资产列表
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法查询资产台账"}

    try:
        query = active_db.query(Asset).options(joinedload(Asset.detail))

        if keyword and keyword.strip():
            kw = keyword.strip()
            query = query.filter(
                or_(
                    Asset.asset_no.contains(kw),
                    Asset.name.contains(kw),
                    Asset.location.contains(kw),
                    Asset.specs.contains(kw),
                )
            )

        if category and category.strip():
            query = query.filter(Asset.category == category.strip())

        if health_status:
            norm_health = health_status.strip().upper()
            if norm_health in VALID_HEALTH_STATUSES:
                query = query.filter(Asset.health_status == norm_health)

        if borrow_status:
            norm_borrow = borrow_status.strip().upper()
            if norm_borrow in VALID_BORROW_STATUSES:
                query = query.filter(Asset.borrow_status == norm_borrow)

        safe_limit = max(1, min(limit, 50))
        assets = query.order_by(desc(Asset.created_at), desc(Asset.id)).limit(safe_limit).all()

        return {
            "status": "success",
            "count": len(assets),
            "assets": [
                {
                    "id": a.id,
                    "asset_no": a.asset_no,
                    "name": a.name,
                    "category": a.category,
                    "location": a.location,
                    "health_status": a.health_status,
                    "borrow_status": a.borrow_status,
                    "borrower": a.borrower,
                    "specs": a.specs,
                    "detail": {
                        "serial_number": a.detail.serial_number,
                        "brand": a.detail.brand,
                        "model_name": a.detail.model_name,
                        "management_ip": a.detail.management_ip,
                        "cpu_info": a.detail.cpu_info,
                        "memory_info": a.detail.memory_info,
                        "storage_info": a.detail.storage_info,
                        "gpu_info": a.detail.gpu_info,
                        "network_interfaces": a.detail.network_interfaces,
                        "power_supply": a.detail.power_supply,
                        "warranty_period": a.detail.warranty_period,
                    } if a.detail else None,
                }
                for a in assets
            ],
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="borrow_asset", description="办理机房设备资产借出登记。系统具备防重复借出校验，若设备已被借出或处于维护中将拒绝借出")
def borrow_asset(
    asset_no: str,
    borrower: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """办理资产设备借出登记

    :param asset_no: 待借出的资产设备编号，如 DEV-SRV-202
    :param borrower: 借用人姓名或科研团队名称
    :param db: 数据库会话 (由系统自动注入)
    :return: 借出操作结果与最新资产状态
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法办理资产借出"}

    try:
        clean_no = (asset_no or "").strip().upper()
        clean_borrower = (borrower or "").strip()

        if not clean_no or not clean_borrower:
            return {"status": "error", "message": "设备编号和借用人不能为空"}

        asset = resolve_asset(clean_no, db=active_db)
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到匹配 '{clean_no}' 的资产设备"}
        clean_no = asset.asset_no

        # 防重复借用校验
        if asset.borrow_status != "AVAILABLE":
            return {
                "status": "conflict",
                "message": f"资产 '{clean_no}' ({asset.name}) 当前借用状态为 [{asset.borrow_status}]（当前借用人/维护方：{asset.borrower or '无'}），无法重复借出！",
                "asset": {
                    "asset_no": asset.asset_no,
                    "name": asset.name,
                    "borrow_status": asset.borrow_status,
                    "borrower": asset.borrower,
                },
            }

        # 机房运行安全联锁校验 (设备超温 >=40℃ 或处于故障/离线时禁止出借)
        if asset.health_status in ["OVERHEAT", "FAULT", "OFFLINE"] or (
            asset.custom_temperature is not None and asset.custom_temperature >= 40.0
        ):
            temp_desc = f"{asset.custom_temperature}℃" if asset.custom_temperature is not None else "未知"
            return {
                "status": "blocked",
                "message": f"资产 '{clean_no}' ({asset.name}) 当前处于健康异常/超温状态 [{asset.health_status}] (当前温度: {temp_desc})，触发机房安全联锁，禁止借出！",
                "asset": {
                    "asset_no": asset.asset_no,
                    "name": asset.name,
                    "health_status": asset.health_status,
                    "borrow_status": asset.borrow_status,
                    "temperature": asset.custom_temperature,
                },
            }

        asset.borrow_status = "IN_USE"
        asset.borrower = clean_borrower

        # 自动生成并持久化设备借还流转记录 (AssetBorrowLog)
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        prefix = f"BORROW-{date_str}-"
        count = active_db.query(AssetBorrowLog).filter(AssetBorrowLog.log_no.like(f"{prefix}%")).count()
        candidate_log_no = None
        for i in range(count + 1, count + 100):
            cand = f"{prefix}{i:03d}"
            if not active_db.query(AssetBorrowLog).filter(AssetBorrowLog.log_no == cand).first():
                candidate_log_no = cand
                break
        if not candidate_log_no:
            for _ in range(10):
                cand = f"{prefix}{uuid.uuid4().hex[:4].upper()}"
                if not active_db.query(AssetBorrowLog).filter(AssetBorrowLog.log_no == cand).first():
                    candidate_log_no = cand
                    break
        if not candidate_log_no:
            candidate_log_no = f"{prefix}{uuid.uuid4().hex[:6].upper()}"

        # 反查 User 用户表匹配真实登录名 username，避免将中文姓名直接作为系统用户名
        short_borrower_name = clean_borrower.split("(")[0].split("（")[0].strip()
        matched_user = active_db.query(User).filter(
            (User.username == clean_borrower)
            | (User.real_name == clean_borrower)
            | (User.username == short_borrower_name)
            | (User.real_name == short_borrower_name)
            | (User.real_name.contains(short_borrower_name))
        ).first()
        actual_borrower_username = matched_user.username if matched_user else clean_borrower

        borrow_log = AssetBorrowLog(
            log_no=candidate_log_no,
            asset_id=clean_no,
            borrower_username=actual_borrower_username,
            borrower_name=clean_borrower,
            purpose="高校科研与教学实验领用",
            borrow_time=now,
            expected_return_time=now + timedelta(days=14),
            return_status="BORROWING",
            approver="系统管理员",
        )
        active_db.add(borrow_log)

        try:
            active_db.commit()
            active_db.refresh(asset)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"更新资产借用状态失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"设备 '{asset.name}' (编号: {clean_no}) 成功借出登记，当前借用人：{clean_borrower}",
            "asset": {
                "id": asset.id,
                "asset_no": asset.asset_no,
                "name": asset.name,
                "borrow_status": asset.borrow_status,
                "borrower": asset.borrower,
                "location": asset.location,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="return_asset", description="办理机房设备资产归还登记，将设备状态恢复为可借用 (AVAILABLE) 并清空借用人")
def return_asset(
    asset_no: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """办理资产设备归还登记

    :param asset_no: 归还的资产设备编号，如 DEV-SRV-201
    :param db: 数据库会话 (由系统自动注入)
    :return: 归还操作结果与最新资产状态
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法办理资产归还"}

    try:
        clean_no = (asset_no or "").strip().upper()
        if not clean_no:
            return {"status": "error", "message": "资产编号不能为空"}

        asset = resolve_asset(clean_no, db=active_db)
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到匹配 '{clean_no}' 的资产设备"}
        clean_no = asset.asset_no

        if asset.borrow_status == "AVAILABLE":
            return {
                "status": "warning",
                "message": f"资产 '{clean_no}' ({asset.name}) 当前已是可借用状态 (AVAILABLE)，无需重复归还",
                "asset": {
                    "asset_no": asset.asset_no,
                    "name": asset.name,
                    "borrow_status": asset.borrow_status,
                    "borrower": asset.borrower,
                },
            }

        previous_borrower = asset.borrower
        asset.borrow_status = "AVAILABLE"
        asset.borrower = None

        # 自动闭环更新对应借调记录的实际归还时间与状态
        now = datetime.now()
        pending_log = (
            active_db.query(AssetBorrowLog)
            .filter(
                AssetBorrowLog.asset_id == clean_no,
                AssetBorrowLog.return_status.in_(["BORROWING", "OVERDUE"]),
            )
            .order_by(desc(AssetBorrowLog.borrow_time))
            .first()
        )
        if pending_log:
            pending_log.actual_return_time = now
            pending_log.return_status = "RETURNED"
            pending_log.approver = "系统管理员"

        try:
            active_db.commit()
            active_db.refresh(asset)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"归还资产失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"设备 '{asset.name}' (编号: {clean_no}) 归还成功，原借用人：{previous_borrower or '无'}",
            "asset": {
                "id": asset.id,
                "asset_no": asset.asset_no,
                "name": asset.name,
                "borrow_status": asset.borrow_status,
                "borrower": asset.borrower,
                "location": asset.location,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="update_asset_health", description="变更指定设备资产的健康运行等级（HEALTHY 良好、WARNING 预警、OVERHEAT 高温告警、OFFLINE 离线故障）")
def update_asset_health(
    asset_no: str,
    health_status: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """更新资产健康状态

    :param asset_no: 资产设备编号
    :param health_status: 目标健康状态 (HEALTHY, WARNING, OVERHEAT, OFFLINE)
    :param db: 数据库会话 (由系统自动注入)
    :return: 更新结果
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法更新资产健康状态"}

    try:
        clean_no = (asset_no or "").strip().upper()
        norm_status = (health_status or "").strip().upper()

        if norm_status not in VALID_HEALTH_STATUSES:
            return {
                "status": "error",
                "message": f"无效的健康状态 '{health_status}'，可选值为 {list(VALID_HEALTH_STATUSES)}",
            }

        asset = resolve_asset(clean_no, db=active_db)
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到匹配 '{clean_no}' 的资产设备"}
        clean_no = asset.asset_no

        asset.health_status = norm_status

        try:
            active_db.commit()
            active_db.refresh(asset)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"更新资产健康状态失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"资产 '{clean_no}' ({asset.name}) 健康状态已更新为 {norm_status}",
            "asset": {
                "id": asset.id,
                "asset_no": asset.asset_no,
                "name": asset.name,
                "health_status": asset.health_status,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="get_asset_detail", description="查询指定设备资产的完整硬件参数物理规格与详细台账（包含CPU、内存、存储、GPU、管理IP、出厂序列号SN及维保到期日等）")
def get_asset_detail(
    asset_no: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """查询单台设备资产的完整硬件详细参数

    :param asset_no: 资产设备编号，如 DEV-SRV-201
    :param db: 数据库会话 (由系统自动注入)
    :return: 包含主台账与详细硬件参数的字典
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法查询设备详情"}

    try:
        clean_no = (asset_no or "").strip().upper()
        if not clean_no:
            return {"status": "error", "message": "资产编号不能为空"}

        asset = resolve_asset(clean_no, db=active_db)
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到匹配 '{clean_no}' 的资产设备"}
        clean_no = asset.asset_no

        detail_info = None
        if asset.detail:
            d = asset.detail
            detail_info = {
                "serial_number": d.serial_number,
                "brand": d.brand,
                "model_name": d.model_name,
                "os_firmware": d.os_firmware,
                "mac_address": d.mac_address,
                "management_ip": d.management_ip,
                "cpu_info": d.cpu_info,
                "memory_info": d.memory_info,
                "storage_info": d.storage_info,
                "gpu_info": d.gpu_info,
                "network_interfaces": d.network_interfaces,
                "power_supply": d.power_supply,
                "purchase_date": d.purchase_date,
                "warranty_period": d.warranty_period,
                "supplier": d.supplier,
                "extra_params": d.extra_params,
            }

        return {
            "status": "success",
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
                "detail": detail_info,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="add_asset", description="在机房资产台账中录入新设备，支持设置设备编号、名称、分类、机柜位置以及可选的硬件详细参数（型号、管理IP、CPU、内存等）")
def add_asset(
    asset_no: str,
    name: str,
    category: str,
    location: str,
    specs: Optional[str] = None,
    brand: Optional[str] = None,
    model_name: Optional[str] = None,
    management_ip: Optional[str] = None,
    serial_number: Optional[str] = None,
    cpu_info: Optional[str] = None,
    memory_info: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """录入新设备资产与硬件物理参数

    :param asset_no: 资产唯一编号，如 DEV-SRV-206
    :param name: 设备名称，如 2号机房-通用计算节点06
    :param category: 类别 (服务器/网络设备/实验教学/配电温控)
    :param location: 机柜/物理位置，如 实训楼201-机柜A06
    :param specs: 简要规格配置说明
    :param brand: 厂商品牌
    :param model_name: 具体设备型号
    :param management_ip: 带外/管理IP
    :param serial_number: 出厂序列号
    :param cpu_info: CPU规格及核心
    :param memory_info: 内存规格
    :param db: 数据库会话 (由系统自动注入)
    :return: 录入操作结果
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法录入新设备"}

    try:
        clean_no = (asset_no or "").strip().upper()
        clean_name = (name or "").strip()
        clean_category = (category or "").strip()
        clean_location = (location or "").strip()

        if not clean_no or not clean_name or not clean_category or not clean_location:
            return {"status": "error", "message": "设备编号、名称、分类和物理位置均为必填项"}

        existing = active_db.query(Asset).filter(Asset.asset_no == clean_no).first()
        if existing:
            return {"status": "error", "message": f"资产编号 '{clean_no}' 已存在，不能重复录入"}

        asset = Asset(
            asset_no=clean_no,
            name=clean_name,
            category=clean_category,
            location=clean_location,
            health_status="HEALTHY",
            borrow_status="AVAILABLE",
            specs=specs,
        )
        active_db.add(asset)
        active_db.flush()

        has_detail = any([brand, model_name, management_ip, serial_number, cpu_info, memory_info])
        if has_detail:
            detail = AssetDetail(
                asset_id=asset.id,
                brand=brand,
                model_name=model_name,
                management_ip=management_ip,
                serial_number=serial_number,
                cpu_info=cpu_info,
                memory_info=memory_info,
            )
            active_db.add(detail)

        try:
            active_db.commit()
            active_db.refresh(asset)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"持久化录入资产失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"资产设备 '{clean_name}' (编号: {clean_no}) 成功录入机房台账！",
            "asset": {
                "id": asset.id,
                "asset_no": asset.asset_no,
                "name": asset.name,
                "category": asset.category,
                "location": asset.location,
                "health_status": asset.health_status,
                "borrow_status": asset.borrow_status,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="check_overdue_assets", description="检查并检索当前机房所有借用已超期的设备清单及逾期天数")
def check_overdue_assets(db: Optional[Session] = None) -> Dict[str, Any]:
    """检查机房全量借用逾期设备

    :param db: 数据库会话 (由系统自动注入)
    :return: 逾期设备总数、最大逾期天数及各设备清单
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法检索超期设备台账"}

    try:
        from app.services.overdue_service import get_overdue_assets_summary
        return get_overdue_assets_summary(active_db)
    except Exception as exc:
        return {"status": "error", "message": f"检索超期设备异常: {str(exc)}"}
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="draft_overdue_notice", description="针对指定超期借用的设备编号，自动生成合规的《设备资产超期归还催告通知函》公文通知")
def draft_overdue_notice(asset_no: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """针对超期设备生成正式红头催告通知单

    :param asset_no: 资产唯一编号，如 DEV-SRV-201
    :param db: 数据库会话 (由系统自动注入)
    :return: 催告公文结构化数据与 Markdown 全文
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法生成催告通知"}

    try:
        clean_no = (asset_no or "").strip().upper()
        if not clean_no:
            return {"status": "error", "message": "设备资产编号不能为空"}

        from app.services.overdue_service import generate_overdue_notice
        return generate_overdue_notice(active_db, clean_no)
    except ValueError as val_err:
        return {"status": "error", "message": str(val_err)}
    except Exception as exc:
        return {"status": "error", "message": f"生成催告单异常: {str(exc)}"}
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="send_overdue_urge_notification", description="向超期借用设备的借调责任教师（如李老师）下发正式站内催还待办通知")
def send_overdue_urge_notification(
    asset_no: str,
    urge_message: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """向超期借用责任教师下发站内待办督促通知

    :param asset_no: 资产唯一编号，如 DEV-SRV-201
    :param urge_message: 可选的定制催促消息文本
    :param db: 数据库会话 (由系统自动注入)
    :return: 下发操作结果与待办记录明细
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    if active_db is None:
        return {"status": "error", "message": "数据库会话不可用，无法下发催还通知"}

    try:
        clean_no = (asset_no or "").strip().upper()
        if not clean_no:
            return {"status": "error", "message": "设备资产编号不能为空"}

        asset = resolve_asset(clean_no, db=active_db)
        if not asset:
            return {"status": "error", "message": f"未找到匹配 '{clean_no}' 的机房设备"}
        clean_no = asset.asset_no

        # 查询当前未归还的借调记录与借调教师
        blog = (
            active_db.query(AssetBorrowLog)
            .filter(
                AssetBorrowLog.asset_id == clean_no,
                AssetBorrowLog.return_status.in_(["BORROWING", "OVERDUE"]),
                AssetBorrowLog.actual_return_time.is_(None),
            )
            .order_by(desc(AssetBorrowLog.borrow_time))
            .first()
        )

        borrower_username = "admin"
        borrower_name = "设备主管/管理员"
        overdue_days = 1

        now = datetime.now()
        if blog:
            if blog.borrower_username:
                borrower_username = blog.borrower_username
            if blog.borrower_name:
                borrower_name = blog.borrower_name
            if blog.expected_return_time:
                overdue_days = max(1, (now - blog.expected_return_time).days)
        elif asset.borrower:
            clean_b = asset.borrower.split("(")[0].split("（")[0].strip()
            user = active_db.query(User).filter(
                (User.real_name == clean_b)
                | (User.username == clean_b)
                | (User.real_name.contains(clean_b))
            ).first()
            if user:
                borrower_username = user.username
                borrower_name = user.real_name
            else:
                borrower_name = asset.borrower

        title = f"【超期催促】{clean_no} 借用已超期 {overdue_days} 天，请及时办理归还或续借手续"
        default_content = (
            f"尊敬的{borrower_name}：您借调的设备「{asset.name} ({clean_no})」已超过约定归还期限（超期约 {overdue_days} 天）。"
            f"请尽快前往实训机房办理设备归还与安全验收，或于系统办理延期审批手续。"
        )
        content = f"{default_content}\n\n督促留言：{urge_message.strip()}" if urge_message and urge_message.strip() else default_content

        # 幂等查重：若已存在未读的同设备超期催办待办，更新内容与时间戳，避免重复生成堆叠
        existing_unread = (
            active_db.query(UserNotification)
            .filter(
                UserNotification.username == borrower_username,
                UserNotification.asset_no == clean_no,
                UserNotification.notice_type == "OVERDUE_URGE",
                UserNotification.is_read == False,
            )
            .order_by(desc(UserNotification.created_at))
            .first()
        )

        if existing_unread:
            existing_unread.title = title
            existing_unread.content = content
            existing_unread.created_at = datetime.now()
            notification = existing_unread
        else:
            notification = UserNotification(
                username=borrower_username,
                title=title,
                content=content,
                notice_type="OVERDUE_URGE",
                asset_no=clean_no,
                is_read=False,
            )
            active_db.add(notification)

        try:
            active_db.commit()
            active_db.refresh(notification)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"持久化下发待办通知失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"已成功向借调责任人 {borrower_name} ({borrower_username}) 下发站内超期催还待办通知！",
            "notification": {
                "id": notification.id,
                "username": notification.username,
                "title": notification.title,
                "content": notification.content,
                "notice_type": notification.notice_type,
                "asset_no": notification.asset_no,
                "is_read": notification.is_read,
                "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S") if notification.created_at else "",
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()

