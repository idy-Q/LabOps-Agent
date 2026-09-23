# LabOps-Agent（面向高校实验室的轻量化智能自治运维系统）文档中心

> 本目录为面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) 的**顶层设计、架构流转、技术规范与工程实施方案**的统一存放地，与系统的核心工程代码（`backend/`、`frontend/`）保持清晰的物理与逻辑职责分离。

---

## 一、 目录结构索引

```text
docs/
├── README.md                                 # 本文档：文档中心总览与索引导航
├── architecture_and_development_plan.md      # 系统顶层设计、ReAct 调度流转与架构实现方案
├── feature_roadmap_and_plan.md               # 演进特性路线图与技术实现方案总册（FEAT-01~04）
├── task_checklist.md                         # 全周期研发任务跟踪与里程碑看板（阶段 1~10 完整封板）
└── thesis_materials/                         # 毕业设计与答辩核心支撑材料库
    ├── 01_database_design/                   # 数据库数据字典与物理 DDL 架构
    ├── 02_screenshots/                       # 界面设计、拟态双模态与交互截图指引
    ├── 03_test_cases/                        # 全生命周期测试用例与测试报告（全栈 172 项全绿）
    ├── 04_core_algorithms/                   # 白盒 ReAct 状态机引擎与混合 RAG 算法解析
    └── 05_demo_video/                        # 毕业设计答辩演示文稿与全流程演示脚本
```

---

## 二、 核心技术方案导读

### 1. 顶层设计与架构规划 ([architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md))
* **定位**：系统设计目标、技术选型（Vue 3 + FastAPI + SQLite + ChromaDB）、高可靠状态闭环设计与整体架构时序。
* **核心内容**：
  - **业务场景与痛点分析**：设备资产分散、健康监控孤立、规程检索低效、学生越权乱象。
  - **白盒化 ReAct 调度**：手写状态机循环（Thought -> Action -> Observation）、RBAC 越权卫士与 Mermaid 完整时序流转图。
  - **数据持久层设计**：SQLite 关系型存储（工单/资产/审计/用户权限/机房/工单流转/借还日志）与 ChromaDB 本地向量库集成。
  - **工程规范与交付形态**：前后端单体轻量化同仓管理、Docker Compose 生产编排与反向代理网关。
  - **阶段规划推进**：阶段 1 ~ 阶段 10 完整闭环，涵盖主动自治巡检、机柜 2D 拓扑、工单流转履历时间轴与规章规程知识中心。
  - **白盒化 RAG 架构实现专章**：第七章系统级阐述规章规程知识中心设计哲学、关系型与向量库双模桥接模型、Top-K 逆向溯源映射机制与白盒化查验探针。

### 2. 演进特性路线图与技术方案 ([feature_roadmap_and_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/feature_roadmap_and_plan.md))
* **定位**：系统增量里程碑特性的架构推演、交互设计规范与技术落地闭环总册。
* **核心交付成果**：
  - **FEAT-01 主动自治巡检与研判简报**：遍历资产遥测探针，多维越界判定与防重复建单闭环，独立沙箱 A4 PDF 研报打印引擎。
  - **FEAT-02 机房机柜 2D 机位拓扑视图**：实训机房 2 架标准 42U 机柜物理 U 位仿真标尺、设备跨行占用、热力与健康态势直观可视。
  - **FEAT-03 运维工单流转与资产履历时序时间轴**：工单全时序状态演化、处置人实名审计防抵赖、全景档案穿透弹窗与资产全生命周期时间轴。
  - **FEAT-04 规章规程知识中心与 RAG 向量切块查验**：机房规程多维检索与条款沉浸式阅读、安全红线微光高亮、向 AI 咨询交互联动与底层向量分块透明查验。

### 3. 全周期任务看板与里程碑 ([task_checklist.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/task_checklist.md))
* **定位**：工程实现执行层进度追踪，记录每个子阶段的任务拆解、验证指标与变更日志（Changelog）。
* **核心里程碑**：
  - 阶段 1~5：脚手架、FastAPI 核心服务、白盒 ReAct 引擎、混合 RAG 知识检索、Vue 3 玻璃拟态前端与容器编排；
  - 阶段 6：RBAC 越权拦截卫士、身份前置引导 Popover、安全盾牌卡片与冰晶白拟态深度重构；
  - 阶段 7~10：全机房主动自治巡检、机柜 2D 拓扑视图、时序履历抽屉、规章知识中心与 RAG 切块透明查验（全栈测试 172 项全绿）。

### 4. 毕业设计与答辩材料库 ([thesis_materials/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials))
* **[01_database_design](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design)**：完整的 ER 关系、表结构设计说明及 `schema.sql`；
* **[03_test_cases](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases)**：各阶段测试用例与综合测试验收报告（含 `phase10_regulations_knowledge_center_test_report.md` 与 `auth_and_rbac_test_report.md`）；
* **[04_core_algorithms](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/04_core_algorithms)**：ReAct 状态机引擎与 RAG 向量检索算法（层次分块、余弦规整化与白盒探针）的数学定义、流转机制与伪代码；
* **[05_demo_video](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/05_demo_video)**：毕业答辩 10 分钟演示提纲、操作动线与解说词脚本。

---

## 三、 文档与工程代码协同规范

1. **工程与文档边界明确**：
   - 系统源码严格位于根目录的 `backend/`（后端服务）与 `frontend/`（前端界面）；
   - 所有全局系统设计、时序架构图纸统一归档至本 `docs/` 目录，保持根目录清爽规范。
2. **知识库语料说明**：
   - 后端运行时 RAG 所需的规范语料文本位于 `backend/app/data/regulations/`，属于后端运行依赖资产，不由本目录接管。
3. **本地开发材料说明**：
   - 开发者本地任务看板与多媒体材料已配置于 `.gitignore` 中，保留在本地工作区，公开仓库保持轻量与专注。
