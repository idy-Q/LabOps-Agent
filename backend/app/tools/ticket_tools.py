"""机房运维工单管理工具 (Ticket Tools)"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.db.models import Ticket
from app.tools.registry import tool

VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_STATUSES = {"PENDING", "PROCESSING", "RESOLVED", "CLOSED"}


def _generate_ticket_no(db: Session) -> str:
    """自动生成工单编号，格式：TK-YYYYMMDD-XXX，保证全局唯一"""
    date_str = datetime.now().strftime("%Y%m%d")
    prefix = f"TK-{date_str}-"
    count = db.query(Ticket).filter(Ticket.ticket_no.like(f"{prefix}%")).count()
    for i in range(count + 1, count + 100):
        candidate = f"{prefix}{i:03d}"
        if not db.query(Ticket).filter(Ticket.ticket_no == candidate).first():
            return candidate
    for _ in range(10):
        rand_str = uuid.uuid4().hex[:6].upper()
        candidate = f"{prefix}{rand_str}"
        if not db.query(Ticket).filter(Ticket.ticket_no == candidate).first():
            return candidate
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


@tool(name="create_ticket", description="创建机房运维工单。当发现设备指标异常、需要现场维修或例行巡检时调用，自动分配唯一工单编号并持久化写入工单库")
def create_ticket(
    title: str,
    description: str,
    priority: str = "MEDIUM",
    device_id: Optional[str] = None,
    creator: str = "LabOps-Agent",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """创建新的运维工单记录

    :param title: 工单简明标题，如 'DEV-SRV-201 核心温度过热紧急排查'
    :param description: 工单详细处置与排查要求
    :param priority: 优先级等级 (LOW, MEDIUM, HIGH, CRITICAL)
    :param device_id: 关联设备编号，如 DEV-SRV-201
    :param creator: 提单人或系统标识，默认为 'LabOps-Agent'
    :param db: 数据库会话 (由系统自动注入)
    :return: 创建成功的工单详细信息字典
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
        return {"status": "error", "message": "数据库会话不可用，无法持久化工单"}

    try:
        norm_priority = (priority or "MEDIUM").strip().upper()
        if norm_priority not in VALID_PRIORITIES:
            norm_priority = "MEDIUM"

        clean_device = device_id.strip().upper() if device_id and device_id.strip() else None

        new_ticket = None
        for attempt in range(3):
            ticket_no = (
                _generate_ticket_no(active_db)
                if attempt == 0
                else f"TK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            )
            candidate_ticket = Ticket(
                ticket_no=ticket_no,
                title=title.strip(),
                description=description.strip(),
                priority=norm_priority,
                status="PENDING",
                device_id=clean_device,
                creator=creator.strip() if creator else "LabOps-Agent",
            )
            try:
                active_db.add(candidate_ticket)
                active_db.commit()
                active_db.refresh(candidate_ticket)
                new_ticket = candidate_ticket
                break
            except Exception as exc:
                active_db.rollback()
                if attempt == 2:
                    return {"status": "error", "message": f"持久化工单失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"工单创建成功，编号为 {new_ticket.ticket_no}",
            "ticket": {
                "id": new_ticket.id,
                "ticket_no": new_ticket.ticket_no,
                "title": new_ticket.title,
                "description": new_ticket.description,
                "priority": new_ticket.priority,
                "status": new_ticket.status,
                "device_id": new_ticket.device_id,
                "creator": new_ticket.creator,
                "created_at": new_ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if new_ticket.created_at else None,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="query_tickets", description="检索机房运维工单列表，支持按工单编号、关键词、工单状态、优先级、关联设备查询，默认按创建时间倒序返回")
def query_tickets(
    ticket_no: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 5,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """按条件查询工单记录列表

    :param ticket_no: 精确工单编号过滤，如 TK-20260901-001
    :param keyword: 模糊检索关键词（匹配工单号、标题或处置说明）
    :param status: 工单状态过滤 (PENDING, PROCESSING, RESOLVED, CLOSED)
    :param priority: 优先级过滤 (LOW, MEDIUM, HIGH, CRITICAL)
    :param device_id: 关联设备编号过滤
    :param limit: 最多返回条数，默认 5 条
    :param db: 数据库会话 (由系统自动注入)
    :return: 匹配的工单列表
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
        return {"status": "error", "message": "数据库会话不可用，无法查询工单"}

    try:
        query = active_db.query(Ticket)

        if ticket_no and ticket_no.strip():
            query = query.filter(Ticket.ticket_no == ticket_no.strip().upper())

        if keyword and keyword.strip():
            kw = keyword.strip()
            query = query.filter(
                or_(
                    Ticket.ticket_no.contains(kw),
                    Ticket.title.contains(kw),
                    Ticket.description.contains(kw),
                )
            )

        if status:
            norm_status = status.strip().upper()
            if norm_status in VALID_STATUSES:
                query = query.filter(Ticket.status == norm_status)

        if priority:
            norm_pri = priority.strip().upper()
            if norm_pri in VALID_PRIORITIES:
                query = query.filter(Ticket.priority == norm_pri)

        if device_id:
            query = query.filter(Ticket.device_id == device_id.strip().upper())

        safe_limit = max(1, min(limit, 50))
        tickets = query.order_by(desc(Ticket.created_at), desc(Ticket.id)).limit(safe_limit).all()

        return {
            "status": "success",
            "count": len(tickets),
            "tickets": [
                {
                    "id": t.id,
                    "ticket_no": t.ticket_no,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "device_id": t.device_id,
                    "creator": t.creator,
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None,
                }
                for t in tickets
            ],
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()


@tool(name="update_ticket_status", description="更新指定工单的流转状态（如由 PENDING 推进至 PROCESSING、RESOLVED 或 CLOSED 办结归档），并可追加排查处置记录")
def update_ticket_status(
    ticket_no: str,
    status: str,
    description_append: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """更新工单状态及处置详情

    :param ticket_no: 目标工单编号，如 TK-20260901-001
    :param status: 目标状态 (PENDING, PROCESSING, RESOLVED, CLOSED)
    :param description_append: 追加的处置过程或排查说明
    :param db: 数据库会话 (由系统自动注入)
    :return: 更新后的工单信息
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
        return {"status": "error", "message": "数据库会话不可用，无法更新工单"}

    try:
        clean_ticket_no = (ticket_no or "").strip().upper()
        norm_status = (status or "").strip().upper()
        if norm_status not in VALID_STATUSES:
            return {
                "status": "error",
                "message": f"无效的工单状态 '{status}'，必须为 {list(VALID_STATUSES)} 之一",
            }

        ticket = active_db.query(Ticket).filter(Ticket.ticket_no == clean_ticket_no).first()
        if not ticket:
            return {"status": "error", "message": f"未找到工单编号为 '{clean_ticket_no}' 的工单"}

        ticket.status = norm_status
        if description_append and description_append.strip():
            ticket.description = f"{ticket.description}\n[追加处置]: {description_append.strip()}"

        try:
            active_db.commit()
            active_db.refresh(ticket)
        except Exception as exc:
            active_db.rollback()
            return {"status": "error", "message": f"更新工单状态失败: {str(exc)}"}

        return {
            "status": "success",
            "message": f"工单 {clean_ticket_no} 状态已更新为 {norm_status}",
            "ticket": {
                "id": ticket.id,
                "ticket_no": ticket.ticket_no,
                "title": ticket.title,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "device_id": ticket.device_id,
                "creator": ticket.creator,
                "updated_at": ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else None,
            },
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()
