"""Pydantic 数据模式校验包"""

from app.schemas.ticket import TicketBase, TicketCreate, TicketUpdate, TicketResponse
from app.schemas.asset import AssetBase, AssetCreate, AssetUpdate, AssetResponse
from app.schemas.audit import AuditLogBase, AuditLogCreate, AuditLogResponse
from app.schemas.chat import ChatHistoryBase, ChatHistoryCreate, ChatHistoryResponse

__all__ = [
    "TicketBase",
    "TicketCreate",
    "TicketUpdate",
    "TicketResponse",
    "AssetBase",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogResponse",
    "ChatHistoryBase",
    "ChatHistoryCreate",
    "ChatHistoryResponse",
]
