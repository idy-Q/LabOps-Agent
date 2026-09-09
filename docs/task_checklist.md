# LabOps-Agent 全周期开发任务清单与进度看板

> **跨会话续接说明**：  
> 本文件位于工作区 `docs/task_checklist.md`，是跨对话框记忆与状态同步的**唯一事实来源（Single Source of Truth）**。  
> 每次新开对话时，只需对 AI 说：`“请阅读 docs/task_checklist.md 并继续下一步”`，AI 即可零偏差秒级恢复上下文。

---

## 一、 项目总览与里程碑进度

* **系统名称**：基于轻量级 ReAct 架构的高校机房智能运维与资产管理系统（LabOps-Agent）
* **开发策略**：严格 24 小时极速交付，KISS 极简可维护，严禁过度设计，阶段封板
* **当前总进度**：`[■■□□□] 阶段 1 已完成 (1/5 阶段完成)`

| 阶段 | 阶段目标 | 预估耗时 | 状态 | 完成时间 |
| :--- | :--- | :---: | :---: | :---: |
| **阶段 1** | **骨架搭建与数据底座（FastAPI + SQLite + CRUD）** | 4h | **已完成 (Completed)** | 2026-09-09 |
| **阶段 2** | **手写 ReAct 调度引擎与垂直业务工具集** | 7h | 待开始 (Ready) | - |
| **阶段 3** | **机房规章 RAG 知识库与检索集成** | 3h | 待开始 (Pending) | - |
| **阶段 4** | **Vue 3 前端左右分栏与细粒度 SSE 联动** | 6h | 待开始 (Pending) | - |
| **阶段 5** | **Docker 容器化、封板验收与答辩材料归档** | 4h | 待开始 (Pending) | - |

---

## 二、 当前阶段细化任务拆解：阶段 1（骨架搭建与数据底座）

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

- [x] **Task 1.4 RESTful API 路由实现**
  - [x] 编写 [backend/app/api/tickets.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/api/tickets.py)（列表、新增、详情、状态更新）
  - [x] 编写 [backend/app/api/assets.py](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/backend/app/api/assets.py)（列表、新增、设备借还/健康状态变更）
  - [x] 路由挂载至 `main.py` 并提供 `GET /api/health`

- [x] **Task 1.5 服务启动与接口验收**
  - [x] 自动初始化生成 `backend/app/data/labops.db`
  - [x] 测试运行 FastAPI 服务，验证 Swagger UI (`/docs`) 与 REST 接口 CRUD 正常
  - [x] 阶段 1 封板并更新任务清单

---

## 三、 后续阶段任务规划概要

### 阶段 2：手写 ReAct 调度引擎与垂直业务工具集 (待开始)
- [ ] 核心手写状态机 `agent/react_engine.py`（while 循环、Tools 派发、OpenAI 格式解析）
- [ ] 业务工具集：`metric_tools.py`、`ticket_tools.py`、`asset_tools.py`
- [ ] 工具调用审计集成（每次调用持久化至 `AuditLog`）
- [ ] 控制台测试脚本与状态流转闭环验证

### 阶段 3：机房规章 RAG 知识库与检索集成 (待开始)
- [ ] 准备 3 篇标准机房管理制度 Markdown
- [ ] ChromaDB 本地持久化与 Embedding 批量写入
- [ ] 实现 `query_regulations` 工具并入驻 Agent 工具池
- [ ] RAG 问答与规章引用溯源验证

### 阶段 4：Vue 3 前端左右分栏与细粒度 SSE 联动 (待开始)
- [ ] Vue 3 + Tailwind CSS 左右分栏骨架搭建
- [ ] SSE 客户端解析（`think`、`tool_call`、`citation`、`ticket_mutation`）
- [ ] 左侧对话流（思考过程折叠框 + Tool 卡片 + 溯源徽章）
- [ ] 右侧实时数据看板（健康监控指标 + 实时工单列表 + 资产台账）
- [ ] 左右双向无感联动与变更突变响应

### 阶段 5：Docker 容器化、封板验收与答辩材料归档 (待开始)
- [ ] 后端与前端 `Dockerfile` 编写
- [ ] 根目录 `docker-compose.yml` 与 Nginx 反代配置
- [ ] 一键启动测试与 24h 极速开发封板
- [ ] 录屏演示脚本与答辩防“套壳”支撑材料归档

---

## 四、 里程碑变更记录 (Changelog)

| 日期与时间 | 变更阶段 | 变更内容概述 | 操作人 / 会话 |
| :--- | :--- | :--- | :--- |
| 2026-09-09 | 阶段 1 | 创建全周期开发任务清单，启动阶段 1 骨架搭建 | Antigravity AI |
| 2026-09-09 | 阶段 1 | 完成后端工程初始化、SQLite+SQLAlchemy 2.0 数据底座（Ticket, Asset, AuditLog, ChatHistory）、RESTful CRUD API 路由与自动化回归测试，阶段 1 封板 | Antigravity AI |

