"""SQLAlchemy 2.0 数据底座模型定义

包含十二张核心业务、运维流转与知识资产表：
1. Ticket: 运维工单表
2. Asset: 机房资产设备表
3. AuditLog: Agent 行为与工具调用审计日志表
4. ChatHistory: 对话与推理链条持久化表
5. User: 系统用户与角色权限表
6. ServerRoom: 机房区域与机柜台账表
7. ServerRack: 机房工业级标准机柜台账表
8. AssetBorrowLog: 设备借调流转历史记录表
9. TicketWorkflow: 工单流转处置记录表
10. KnowledgeDocument: 知识库规程源文档表
11. KnowledgeChunk: 知识切块索引台账表
12. UserNotification: 用户站内待办与超期督促通知表
"""

import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

PASSWORD_SALT = "labops_secure_salt_2026"


def hash_password(password: str, salt: str = PASSWORD_SALT) -> str:
    """使用 SHA-256 加盐生成 64 位十六进制密码哈希"""
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str, salt: str = PASSWORD_SALT) -> bool:
    """验证明文密码与加盐哈希是否匹配"""
    return hash_password(password, salt) == hashed



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

    detail: Mapped[Optional["AssetDetail"]] = relationship(
        "AssetDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def custom_temperature(self) -> Optional[float]:
        """获取设备设定的核心遥测温度 (优先从 AssetDetail 读取，亦兼容 extra_params)"""
        if self.detail and self.detail.custom_temperature is not None:
            return round(float(self.detail.custom_temperature), 1)
        if self.detail and self.detail.extra_params:
            try:
                import json
                ep = json.loads(self.detail.extra_params)
                if "custom_temperature" in ep and ep["custom_temperature"] is not None:
                    return round(float(ep["custom_temperature"]), 1)
                if "temperature" in ep and ep["temperature"] is not None:
                    return round(float(ep["temperature"]), 1)
            except Exception:
                pass
        return None

    @property
    def telemetry_temperature(self) -> float:
        """设备实时动环遥测温度 (若设置自定义温度则优先注入，否则依健康状态派生基准探针温度)"""
        ct = self.custom_temperature
        if ct is not None:
            if self.health_status == "OFFLINE":
                return 22.0
            return ct
        if self.health_status == "OVERHEAT":
            return 43.5
        elif self.health_status == "WARNING":
            return 38.0
        elif self.health_status == "OFFLINE":
            return 22.0
        return 31.5

    @property
    def temperature(self) -> float:
        """设备实时动环遥测温度 (telemetry_temperature 别名)"""
        return self.telemetry_temperature

    def __repr__(self) -> str:
        return f"<Asset {self.asset_no} - {self.name} [{self.health_status}]>"


class AssetDetail(Base):
    """设备硬件物理规格与详细参数表 (1对1关联 assets 表)"""

    __tablename__ = "asset_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True, comment="关联资产主表ID"
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="出厂硬件序列号 (SN)"
    )
    brand: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="厂商品牌"
    )
    model_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="设备具体型号"
    )
    os_firmware: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="操作系统或固件版本"
    )
    mac_address: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="物理MAC地址"
    )
    management_ip: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="带外/管理IP地址"
    )

    # 核心计算与物理参数
    cpu_info: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="CPU处理器规格及核心数"
    )
    memory_info: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="内存容量及类型"
    )
    storage_info: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="磁盘存储与RAID阵列"
    )
    gpu_info: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="GPU/加速卡配置"
    )
    network_interfaces: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="网络端口与传输速率"
    )
    power_supply: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="供电与功耗规格"
    )

    # 维保与商务信息
    purchase_date: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="采购投产日期"
    )
    warranty_period: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="维保期限与到期日"
    )
    supplier: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="供应商与技术支持电话"
    )

    # 扩展自定义参数 (JSON 字符串，支持各类专用设备定制参数)
    extra_params: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="各类设备定制参数(JSON格式)"
    )

    # 动环探针遥测注入设定参数
    custom_temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="用户自定义设定核心运行温度(°C)，用于动环探针遥测注入"
    )

    @property
    def temperature(self) -> Optional[float]:
        """自定义设定核心运行温度(°C)，同 custom_temperature 别名"""
        return self.custom_temperature

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="录入时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    asset: Mapped["Asset"] = relationship("Asset", back_populates="detail")

    def __repr__(self) -> str:
        return f"<AssetDetail for Asset ID {self.asset_id} (SN: {self.serial_number})>"


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


