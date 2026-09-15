# LabOps-Agent 系统文档中心

> 本目录为 LabOps-Agent 系统的**顶层设计、架构流转、技术规范与工程实施方案**的统一存放地，与系统的核心工程代码（`backend/`、`frontend/`）保持清晰的物理与逻辑职责分离。

---

## 一、 目录结构索引

```text
docs/
├── README.md                                 # 本文档：文档中心总览与索引导航
└── architecture_and_development_plan.md      # 系统顶层设计、ReAct 调度流转与架构实现方案
```

---

## 二、 核心技术方案导读

### 1. 顶层设计与架构规划 ([architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md))
* **定位**：系统设计目标、技术选型（Vue 3 + FastAPI + SQLite + ChromaDB）、高可靠状态闭环设计与整体架构时序。
* **核心内容**：
  - **业务场景与痛点分析**：设备资产分散、健康监控孤立、规程检索低效。
  - **白盒化 ReAct 调度**：手写状态机循环（Thought -> Action -> Observation）与 Mermaid 完整时序流转图。
  - **数据持久层设计**：SQLite 关系型存储（工单/资产/审计/用户权限）与 ChromaDB 本地向量库集成。
  - **工程规范与交付形态**：前后端单体轻量化同仓管理、Docker Compose 生产编排与反向代理网关。
  - **常见架构考量 (FAQ)**：针对原生状态机、免黑盒框架选型以及防模型幻觉的深度解析。

---

## 三、 文档与工程代码协同规范

1. **工程与文档边界明确**：
   - 系统源码严格位于根目录的 `backend/`（后端服务）与 `frontend/`（前端界面）；
   - 所有全局系统设计、时序架构图纸统一归档至本 `docs/` 目录，保持根目录清爽规范。
2. **知识库语料说明**：
   - 后端运行时 RAG 所需的规范语料文本位于 `backend/app/data/regulations/`，属于后端运行依赖资产，不由本目录接管。
3. **本地开发材料说明**：
   - 开发者本地任务看板与多媒体材料已配置于 `.gitignore` 中，保留在本地工作区，公开仓库保持轻量与专注。
