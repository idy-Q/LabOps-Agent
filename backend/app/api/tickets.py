"""运维工单 RESTful API 路由"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.db.models import Ticket, TicketWorkflow, AuditLog
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    PriorityType,
    StatusType,
)

router = APIRouter()


def generate_ticket_no(db: Session) -> str:
    """自动生成工单编号，格式：TK-YYYYMMDD-XXXXXX，保证全局唯一"""
    date_str = datetime.now().strftime("%Y%m%d")
    for _ in range(10):
        rand_str = uuid.uuid4().hex[:6].upper()
        candidate = f"TK-{date_str}-{rand_str}"
        if not db.query(Ticket).filter(Ticket.ticket_no == candidate).first():
            return candidate
    return f"TK-{date_str}-{uuid.uuid4().hex[:8].upper()}"


@router.get(
    "/",
    response_model=List[TicketResponse],
    summary="查询工单列表",
    description="支持按状态、优先级、关联设备、工单号及关键词过滤，按创建时间倒序排列。",
)
def list_tickets(
    status: Optional[StatusType] = Query(default=None, description="按状态过滤"),
    priority: Optional[PriorityType] = Query(default=None, description="按优先级过滤"),
    device_id: Optional[str] = Query(default=None, description="按关联设备过滤"),
    ticket_no: Optional[str] = Query(default=None, description="按工单号精确过滤"),
    keyword: Optional[str] = Query(default=None, description="按工单号/标题/描述关键词模糊搜索"),
    skip: int = Query(default=0, ge=0, description="分页起始偏移量"),
    limit: int = Query(default=50, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if device_id:
        query = query.filter(Ticket.device_id == device_id)
    if ticket_no:
        query = query.filter(Ticket.ticket_no == ticket_no)
    if keyword:
        query = query.filter(
            or_(
                Ticket.ticket_no.contains(keyword),
                Ticket.title.contains(keyword),
                Ticket.description.contains(keyword),
            )
        )

    tickets = (
        query.order_by(desc(Ticket.created_at), desc(Ticket.id))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tickets


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新工单",
    description="创建一条新工单。若未显式提供工单号，将自动生成。",
)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
):
    if ticket_in.ticket_no:
        ticket_no = ticket_in.ticket_no
        existing = db.query(Ticket).filter(Ticket.ticket_no == ticket_no).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工单编号 '{ticket_no}' 已存在，请勿重复创建",
            )
    else:
        ticket_no = generate_ticket_no(db)

    ticket = Ticket(
        ticket_no=ticket_no,
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        status=ticket_in.status or "PENDING",
        device_id=ticket_in.device_id,
        creator=ticket_in.creator,
    )
    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"工单编号 '{ticket_no}' 已存在或数据冲突",
        )
    except Exception:
        db.rollback()
        raise
    return ticket


@router.get(
    "/{ticket_no_or_id}/timeline",
    summary="获取工单流转全景脉络时间轴",
    description="支持工单 ID 或工单编号查询，按时序聚合提单创建、流转演化、Agent工具自动化审计及处理耗时。",
)
def get_ticket_timeline(
    ticket_no_or_id: str,
    db: Session = Depends(get_db),
):
    clean_target = ticket_no_or_id.strip()
    ticket = None
    if clean_target.isdigit():
        ticket = db.query(Ticket).filter(Ticket.id == int(clean_target)).first()
    if not ticket:
        ticket = db.query(Ticket).filter(Ticket.ticket_no == clean_target).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未检索到编号或ID为 '{ticket_no_or_id}' 的工单",
        )

    nodes = []
    workflows = (
        db.query(TicketWorkflow)
        .filter(TicketWorkflow.ticket_id == ticket.ticket_no)
        .order_by(TicketWorkflow.created_at.asc(), TicketWorkflow.id.asc())
        .all()
    )

    # 3. 关联 Agent 工具调用审计日志 (audit_logs 表)
    audit_logs = (
        db.query(AuditLog)
        .filter(
            or_(
                AuditLog.tool_args.contains(ticket.ticket_no),
                AuditLog.tool_result.contains(ticket.ticket_no),
            )
        )
        .order_by(AuditLog.created_at.asc())
        .all()
    )

    # 严格校准起始基准时间为所有关联事件（工单创建、历史工作流、审计日志）的最早时间点
    candidate_times = [ticket.created_at or datetime.now()]
    for wf in workflows:
        if wf.created_at:
            candidate_times.append(wf.created_at)
    for al in audit_logs:
        if al.created_at:
            candidate_times.append(al.created_at)
    base_time = min(candidate_times)

    # 1. 提单创建节点 (创生起始节点)
    nodes.append({
        "id": f"node-created-{ticket.id}",
        "node_type": "CREATED",
        "title": f"工单创建 - {ticket.title}",
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "raw_time": base_time,
        "operator": ticket.creator or "系统监控",
        "previous_status": None,
        "next_status": "PENDING",
        "comment": ticket.description,
        "duration_from_start": "+0分钟",
        "metadata": {
            "priority": ticket.priority,
            "device_id": ticket.device_id,
        },
    })
    for wf in workflows:
        wf_time = wf.created_at or base_time
        diff_sec = max(0.0, (wf_time - base_time).total_seconds())
        nodes.append({
            "id": f"node-wf-{wf.id}",
            "node_type": wf.next_status,
            "title": f"工单状态变迁 ({wf.previous_status} -> {wf.next_status})",
            "timestamp": wf_time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_time": wf_time,
            "operator": wf.operator,
            "previous_status": wf.previous_status,
            "next_status": wf.next_status,
            "comment": wf.comment or f"状态推进至 {wf.next_status}",
            "duration_from_start": format_duration(diff_sec),
            "metadata": {
                "workflow_id": wf.id,
            },
        })

    # 3. 追加 Agent 自动化审计日志节点
    for al in audit_logs:
        al_time = al.created_at or base_time
        diff_sec = max(0.0, (al_time - base_time).total_seconds())
        nodes.append({
            "id": f"node-audit-{al.id}",
            "node_type": "AUTOMATION",
            "title": f"Agent 自动化调用: {al.tool_name}",
            "timestamp": al_time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_time": al_time,
            "operator": "LabOps-Agent",
            "previous_status": None,
            "next_status": None,
            "comment": f"调用工具 [{al.tool_name}]，状态: {al.status}",
            "duration_from_start": format_duration(diff_sec),
            "metadata": {
                "tool_name": al.tool_name,
                "status": al.status,
                "trace_id": al.trace_id,
            },
        })

    # 按时间升序排序，同一秒保证 CREATED 最先，然后 AUTOMATION，最后 WORKFLOW
    def sort_key(item):
        type_rank = {"CREATED": -1, "AUTOMATION": 1}
        return (item["raw_time"], type_rank.get(item["node_type"], 2))

    nodes.sort(key=sort_key)

    latest_time = max([ticket.updated_at or base_time] + [n["raw_time"] for n in nodes])
    for n in nodes:
        n.pop("raw_time", None)

    total_sec = max(0.0, (latest_time - base_time).total_seconds())
    total_duration_str = format_duration(total_sec).lstrip("+")

    return {
        "ticket": {
            "id": ticket.id,
            "ticket_no": ticket.ticket_no,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "device_id": ticket.device_id,
            "creator": ticket.creator,
            "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else None,
            "updated_at": ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else None,
        },
        "timeline": nodes,
        "summary": {
            "total_nodes": len(nodes),
            "current_status": ticket.status,
            "is_closed": ticket.status in ("CLOSED", "RESOLVED"),
            "total_duration": total_duration_str,
        },
    }


def format_duration(delta_seconds: float) -> str:
    """格式化相对提单时间的耗时文本"""
    if delta_seconds <= 0:
        return "+0分钟"
    minutes = int(delta_seconds // 60)
    if minutes < 1:
        return "+0分钟"
    if minutes < 60:
        return f"+{minutes}分钟"
    hours = minutes // 60
    rem_minutes = minutes % 60
    if hours < 24:
        return f"+{hours}小时{rem_minutes}分" if rem_minutes > 0 else f"+{hours}小时"
    days = hours // 24
    rem_hours = hours % 24
    return f"+{days}天{rem_hours}小时" if rem_hours > 0 else f"+{days}天"


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="获取单个工单详情",
    description="通过工单唯一 ID 获取工单的详细信息。",
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {ticket_id} 的工单不存在",
        )
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="更新工单信息",
    description="更新工单的状态、优先级、描述或关联设备等字段，状态变迁时自动写入流转审计记录。",
)
@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    include_in_schema=False,
)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    operator: Optional[str] = Query(default=None, description="流转处置操作人（可选查询参数）"),
    comment: Optional[str] = Query(default=None, description="流转处置说明（可选查询参数）"),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {ticket_id} 的工单不存在",
        )

    update_data = ticket_update.model_dump(exclude_unset=True)
    body_operator = update_data.pop("operator", None)
    body_comment = update_data.pop("comment", None)

    # 优先取请求体中的 operator/comment，未提供时取 Query 参数，最后使用缺省值
    effective_operator = (body_operator or operator or "").strip() or "系统管理员"
    effective_comment = (body_comment or comment or "").strip()

    # 检测工单状态变迁并自动记录 TicketWorkflow
    new_status = update_data.get("status")
    if new_status and new_status != ticket.status:
        old_status = ticket.status
        cm = effective_comment or f"工单状态从 {old_status} 推进至 {new_status}"
        wf = TicketWorkflow(
            ticket_id=ticket.ticket_no,
            previous_status=old_status,
            next_status=new_status,
            operator=effective_operator,
            comment=cm,
        )
        db.add(wf)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    try:
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="删除工单",
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {ticket_id} 的工单不存在",
        )
    try:
        db.query(TicketWorkflow).filter(TicketWorkflow.ticket_id == ticket.ticket_no).delete()
        db.delete(ticket)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return Response(status_code=status.HTTP_204_NO_CONTENT)
