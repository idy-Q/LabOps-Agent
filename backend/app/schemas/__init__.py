"""Pydantic 数据模式校验包"""

from app.schemas.ticket import TicketBase, TicketCreate, TicketUpdate, TicketResponse
from app.schemas.asset import AssetBase, AssetCreate, AssetUpdate, AssetResponse
from app.schemas.audit import AuditLogBase, AuditLogCreate, AuditLogResponse
from app.schemas.chat import ChatHistoryBase, ChatHistoryCreate, ChatHistoryResponse, ChatStreamRequest
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, DemoUserResponse
from app.schemas.room import RoomBase, RoomCreate, RoomUpdate, RoomResponse
from app.schemas.rack import RackBase, RackCreate, RackUpdate, RackResponse

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
    "ChatStreamRequest",
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "DemoUserResponse",
    "RoomBase",
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RackBase",
    "RackCreate",
    "RackUpdate",
    "RackResponse",
]

