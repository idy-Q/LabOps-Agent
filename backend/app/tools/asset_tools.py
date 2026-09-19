"""机房资产台账与设备借还管理工具 (Asset Tools)"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_

from app.db.models import Asset, AssetDetail
from app.tools.registry import tool

VALID_HEALTH_STATUSES = {"HEALTHY", "WARNING", "OVERHEAT", "OFFLINE"}
VALID_BORROW_STATUSES = {"AVAILABLE", "IN_USE", "MAINTENANCE"}


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

        asset = active_db.query(Asset).filter(Asset.asset_no == clean_no).first()
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到设备编号为 '{clean_no}' 的资产"}

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

        asset.borrow_status = "IN_USE"
        asset.borrower = clean_borrower

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

        asset = active_db.query(Asset).filter(Asset.asset_no == clean_no).first()
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到设备编号为 '{clean_no}' 的资产"}

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

        asset = active_db.query(Asset).filter(Asset.asset_no == clean_no).first()
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到设备编号为 '{clean_no}' 的资产"}

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

        asset = (
            active_db.query(Asset)
            .options(joinedload(Asset.detail))
            .filter(Asset.asset_no == clean_no)
            .first()
        )
        if not asset:
            return {"status": "error", "message": f"未在台账中检索到设备编号为 '{clean_no}' 的资产"}

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