class User(Base):
    """系统用户与角色权限表"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="登录工号/学号"
    )
    password_hash: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="加盐密码哈希 (SHA-256)"
    )
    real_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="真实姓名，如 王主管/李老师"
    )
    role: Mapped[str] = mapped_column(
        String(32), default="TEACHER", nullable=False, comment="角色枚举: ADMIN, TEACHER, STUDENT"
    )
    department: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="教研室/班级/部门"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="联系电话"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="注册创建时间"
    )

    def __repr__(self) -> str:
        return f"<User {self.username} - {self.real_name} [{self.role}]>"


class ServerRoom(Base):
    """机房区域与机柜台账表"""

    __tablename__ = "server_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="机房编号，如 ROOM-201"
    )
    room_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="机房名称，如 人工智能与大数据实训机房"
    )
    total_racks: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="机柜总数"
    )
    power_capacity_kw: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, comment="PDU 配电额定功率(kW)"
    )
    manager_teacher: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="责任教师/安全责任人"
    )
    location: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="位置描述，如 实训楼2层东侧201室"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="录入时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<ServerRoom {self.room_code} - {self.room_name}>"


class ServerRack(Base):
    """机房工业级标准机柜台账表"""

    __tablename__ = "server_racks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rack_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="机柜唯一编号，如 机柜A01, 机柜A03"
    )
    rack_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="机柜显示名称，如 A03 智算高通量扩展柜"
    )
    room_code: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="关联机房编号，如 ROOM-201, ROOM-101"
    )
    total_u: Mapped[int] = mapped_column(
        Integer, default=42, nullable=False, comment="总可用槽位空间(U)，默认 42"
    )
    power_rating_w: Mapped[int] = mapped_column(
        Integer, default=4500, nullable=False, comment="额定功耗(W)，默认 4500"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="立柜投产时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<ServerRack {self.rack_id} - {self.rack_name} @ {self.room_code}>"


class AssetBorrowLog(Base):
    """设备借调流转历史记录表"""

    __tablename__ = "asset_borrow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_no: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="借还记录流水编号，如 BORROW-20260901-001"
    )
    asset_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="设备编号，如 DEV-SRV-201"
    )
    borrower_username: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="借调人用户名"
    )
    borrower_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="借调人姓名"
    )
    purpose: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="借用用途"
    )
    borrow_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="借出时间"
    )
    expected_return_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="约定归还时间"
    )
    actual_return_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际归还时间"
    )
    return_status: Mapped[str] = mapped_column(
        String(32), default="BORROWING", nullable=False, comment="归还状态: BORROWING, RETURNED, OVERDUE"
    )
    approver: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="验收人"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<AssetBorrowLog {self.log_no} - {self.asset_id} [{self.return_status}]>"


class TicketWorkflow(Base):
    """工单流转处置记录表"""

    __tablename__ = "ticket_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="工单号，如 TK-20260901-001"
    )
    previous_status: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="前置状态: PENDING, PROCESSING, RESOLVED"
    )
    next_status: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="后置状态: PROCESSING, RESOLVED, CLOSED"
    )
    operator: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="处置人"
    )
    comment: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="处置说明"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="操作时间"
    )

    def __repr__(self) -> str:
        return f"<TicketWorkflow {self.ticket_id}: {self.previous_status}->{self.next_status} by {self.operator}>"


class KnowledgeDocument(Base):
    """知识库规程源文档表"""

    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="文档ID，如 DOC-RAG-001"
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="文档标题，如《用电安全与高功耗设备接入管理规范》"
    )
    version: Mapped[str] = mapped_column(
        String(32), default="2026版", nullable=False, comment="版本号"
    )
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="文件分类: 应急条例, 维保规程, 用电规范"
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="文件SHA256哈希"
    )
    char_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="总字符数"
    )
    effective_date: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="生效日期"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="录入时间"
    )

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.doc_id} - {self.title} [{self.version}]>"


class KnowledgeChunk(Base):
    """知识切块索引台账表"""

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False, comment="切块ID，如 CHK-001-01"
    )
    document_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("knowledge_documents.doc_id", ondelete="CASCADE"), index=True, nullable=False, comment="所属文档ID (外键)"
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="分块序号"
    )
    section_title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="章节层级标题"
    )
    chunk_content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="切块文本"
    )
    token_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Token预估数"
    )
    chroma_id: Mapped[Optional[str]] = mapped_column(
        String(64), index=True, nullable=True, comment="Chroma向量索引ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="切块时间"
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument", back_populates="chunks"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeChunk {self.chunk_id} [doc={self.document_id}, idx={self.chunk_index}]>"


class UserNotification(Base):
    """用户站内待办与超期督促通知表"""

    __tablename__ = "user_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="接收通知的用户名，如 teacher_li"
    )
    title: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="通知标题"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="通知详细内容/公文摘要"
    )
    notice_type: Mapped[str] = mapped_column(
        String(32), default="OVERDUE_URGE", nullable=False, comment="类型: OVERDUE_URGE/SYSTEM"
    )
    asset_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="关联资产编号，如 DEV-SRV-201"
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否已读"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<UserNotification id={self.id} user={self.username} title={self.title} read={self.is_read}>"


