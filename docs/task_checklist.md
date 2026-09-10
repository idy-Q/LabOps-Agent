# LabOps-Agent 全周期开发任务清单与进度看板

> **跨会话续接说明**：  
> 本文件位于工作区 `docs/task_checklist.md`，是跨对话框记忆与状态同步的**唯一事实来源（Single Source of Truth）**。  
> 每次新开对话时，只需对 AI 说：`“请阅读 docs/task_checklist.md 并继续下一步”`，AI 即可零偏差秒级恢复上下文。

---

## 一、 项目总览与里程碑进度

* **系统名称**：基于轻量级 ReAct 架构的高校机房智能运维与资产管理系统（LabOps-Agent）
* **开发策略**：严格 24 小时极速交付，KISS 极简可维护，严禁过度设计，阶段封板
* **当前总进度**：`[■■■■□] 阶段 3 已完成 (3/5 阶段完成)`

| 阶段 | 阶段目标 | 预估耗时 | 状态 | 完成时间 |
| :--- | :--- | :---: | :---: | :---: |
| **阶段 1** | **骨架搭建与数据底座（FastAPI + SQLite + CRUD）** | 4h | **已完成 (Completed)** | 2026-09-09 |
| **阶段 2** | **手写 ReAct 调度引擎与垂直业务工具集** | 7h | **已完成 (Completed)** | 2026-09-09 |
| **阶段 3** | **机房规章 RAG 知识库与检索集成** | 3h | **已完成 (Completed)** | 2026-09-10 |
| **阶段 4** | **Vue 3 前端左右分栏与细粒度 SSE 联动** | 6h | 待开始 (Pending) | - |
| **阶段 5** | **Docker 容器化、封板验收与答辩材料归档** | 4h | 待开始 (Pending) | - |

---

## 二、 阶段 1：骨架搭建与数据底座（已封板）

- [x] **Task 1.1 后端工程初始化与依赖配置**
  - [x] 创建 `backend/` 目录骨架与 `.venv` 虚拟环境
  - [x] 编写 [backend/requirements.txt](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/requirements.txt)（FastAPI, Uvicorn, SQLAlchemy, Pydantic 等）
  - [x] 编写 [backend/app/config.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/config.py) 全局环境与路径配置
  - [x] 编写 [backend/app/main.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/main.py) FastAPI 基础实例与 CORS 跨域

- [x] **Task 1.2 关系型数据库引擎与数据模型 (SQLite + SQLAlchemy 2.0)**
  - [x] 编写 [backend/app/db/session.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/db/session.py) 数据库连接与会话依赖
  - [x] 编写 [backend/app/db/models.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/db/models.py)：
    - `Ticket`：工单表（工单号、标题、优先级、状态、关联设备、处置内容等）
    - `Asset`：设备资产表（资产编号、名称、机房位置、健康状态、借还状态）
    - `AuditLog`：Agent 工具调用审计日志表
    - `ChatHistory`：会话历史记录表
  - [x] 编写 [backend/app/db/init_db.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/db/init_db.py) 自动建表与 5 条典型测试种子数据填充

- [x] **Task 1.3 数据模式定义 (Pydantic Schemas)**
  - [x] 编写 [backend/app/schemas/ticket.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/schemas/ticket.py)
  - [x] 编写 [backend/app/schemas/asset.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/schemas/asset.py)
  - [x] 编写 [backend/app/schemas/audit.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/schemas/audit.py) 与 [backend/app/schemas/chat.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/schemas/chat.py)

- [x] **Task 1.4 RESTful API 路由实现**
  - [x] 编写 [backend/app/api/tickets.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/api/tickets.py)（列表、新增、详情、状态更新）
  - [x] 编写 [backend/app/api/assets.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/api/assets.py)（列表、新增、设备借还/健康状态变更）
  - [x] 路由挂载至 `main.py` 并提供 `GET /api/health`

- [x] **Task 1.5 服务启动与接口验收**
  - [x] 自动初始化生成 `backend/app/data/labops.db`
  - [x] 测试运行 FastAPI 服务，验证 Swagger UI (`/docs`) 与 REST 接口 CRUD 正常
  - [x] 阶段 1 封板并更新任务清单

- [x] **Task 1.6 阶段一毕设素材沉淀与归档 (thesis_materials/)**
  - [x] 创建 `thesis_materials/` 目录树（01~05 子目录结构）
  - [x] 导出 `01_database_design/schema.sql` 建表脚本与 `database_data_dictionary.md` 逻辑设计数据字典
  - [x] 归档 `03_test_cases/phase1_api_test_report.md`（15 个接口自动化测试用例报告，论文直接复用）
  - [x] 编写 `02_screenshots/README.md` 阶段一必备截图指引

---

## 三、 阶段 2：手写 ReAct 调度引擎与垂直业务工具集（已封板）

