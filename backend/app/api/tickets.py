"""运维工单 RESTful API 路由"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import Ticket
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    PriorityType,
    StatusType,
)

router = APIRouter()


def generate_ticket_no() -> str:
    """自动生成工单编号，格式：TK-YYYYMMDD-XXXX"""
    date_str = datetime.now().strftime("%Y%m%d")
    rand_str = uuid.uuid4().hex[:4].upper()
    return f"TK-{date_str}-{rand_str}"


@router.get(
    "/",
    response_model=List[TicketResponse],
    summary="查询工单列表",
    description="支持按状态、优先级、关联设备过滤，按创建时间倒序排列。",
)
def list_tickets(
    status: Optional[StatusType] = Query(default=None, description="按状态过滤"),
    priority: Optional[PriorityType] = Query(default=None, description="按优先级过滤"),
    device_id: Optional[str] = Query(default=None, description="按关联设备过滤"),
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

    tickets = query.order_by(desc(Ticket.created_at)).offset(skip).limit(limit).all()
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
    ticket_no = ticket_in.ticket_no or generate_ticket_no()

    # 检查工单号是否唯一
    existing = db.query(Ticket).filter(Ticket.ticket_no == ticket_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"工单编号 '{ticket_no}' 已存在，请勿重复创建",
        )

    ticket = Ticket(
        ticket_no=ticket_no,
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        status=ticket_in.status or "PENDING",
        device_id=ticket_in.device_id,
        creator=ticket_in.creator,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="获取单个工单详情",
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
    description="更新工单的状态、优先级、描述或关联设备等字段。",
)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {ticket_id} 的工单不存在",
        )

    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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
    db.delete(ticket)
    db.commit()
    return None
