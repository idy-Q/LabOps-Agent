-- ==============================================================================
-- 湖北商贸学院计算机科学与技术专业毕业设计
-- 项目名称：基于轻量级 ReAct 架构的高校机房智能运维与资产管理系统 (LabOps-Agent)
-- 模块说明：数据库概念与逻辑结构设计建表 SQL 脚本 (SQLite / MySQL 兼容标准 DDL)
-- 对应论文：第四章 4.2 数据库概念设计 与 4.3 数据库详细结构设计
-- 生成时间：2026-09-09
-- ==============================================================================

-- 1. 运维工单表 (Tickets)
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_no VARCHAR(64) NOT NULL UNIQUE,       -- 工单编号 (如: TK-20260901-001)
    title VARCHAR(255) NOT NULL,                 -- 工单标题
    description TEXT NOT NULL,                   -- 故障描述与排查处置建议
    priority VARCHAR(32) NOT NULL DEFAULT 'MEDIUM', -- 紧急度: LOW, MEDIUM, HIGH, CRITICAL
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',  -- 状态: PENDING(待处理), PROCESSING(处理中), RESOLVED(已解决), CLOSED(已办结)
    device_id VARCHAR(64),                       -- 关联设备编号 (如: DEV-SRV-201)
    creator VARCHAR(64) NOT NULL DEFAULT '系统监控', -- 创建人/角色 (学生/机房管理员/Agent自动)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);
CREATE INDEX IF NOT EXISTS ix_tickets_ticket_no ON tickets (ticket_no);
CREATE INDEX IF NOT EXISTS ix_tickets_device_id ON tickets (device_id);

-- 2. 机房实验设备资产表 (Assets)
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_no VARCHAR(64) NOT NULL UNIQUE,        -- 资产编号 (如: DEV-SRV-201, DEV-NET-102)
    name VARCHAR(128) NOT NULL,                  -- 资产名称 (如: 高性能GPU计算节点-01)
    category VARCHAR(64) NOT NULL,               -- 资产类别: 服务器, 网络设备, 实验教学, 配电温控
    location VARCHAR(128) NOT NULL,              -- 物理存放位置 (如: 实训楼201-机柜A01)
    health_status VARCHAR(32) NOT NULL DEFAULT 'HEALTHY', -- 健康状态: HEALTHY, WARNING, OVERHEAT, OFFLINE
    borrow_status VARCHAR(32) NOT NULL DEFAULT 'AVAILABLE', -- 借用状态: AVAILABLE, IN_USE, MAINTENANCE
    borrower VARCHAR(64),                        -- 当前借用人/使用教研室
    specs TEXT,                                  -- 硬件规格明细 (CPU, 内存, GPU, 接口)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 录入时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);
CREATE INDEX IF NOT EXISTS ix_assets_asset_no ON assets (asset_no);

-- 3. Agent 行为与工具调用审计日志表 (AuditLog) - 答辩杀手锏核心表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id VARCHAR(64),                        -- 会话追踪 Trace ID
    tool_name VARCHAR(64) NOT NULL,              -- 调用的 Tool 名称 (如: get_server_metrics, create_ticket)
    tool_args TEXT,                              -- 工具入参 JSON 字符串
    tool_result TEXT,                            -- 工具返回结果 JSON 字符串
    status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS', -- 工具执行状态: SUCCESS, FAILED
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP -- 调用时间戳
);
CREATE INDEX IF NOT EXISTS ix_audit_logs_trace_id ON audit_logs (trace_id);

-- 4. 会话历史记录与思考链持久化表 (ChatHistory)
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64) NOT NULL,             -- 会话 Session ID
    role VARCHAR(32) NOT NULL,                   -- 角色: user, assistant, tool, system
    content TEXT NOT NULL,                       -- 消息正文文本
    thought TEXT,                                -- Agent 思考链推理文本 (Thinking 过程)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP -- 发送时间
);
CREATE INDEX IF NOT EXISTS ix_chat_history_session_id ON chat_history (session_id);
