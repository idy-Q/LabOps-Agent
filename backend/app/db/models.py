"""SQLAlchemy 2.0 数据底座模型定义

包含四张核心业务表：
1. Ticket: 运维工单表
2. Asset: 机房资产设备表
3. AuditLog: Agent 行为与工具调用审计日志表
4. ChatHistory: 对话与推理链条持久化表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Ticket(Base):
    """运维工单表"""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_no: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="工单号，如 TK-20260901-001"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="工单标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="工单描述/排查处置内容")
    priority: Mapped[str] = mapped_column(
        String(32), default="MEDIUM", nullable=False, comment="优先级: LOW, MEDIUM, HIGH, CRITICAL"
    )
    status: Mapped[str] = mapped_column(
        String(32), default="PENDING", nullable=False, comment="状态: PENDING, PROCESSING, RESOLVED, CLOSED"
    )
    device_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True, comment="关联设备/资产编号"
    )
    creator: Mapped[str] = mapped_column(
        String(64), default="系统监控", nullable=False, comment="提单人/系统角色"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_no} - {self.title} [{self.status}]>"


class Asset(Base):
    """机房资产设备表"""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_no: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="资产编号，如 DEV-SRV-201"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="资产名称")
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="资产分类: 服务器, 网络设备, 实验教学, 配电温控"
    )
    location: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="机房位置，如 实训楼201-机柜A01"
    )
    health_status: Mapped[str] = mapped_column(
        String(32), default="HEALTHY", nullable=False, comment="健康状态: HEALTHY, WARNING, OVERHEAT, OFFLINE"
    )
    borrow_status: Mapped[str] = mapped_column(
        String(32), default="AVAILABLE", nullable=False, comment="借用状态: AVAILABLE, IN_USE, MAINTENANCE"
    )
    borrower: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="借用人/使用部门"
    )
    specs: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="硬件规格说明 (CPU, 内存, GPU, 接口等)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="录入时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<Asset {self.asset_no} - {self.name} [{self.health_status}]>"


class AuditLog(Base):
    """Agent 行为与工具调用审计日志表"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True, comment="分布式链路/会话追踪ID"
    )
    tool_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="调用的工具名称"
    )
    tool_args: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="工具调用参数 (JSON 字符串)"
    )
    tool_result: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="工具调用返回结果 (JSON 字符串)"
    )
    status: Mapped[str] = mapped_column(
        String(32), default="SUCCESS", nullable=False, comment="执行状态: SUCCESS, FAILED"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="记录时间"
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.tool_name} [{self.status}] @ {self.created_at}>"


class ChatHistory(Base):
    """会话历史记录表"""

    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="会话唯一标识"
    )
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="消息角色: user, assistant, tool, system"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="消息内容文本"
    )
    thought: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Agent 思考链推理文本"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="发送时间"
    )

    def __repr__(self) -> str:
        return f"<ChatHistory {self.session_id} - {self.role}>"
