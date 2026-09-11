# LabOps-Agent 毕设文档与答辩材料中心

> 本目录为毕业设计相关**全量整理文档、架构设计方案、任务进度看板与论文归档素材**的统一集中存放地，与系统的工程代码（`backend/`、`frontend/`）保持清晰的物理与逻辑职责分离。

---

## 一、 目录结构索引

```text
docs/
├── README.md                                 # 本文档：文档与材料索引导航
├── architecture_and_development_plan.md      # 系统顶层设计、防“套壳”策略与快速落地规划方案
├── task_checklist.md                         # 跨会话续接唯一事实来源（Single Source of Truth）、全周期任务清单与看板
└── thesis_materials/                         # 毕业论文与答辩专用素材沉淀归档
    ├── 01_database_design/                   # 数据库物理设计脚本 (schema.sql) 与逻辑数据字典
    ├── 02_screenshots/                       # 核心界面与交互时序截图规范指引
    ├── 03_test_cases/                        # 阶段自动化回归测试用例报告（API、Agent、RAG、SSE联动）
    ├── 04_core_algorithms/                   # 核心算法形式化定义、伪代码与时序流程图（ReAct引擎、RAG检索）
    └── 05_demo_video/                        # 3分钟中期检查/毕业答辩演示视频录制指引
```

---

## 二、 核心文档职责说明

### 1. 顶层设计与架构规划 ([architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md))
* **定位**：系统立项论证、技术选型（Vue 3 + FastAPI + SQLite + ChromaDB）、答辩防“套壳”指标与整体架构时序。
* **主要用途**：用于毕业论文第 1、2、3 章（绪论、关键技术、需求分析与总体设计）的直接参考。

### 2. 开发看板与跨会话记忆 ([task_checklist.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/task_checklist.md))
* **定位**：全周期 5 个开发阶段的原子任务推进表与详细变更日志（Changelog）。
* **主要用途**：任何新对话只需输入 `“请阅读 docs/task_checklist.md 并继续下一步”`，AI 即可零偏差恢复上下文。

### 3. 毕设论文与答辩材料库 (`thesis_materials/`)
* **01 数据库设计**：含建表 DDL 与包含 4 张核心表（工单、设备资产、审计日志、会话历史）字段、主外键约束与索引规划的数据字典，可直接贴入论文第 4 章“数据库设计”小节。
* **02 界面与交互截图**：提供左右分栏、SSE 流式思考折叠框、工具调用卡片与数据看板联动的规范截图说明。
* **03 测试报告集**：包含阶段 1~4 的端到端测试覆盖用例，覆盖 77+ 项自动化回归测试与性能数据，直接作为论文第 6 章“系统测试”实测数据。
* **04 核心算法模型**：提供 ReAct 原生状态机循环、Algorithm 1 形式化伪代码与 RAG 余弦相似度召回逻辑，筑牢学术创新点壁垒。
* **05 演示视频指引**：用于答辩现场与中期检查视频准备。

---

## 三、 文档与工程代码协同规范

1. **工程与文档边界明确**：
   - 毕设系统代码严格位于工作区根目录的 `backend/`（后端服务）与 `frontend/`（前端界面）；
   - 所有非运行期的文字报告、论文材料、架构图纸统一归档至本 `docs/` 目录，杜绝文档与临时素材在根目录随意堆放。
2. **知识库语料例外说明**：
   - 后端运行时 RAG 所需的规范语料文本位于 `backend/app/data/regulations/`，属于后端运行依赖资产，不由本目录接管。
