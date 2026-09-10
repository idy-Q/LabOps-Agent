"""机房资产台账与设备借还管理工具 (Asset Tools)"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.db.models import Asset
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
        query = active_db.query(Asset)

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
