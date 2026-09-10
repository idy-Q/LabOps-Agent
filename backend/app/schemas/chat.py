"""会话历史与推理链条持久化数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

RoleType = Literal["user", "assistant", "tool", "system"]


class ChatHistoryBase(BaseModel):
    """会话历史基础属性"""

    session_id: str = Field(..., description="会话唯一标识", min_length=1, max_length=64)
    role: RoleType = Field(..., description="消息角色: user, assistant, tool, system")
    content: str = Field(default="", description="消息内容文本")
    thought: Optional[str] = Field(default=None, description="Agent 思考链推理文本")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChatStreamRequest(BaseModel):
    """流式对话请求模型"""

    prompt: str = Field(..., description="用户提问或指令内容", min_length=1)
    session_id: Optional[str] = Field(default=None, description="可选会话ID，若不传则系统自动生成")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChatHistoryCreate(ChatHistoryBase):
    """会话历史创建模型"""
    pass


class ChatHistoryResponse(ChatHistoryBase):
    """会话历史响应模型"""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
