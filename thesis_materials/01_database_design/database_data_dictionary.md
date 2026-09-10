# LabOps-Agent 数据库详细设计与数据字典（毕业论文直接复用）

> **所属章节**：毕业论文 第四章 系统设计 -> 4.3 数据库逻辑结构设计  
> **数据库引擎**：SQLite 3 / 标准 SQL 关系规范  
> **ORM 映射**：SQLAlchemy 2.0 Declarative Base

---

## 表 4-1 运维工单数据表 (tickets)

用于存储机房内所有由师生手动申报或由 AI Agent 依据监控指标自主决策生成的检修工单信息。

| 字段名称 | 字段类型 | 允许为空 | 默认值 | 约束 / 索引 | 业务含义说明 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | INTEGER | 否 | 自增 | 主键 (PK) | 工单主键自增标识符 |
| `ticket_no` | VARCHAR(64) | 否 | - | 唯一索引 (UNIQUE) | 工单全局唯一编号 (如 `TK-20260901-001`) |
| `title` | VARCHAR(255) | 否 | - | - | 工单简要标题 |
| `description` | TEXT | 否 | - | - | 故障具体现象描述与排查处置建议 |
| `priority` | VARCHAR(32) | 否 | 'MEDIUM' | - | 优先级 (`LOW` / `MEDIUM` / `HIGH` / `CRITICAL`) |
| `status` | VARCHAR(32) | 否 | 'PENDING' | - | 工单流转状态 (`PENDING`待处理 / `PROCESSING`处理中 / `RESOLVED`已解决 / `CLOSED`已办结) |
| `device_id` | VARCHAR(64) | 是 | NULL | 普通索引 | 关联的机房资产或服务器节点编号 |
| `creator` | VARCHAR(64) | 否 | '系统监控' | - | 工单创建者 (学生/机房管理员/Agent自动提单) |
| `created_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 工单生成时间戳 |
| `updated_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 工单最新状态变更时间戳 |

---

## 表 4-2 机房实验设备资产台账表 (assets)

用于记录高校计算机实验教学中心所属硬件、网络与算力服务器台账全生命周期信息。

| 字段名称 | 字段类型 | 允许为空 | 默认值 | 约束 / 索引 | 业务含义说明 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | INTEGER | 否 | 自增 | 主键 (PK) | 资产记录主键自增标识符 |
| `asset_no` | VARCHAR(64) | 否 | - | 唯一索引 (UNIQUE) | 资产统一唯一编码 (如 `DEV-SRV-201`) |
| `name` | VARCHAR(128) | 否 | - | - | 设备资产名称 (如 `高性能GPU计算节点-01`) |
| `category` | VARCHAR(64) | 否 | - | - | 设备类别 (`服务器` / `网络设备` / `实验教学` / `配电温控`) |
| `location` | VARCHAR(128) | 否 | - | - | 物理存放机房与机柜 (如 `实训楼201-机柜A01`) |
| `health_status` | VARCHAR(32) | 否 | 'HEALTHY' | - | 实时健康度 (`HEALTHY`健康 / `WARNING`预警 / `OVERHEAT`过热 / `OFFLINE`离线) |
| `borrow_status` | VARCHAR(32) | 否 | 'AVAILABLE' | - | 借还管理状态 (`AVAILABLE`在库空闲 / `IN_USE`借用中 / `MAINTENANCE`维护中) |
| `borrower` | VARCHAR(64) | 是 | NULL | - | 当前借用教职工/学生姓名或班级 |
| `specs` | TEXT | 是 | NULL | - | 硬件规格技术参数 (CPU核数, 显存, 接口等) |
| `created_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 资产台账登记时间 |
| `updated_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 资产状态更新时间 |

---

## 表 4-3 Agent 行为与工具调用审计日志表 (audit_logs)

> **答辩创新点**：此表是证明系统并非“外挂套壳 API”、具备真实可追踪 Function Calling 调用的核心依据。

| 字段名称 | 字段类型 | 允许为空 | 默认值 | 约束 / 索引 | 业务含义说明 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | INTEGER | 否 | 自增 | 主键 (PK) | 审计日志主键 |
| `trace_id` | VARCHAR(64) | 是 | NULL | 普通索引 | 分布式请求或会话追踪唯一流水号 |
| `tool_name` | VARCHAR(64) | 否 | - | - | 被调用的业务工具函数名 (如 `get_server_metrics`, `create_ticket`) |
| `tool_args` | TEXT | 是 | NULL | - | Agent 传递给工具的 JSON 格式入参快照 |
| `tool_result` | TEXT | 是 | NULL | - | 工具执行完毕后返回的原始数据 JSON 结果 |
| `status` | VARCHAR(32) | 否 | 'SUCCESS' | - | 工具执行结果状态 (`SUCCESS` / `FAILED`) |
| `created_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 工具调用的物理发生时间戳 |

---

## 表 4-4 会话历史与思考链记录表 (chat_history)

| 字段名称 | 字段类型 | 允许为空 | 默认值 | 约束 / 索引 | 业务含义说明 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `id` | INTEGER | 否 | 自增 | 主键 (PK) | 记录主键 |
| `session_id` | VARCHAR(64) | 否 | - | 普通索引 | 会话唯一会话ID |
| `role` | VARCHAR(32) | 否 | - | - | 消息发送方主体 (`user` / `assistant` / `tool` / `system`) |
| `content` | TEXT | 否 | - | - | 用户输入或模型正式输出文本正文 |
| `thought` | TEXT | 是 | NULL | - | 大模型深度思考链推理文本 (Thinking 过程快照) |
| `created_at` | DATETIME | 否 | CURRENT_TIMESTAMP | - | 消息生成时间 |
