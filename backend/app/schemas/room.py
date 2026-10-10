"""机房空间台账数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoomBase(BaseModel):
    """机房基础字段"""

    room_code: str = Field(..., description="机房编号，如 ROOM-201", min_length=1, max_length=64)
    room_name: str = Field(..., description="机房名称，如 人工智能与高密算力实训机房", min_length=1, max_length=128)
    location: str = Field(..., description="物理位置，如 实训楼2层东侧201室", min_length=1, max_length=128)
    manager_teacher: str = Field(..., description="责任教师/安全责任人", min_length=1, max_length=64)
    power_capacity_kw: float = Field(default=0.0, description="PDU 配电额定功率(kW)", ge=0.0)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RoomCreate(RoomBase):
    """创建机房请求模型"""

    pass


class RoomUpdate(BaseModel):
    """更新机房请求模型 (字段可选)"""

    room_name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    location: Optional[str] = Field(default=None, min_length=1, max_length=128)
    manager_teacher: Optional[str] = Field(default=None, min_length=1, max_length=64)
    power_capacity_kw: Optional[float] = Field(default=None, ge=0.0)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RoomResponse(RoomBase):
    """机房响应模型"""

    id: int
    total_racks: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
