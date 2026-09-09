"""工单数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


PriorityType = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
StatusType = Literal["PENDING", "PROCESSING", "RESOLVED", "CLOSED"]


class TicketBase(BaseModel):
    """工单基础属性"""

    title: str = Field(..., description="工单标题", min_length=1, max_length=255)
    description: str = Field(..., description="工单详细描述/处置内容", min_length=1)
    priority: PriorityType = Field(default="MEDIUM", description="工单优先级")
    device_id: Optional[str] = Field(default=None, description="关联设备资产编号")
    creator: str = Field(default="管理员", description="提单人或角色", min_length=1, max_length=64)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TicketCreate(TicketBase):
    """工单创建请求模型"""

    ticket_no: Optional[str] = Field(
        default=None, description="自定义工单号，若为空则由后端自动生成"
    )
    status: Optional[StatusType] = Field(default="PENDING", description="初始状态")


class TicketUpdate(BaseModel):
    """工单更新请求模型 (所有字段均可选，禁止未定义字段)"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    priority: Optional[PriorityType] = Field(default=None)
    status: Optional[StatusType] = Field(default=None)
    device_id: Optional[str] = Field(default=None)
    creator: Optional[str] = Field(default=None, min_length=1, max_length=64)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TicketResponse(TicketBase):
    """工单响应模型"""

    id: int
    ticket_no: str
    status: StatusType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
