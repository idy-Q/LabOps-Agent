"""Agent 行为与工具调用审计日志数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    """审计日志基础属性"""

    trace_id: Optional[str] = Field(default=None, description="分布式链路/会话追踪ID", max_length=64)
    tool_name: str = Field(..., description="调用的工具名称", min_length=1, max_length=64)
    tool_args: Optional[str] = Field(default=None, description="工具调用参数 (JSON 字符串)")
    tool_result: Optional[str] = Field(default=None, description="工具调用返回结果 (JSON 字符串)")
    status: str = Field(default="SUCCESS", description="执行状态: SUCCESS, FAILED", max_length=32)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AuditLogCreate(AuditLogBase):
    """审计日志创建请求模型"""
    pass


class AuditLogResponse(AuditLogBase):
    """审计日志详情响应模型"""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