- [x] **Task 2.1 依赖安装与配置扩展**
  - [x] 在 `backend/requirements.txt` 中增加 `openai>=1.14.0` 并在虚拟环境安装成功
  - [x] 在 `backend/app/config.py` 中补充 `REACT_MAX_STEPS = 6` 与 `AGENT_MOCK_MODE = "auto"`（留空私有Key，开箱即用）

- [x] **Task 2.2 工具注册中心与审计拦截机制 (Tools Registry)**
  - [x] 编写 [backend/app/tools/registry.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/tools/registry.py)
  - [x] 实现 `@tool` 注册装饰器与自动生成符合 OpenAI Function Calling 标准的 JSON Schema
  - [x] 实现统一派发执行入口 `execute_tool`，自动将入参/出参以 JSON 持久化写入 `AuditLog` 审计表

- [x] **Task 2.3 垂直业务工具集实现**
  - [x] 编写 [backend/app/tools/metric_tools.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/tools/metric_tools.py)：`get_server_metrics`（温度 >40℃ 自动触发 OVERHEAT 报警）
  - [x] 编写 [backend/app/tools/ticket_tools.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/tools/ticket_tools.py)：`create_ticket`、`query_tickets`、`update_ticket_status`（操作 SQLite `tickets` 表并自动生成 TK 编号）
  - [x] 编写 [backend/app/tools/asset_tools.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/tools/asset_tools.py)：`query_assets`、`borrow_asset`（含防重复借出校验）、`return_asset`、`update_asset_health`

- [x] **Task 2.4 手写 ReAct 调度引擎实现 (Agent Core)**
  - [x] 编写 [backend/app/agent/prompts.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/agent/prompts.py)：机房智能管家规范（感知 -> 研判 -> 闭环 -> 汇报）
  - [x] 编写 [backend/app/agent/react_engine.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/agent/react_engine.py)：
    - 原生 Python while 循环，约 150 行无黑盒框架，带 `max_steps` 防死锁截断保护
    - 双模驱动：支持真实 OpenAI 兼容端点，无 Key 或断网时自动启用确定性本地 Mock 调度大脑
    - 支持同步 `run()` 与流式事件生成器 `stream_run()`（输出 `think`、`tool_start`、`tool_end`、`content`、`done`）
    - 自动将会话轮次与思考记录写入 `ChatHistory` 表

- [x] **Task 2.5 单元测试与端到端闭环验证**
  - [x] 编写 [backend/tests/test_tools.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/tests/test_tools.py)（20 项测试用例，覆盖三大工具集、边界防御、模型幻觉参数过滤、智能参数别名自适应、恶劣循环引用审计安全与并发重试）
  - [x] 编写 [backend/tests/test_react_engine.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/tests/test_react_engine.py)（17 项测试用例，覆盖 ReAct 状态机循环、超温提单联动、借还驱动、独立无DB运行、API容灾降级、业务冲突反馈、SSE 契约、max_steps 截断、非存在设备诚实防御、工单流转、健康更新与主动提单）
  - [x] 运行全局自动化回归测试，全仓 52 项测试 100% 通过（耗时 2.40s）

- [x] **Task 2.6 阶段二毕设素材沉淀与看板封板**
  - [x] 编写 [thesis_materials/04_core_algorithms/react_engine_algorithm.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/thesis_materials/04_core_algorithms/react_engine_algorithm.md)（状态机形式化定义、Algorithm 1 伪代码、Mermaid 时序图）
  - [x] 编写 [thesis_materials/03_test_cases/phase2_agent_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/thesis_materials/03_test_cases/phase2_agent_test_report.md)（阶段二完整测试报告，论文直接复用）
  - [x] 更新任务看板，阶段 2 代码全面封板

---

## 四、 后续阶段任务规划概要

### 阶段 3：机房规章 RAG 知识库与检索集成 (已完成)
- [x] 更新 `requirements.txt` 引入 ChromaDB 并安装
- [x] 编写 `data/regulations/*.md` 高质量规章语料（用电/超温/巡检）
- [x] 实现 `chunking.py` 结构化 Markdown 切块器
- [x] 实现 `vector_store.py` 双模高可用向量库（ChromaDB/内存余弦降级）
- [x] 实现 `@tool` `query_regulations` 并暴露注册
- [x] 更新提示词与 `react_engine.py` 支持规章意图识别与溯源引用
- [x] 编写 `test_rag.py` 确保召回与幂等加载测试通过
- [x] 补充毕业设计文档与核心算法伪代码素材归档：归档规章语料与 Top-K 检索对比测试用例至 `thesis_materials/03_test_cases/`

