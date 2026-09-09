"""会话历史与推理链条持久化数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

RoleType = Literal["user", "assistant", "tool", "system"]


class ChatHistoryBase(BaseModel):
    """会话历史基础属性"""

    session_id: str = Field(..., description="会话唯一标识", min_length=1, max_length=64)
    role: RoleType = Field(..., description="消息角色: user, assistant, tool, system")
    content: str = Field(..., description="消息内容文本", min_length=1)
    thought: Optional[str] = Field(default=None, description="Agent 思考链推理文本")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChatHistoryCreate(ChatHistoryBase):
    """会话历史创建模型"""
    pass


class ChatHistoryResponse(ChatHistoryBase):
    """会话历史响应模型"""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
