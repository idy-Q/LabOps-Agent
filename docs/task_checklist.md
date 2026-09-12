# LabOps-Agent 全周期开发任务清单与进度看板

> **跨会话续接说明**：  
> 本文件位于工作区 `docs/task_checklist.md`，是跨对话框记忆与状态同步的**唯一事实来源（Single Source of Truth）**。  
> 每次新开对话时，只需对 AI 说：`“请阅读 docs/task_checklist.md 并继续下一步”`，AI 即可零偏差秒级恢复上下文。

---

## 一、 项目总览与里程碑进度

* **系统名称**：基于轻量级 ReAct 架构的智能自治运维系统（LabOps-Agent）
* **开发策略**：严格 24 小时极速交付，KISS 极简可维护，严禁过度设计，阶段封板
* **当前总进度**：`[■■■■□] 阶段 4 已完成 (4/5 阶段完成)`

| 阶段 | 阶段目标 | 预估耗时 | 状态 | 完成时间 |
| :--- | :--- | :---: | :---: | :---: |
| **阶段 1** | **骨架搭建与数据底座（FastAPI + SQLite + CRUD）** | 4h | **已完成 (Completed)** | 2026-09-09 |
| **阶段 2** | **手写 ReAct 调度引擎与垂直业务工具集** | 7h | **已完成 (Completed)** | 2026-09-09 |
| **阶段 3** | **机房规章 RAG 知识库与检索集成** | 3h | **已完成 (Completed)** | 2026-09-10 |
| **阶段 4** | **Vue 3 前端左右分栏与细粒度 SSE 联动** | 6h | **已完成 (Completed)** | 2026-09-10 |
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

- [x] **Task 1.6 阶段一毕设素材沉淀与归档 (docs/thesis_materials/)**
  - [x] 创建 `docs/thesis_materials/` 目录树（01~05 子目录结构）
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
  - [x] 编写 [docs/thesis_materials/04_core_algorithms/react_engine_algorithm.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/04_core_algorithms/react_engine_algorithm.md)（状态机形式化定义、Algorithm 1 伪代码、Mermaid 时序图）
  - [x] 编写 [docs/thesis_materials/03_test_cases/phase2_agent_test_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase2_agent_test_report.md)（阶段二完整测试报告，论文直接复用）
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
- [x] 补充毕业设计文档与核心算法伪代码素材归档：归档规章语料与 Top-K 检索对比测试用例至 `docs/thesis_materials/03_test_cases/`

### 阶段 4：Vue 3 前端左右分栏与细粒度 SSE 联动 (已完成)
- [x] Vue 3 + Tailwind CSS 左右分栏骨架搭建
- [x] SSE 客户端解析（`think`、`tool_start`、`tool_end`、`citation`、`ticket_mutation`、`asset_mutation`）
- [x] 左侧对话流（思考过程折叠框 + Tool 卡片 + 溯源徽章）
- [x] 右侧实时数据看板（健康监控指标 + 实时工单列表 + 资产台账）
- [x] 左右双向无感联动与变更突变响应
- [x] **毕设素材归档**：归档测试报告与联动验证数据至 `docs/thesis_materials/03_test_cases/phase4_frontend_sse_test_report.md`