### 阶段 4：Vue 3 前端左右分栏与细粒度 SSE 联动 (待开始)
- [ ] Vue 3 + Tailwind CSS 左右分栏骨架搭建
- [ ] SSE 客户端解析（`think`、`tool_call`、`citation`、`ticket_mutation`）
- [ ] 左侧对话流（思考过程折叠框 + Tool 卡片 + 溯源徽章）
- [ ] 右侧实时数据看板（健康监控指标 + 实时工单列表 + 资产台账）
- [ ] 左右双向无感联动与变更突变响应
- [ ] **毕设素材归档**：截取思考气泡、工具卡片与右侧联动高清图至 `thesis_materials/02_screenshots/`

### 阶段 5：Docker 容器化、封板验收与答辩材料归档 (待开始)
- [ ] 后端与前端 `Dockerfile` 编写
- [ ] 根目录 `docker-compose.yml` 与 Nginx 反代配置
- [ ] 一键启动测试与 24h 极速开发封板
- [ ] **录制 3 分钟中期检查/答辩免死金牌演示视频**并存入 `thesis_materials/05_demo_video/`

---

## 五、 里程碑变更记录 (Changelog)

| 日期与时间 | 变更阶段 | 变更内容概述 | 操作人 / 会话 |
| :--- | :--- | :--- | :--- |
| 2026-09-09 | 阶段 1 | 创建全周期开发任务清单，启动阶段 1 骨架搭建 | Antigravity AI |
| 2026-09-09 | 阶段 1 | 完成后端工程初始化、SQLite+SQLAlchemy 2.0 数据底座（Ticket, Asset, AuditLog, ChatHistory）、RESTful CRUD API 路由与自动化回归测试，阶段 1 封板 | Antigravity AI |
| 2026-09-09 | 阶段 1 | 严谨复核并深度加固：修复工单号生成碰撞与唯一索引异常处理、完善工单/资产编号与关键词搜索过滤、启用 SQLite WAL 并发与超时配置、增加 Pydantic 模式 extra='forbid' 与空白过滤、补全 AuditLog/ChatHistory 模式、实现测试数据库隔离并扩充至 15 项自动化用例全部通过 | Antigravity AI |
| 2026-09-09 | 阶段 2 | 依赖安装与配置扩展：安装 `openai>=1.14.0`，在 `config.py` 增加 `REACT_MAX_STEPS` 与 `AGENT_MOCK_MODE="auto"` 配置项 | Antigravity AI |
| 2026-09-09 | 阶段 2 | 工具注册中心与审计机制：编写 `app/tools/registry.py`，实现 `@tool` 装饰器、自动提取类型与生成 OpenAI Function Calling JSON Schema、统一安全派发并全自动持久化 `AuditLog` 审计表 | Antigravity AI |
| 2026-09-09 | 阶段 2 | 垂直业务工具集实现：实现 `metric_tools`（服务器指标采集与 >40℃ 超温预警）、`ticket_tools`（工单增查改与 TK 自动编号）、`asset_tools`（资产台账检索、借用防重复借出校验、归还与健康状态变更） | Antigravity AI |
| 2026-09-09 | 阶段 2 | 手写 ReAct 调度引擎：编写 `app/agent/prompts.py` 规范人设，编写 `app/agent/react_engine.py` 实现约 150 行无第三方黑盒框架的 while 状态机循环、双模驱动（真实 API + 确定性 Mock 容灾大脑）、OpenAI 标准消息流格式、同步 `run()` 与流式 `stream_run()`（标准结构化事件）、`ChatHistory` 对话与思考链持久化 | Antigravity AI |
| 2026-09-09 | 阶段 2 | 自动化测试与质量加固：编写 `tests/test_tools.py` 与 `tests/test_react_engine.py`，覆盖状态循环、超温提单联动、防重复借用、边界防御、模型幻觉参数过滤、API超时降级与 SSE 契约 | Antigravity AI |
| 2026-09-09 | 阶段 2 | 深度复核与二轮加固：修复不存在设备虚构健康指标致命缺陷；补全 MockDecisionBrain 对工单流转、资产健康更新与主动提单的调度支撑；修复 Windows GBK 编码异常字符；增强 execute_tool 参数智能别名与循环引用审计安全；重构 metric_tools 消除测试对磁盘 SQLite 的隐藏依赖；全仓扩充至 52 项测试 100% 通过（2.40s） | Antigravity AI |
| 2026-09-09 | 阶段 2 | 毕设素材沉淀与看板封板：归档 `04_core_algorithms/react_engine_algorithm.md`（状态机形式化推导、Algorithm 1 伪代码与 Mermaid 时序图）及 `03_test_cases/phase2_agent_test_report.md` 测试报告，阶段 2 全面封板 | Antigravity AI |
| 2026-09-10 | 阶段 3 | 完成 RAG 知识库与检索集成：使用 `chromadb` 向量存储，实现了支持幂等加载的双模检索，编写了机房管理 3 篇结构化文档，更新了本地 MockBrain 并修复了因 L2 距离引发的召回错误；全面重写 E2E 测试扩展至 67 项全绿。阶段 3 封板。 | Antigravity AI |
