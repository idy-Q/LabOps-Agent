"""工业机柜与物理U位台账数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RackBase(BaseModel):
    """机柜基础字段"""

    rack_id: str = Field(..., description="机柜唯一编号，如 机柜A01, 机柜A03", min_length=1, max_length=64)
    rack_name: str = Field(..., description="机柜显示名称，如 A03 智算高通量扩展柜", min_length=1, max_length=128)
    room_code: str = Field(..., description="关联机房编号，如 ROOM-201", min_length=1, max_length=64)
    total_u: int = Field(default=42, description="总可用槽位空间(U)，默认 42", ge=1, le=100)
    power_rating_w: int = Field(default=4500, description="额定功耗(W)，默认 4500", ge=0)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RackCreate(RackBase):
    """创建机柜请求模型"""

    pass


class RackUpdate(BaseModel):
    """更新机柜请求模型 (字段可选)"""

    rack_name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    room_code: Optional[str] = Field(default=None, min_length=1, max_length=64)
    total_u: Optional[int] = Field(default=None, ge=1, le=100)
    power_rating_w: Optional[int] = Field(default=None, ge=0)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RackResponse(RackBase):
    """机柜响应模型"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