### 阶段 5：Docker 容器化、封板验收与答辩材料归档 (待开始)
- [ ] 后端与前端 `Dockerfile` 编写
- [ ] 根目录 `docker-compose.yml` 与 Nginx 反代配置
- [ ] 一键启动测试与 24h 极速开发封板
- [ ] **录制 3 分钟中期检查/答辩免死金牌演示视频**并存入 `docs/thesis_materials/05_demo_video/`

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
| 2026-09-10 | 阶段 4 | 完成 Vue 3 + Tailwind CSS 前端左右分栏骨架、细粒度 SSE 流式交互协议（`think`, `tool_start`, `tool_end`, `citation`, `ticket_mutation`, `asset_mutation`, `content`, `done`）、仿 DeepSeek-R1 思考折叠组件、工具调用卡片、规约溯源徽章、监控指标大盘、工单脉冲高亮与资产借还看板，前后端双向联动全链路闭环，扩充至 74 项自动化测试 100% 通过，前端秒级极速编译，阶段 4 封板 | Antigravity AI |
| 2026-09-10 | 阶段 4 | 严谨复核并深度加固：修复多轮会话记忆缺失导致代词指代错误无法闭环处置历史工单的致命缺陷；实现跨轮次实体回溯与 ChatHistory 历史上下文自动注入；增强 tool_start/tool_end 全局 tool_call_id 异步精确配对；修复前端 SSE 解析 422 异常时 [object Object] 乱码与 error 异常事件漏处理；新增前端历史会话抽屉支持随时切换与对话回放；实现轻量级 Markdown 语法高亮与工单/资产脉冲高亮自动滚动视口；测试套件扩充至 77 项单测 100% 通过（3.24s），前端构建 0 报错 0 告警（115 kB），阶段 4 深度封板 | Antigravity AI |
| 2026-09-11 | 运维治理 | **工作区目录妥善整理与职责分离**：<br>1. **毕设项目与文档物理分离**：将散落在根目录的答辩与测试材料统一归拢至 `docs/thesis_materials/`，彻底分清“工程代码”与“论文交付文档”；<br>2. **Agent Skill 规范化就位**：遵循 Antigravity 官方标准，在 `.agent/skills/` 规范化部署 `ui-ux-pro-max` 及 6 项子技能套件，彻底清除冗余软链与临时源码；<br>3. **根因修复与坏味清除**：修复 `vector_store.py` 路径推导与 `regulation_tools.py` 模块导入期即触碰磁盘 ChromaDB 的副作用，在 `conftest.py` 实现测试期向量库物理隔离，根治测试跑批污染 Git 状态，清除根目录 `.pytest_cache` 污染并完善 `.gitignore`；<br>4. **项目运行保障**：全仓 77 项单测 100% 通过（测试零副作用、零脏状态），前端生产构建零报错，业务运行丝滑稳定。 | Antigravity AI |
| 2026-09-11 | 前端升级 | **智能自治运维 UI/UX 深度现代化重塑**：<br>1. **标题与定位升级**：系统浏览器标题及规范定名更新为“LabOps-Agent \| 智能自治运维”；<br>2. **Codex 动态流体背景与交互式 ASCII 矩阵**：纯原生 Canvas 2D 硬件加速实现 60FPS 极光色彩流幕与鼠标动力学字符水滴（`-`、`>`、`o` 凝聚演变）；<br>3. **全景透明玻璃化与三档调节**：全面升级为 Glassmorphism 界面，提供【纯透清澈 / 平衡毛玻璃 / 深邃亚克力】3 档预设及不透明度与模糊度无级滑块，支持本地记忆与沉稳纯色平滑淡出过渡；<br>4. **导航栏与看板极简精修**：重塑“齿轮+交叉扳手螺丝刀”高保真矢量 Logo，删除全景大盘所有冗余修饰小字（`Realtime Telemetry`、`Telemetry Nodes`、`1-Click` 等），历史与新建会话纯图标化，欢迎卡片同步精简纯净；<br>5. **工程质量保障**：生产构建 0 错误 0 告警，77 项单测全绿，前后端链路稳定流畅。 | Antigravity AI |
| 2026-09-11 | 主题系统 | **全站双模态（明亮/暗黑）主题系统与细节精修**：<br>1. **输入框提示精简**：输入框 placeholder 精简为轻量提示，去除冗长举例；<br>2. **新建会话按钮配色调优**：顶栏纯白加号按钮重构为契合页面主调的半透微光质感与双主题自适应配色；<br>3. **全站双模态（明亮/暗黑）主题系统**：保存暗黑极客科技玻璃风格的同时，研发高质感明亮冰晶微透风格；顶栏新增“明亮 / 暗黑”直观状态按钮与平滑切换；`<head>` 预注脚本实现 0 闪烁（Zero FOUC）；动态极光流体画布与 ASCII 水滴粒子支持浅色高对比度自适应渲染；<br>4. **单测沙箱加固**：在 `conftest.py` 会话级隔离大模型 Mock 模式，彻底杜绝外网 API 干扰；77 项单测 100% 绿灯（2.93s），前端 Vite 5 打包 0 错误 0 告警。 | Antigravity AI |
| 2026-09-12 | 交互重构 | **【方案一】动静分离交互重构与界面空间释放**：<br>1. **输入框常驻栏彻底移除**：清除 `ChatInput.vue` 上方常驻的 5 个死板 Prompt 胶囊，释放纵向视觉高度，回归紧凑纯粹终端风格；<br>2. **欢迎界面空态重塑**：重构 `ChatStream.vue` 中原本不可点击的静态展示卡片，升级为 3 张真正可点击、带精致微动效的【运维典型推荐场景卡片】（超温闭环提单、算力借还登记、用电防火规程），支持整卡点击直发与小图标填入二次编辑，对话开启后自动优雅退场；<br>3. **工程交互健壮性加固**：增加中文输入法 `isComposing` 回车防误发守卫，会话切换自动清理输入框草稿并安全中止旧流；支持键盘无障碍 Tab 导航与双模态（明亮/暗黑）自适应对比度；<br>4. **质量验证**：前端生产构建 0 错误 0 告警（866ms），后端 77 项单测全通（2.87s）。 | Antigravity AI |




