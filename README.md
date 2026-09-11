# 基于轻量级 ReAct 架构的智能自治运维系统（LabOps-Agent）

> 🎓 **计算机科学与技术 / 软件工程 本科毕业设计工程全量套件**  
> 本工作区严格遵循清晰的职责分离规范：**毕设工程代码**、**整理沉淀文档与答辩材料**、**AI Agent 扩展技能库** 互相独立、边界清晰，保障系统开箱即用与长期可维护性。

---

## 一、 工作区顶层目录职责划分

工作区各层级结构已完成妥善梳理与物理/逻辑分离：

```text
毕设/
├── backend/                       # 【毕设项目工程 - 后端服务】
│   ├── app/                       # FastAPI 核心源码 (ReAct 调度引擎、Tools 注册中心、RAG 知识库、REST/SSE API)
│   ├── tests/                     # 自动化回归测试套件 (覆盖工具集、调度引擎、RAG、端到端接口，77 项全绿)
│   ├── demo_cli.py                # 终端极简演示 CLI 交互脚本
│   ├── requirements.txt           # Python 依赖清单
│   └── .venv/                     # Python 独立虚拟环境
│
├── frontend/                      # 【毕设项目工程 - 前端界面】
│   ├── src/                       # Vue 3 + Tailwind CSS 响应式交互界面 (左右分栏联动大盘)
│   ├── package.json               # 前端工程与依赖配置
│   └── vite.config.js             # Vite 构建与开发服务器配置
│
├── docs/                          # 【整理出的文档中心 - 架构规划与答辩归档】
│   ├── README.md                  # 文档中心总览与索引指引
│   ├── architecture_and_development_plan.md  # 顶层系统架构设计与落地规划方案
│   ├── task_checklist.md          # 跨会话续接唯一事实来源（Single Source of Truth）、全周期任务清单与看板
│   └── thesis_materials/          # 毕业论文写作与答辩专用素材沉淀
│       ├── 01_database_design/    # 数据库建表 DDL (schema.sql) 与逻辑设计数据字典
│       ├── 02_screenshots/        # 系统核心功能界面规范截图说明
│       ├── 03_test_cases/         # 各阶段 77+ 项测试用例执行报告（论文直接复用）
│       ├── 04_core_algorithms/    # ReAct 引擎与 RAG 算法形式化推导及 Algorithm 1 伪代码
│       └── 05_demo_video/         # 3分钟中期检查/毕业答辩演示视频录制指引
│
├── .agent/                        # 【AI 辅助开发技能库 - 遵循 Antigravity 官方标准规范】
│   └── skills/                    # 规范化 Agent 技能目录
│       ├── ui-ux-pro-max/         # UI/UX 设计智能全栈决策引擎 (包含离线检索脚本与本地数据集)
│       ├── banner-design/         # 横幅设计辅助技能
│       ├── brand/                 # 品牌视觉辅助技能
│       ├── design/                # 通用设计指引技能
│       ├── design-system/         # 设计系统落地技能
│       ├── slides/                # 答辩幻灯片设计技能
│       └── ui-styling/            # UI 样式与 Tailwind 配套技能
│
├── .gitignore                     # Git 忽略规则（已隔离运行时 DB、ChromaDB、缓存与临时文件）
└── README.md                      # 本说明文档
```

---

## 二、 毕设项目工程启动与验收指南

### 1. 后端服务启动与测试 (Backend)

```bash
# 1. 切换至后端目录并激活虚拟环境 (Windows PowerShell)
cd backend
.\.venv\Scripts\activate

# 2. 运行全套自动化测试回归 (确保 77 项全绿)
pytest tests/

# 3. 启动 FastAPI 本地开发服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
* **Swagger 接口文档**：浏览器访问 `http://127.0.0.1:8000/docs`
* **健康检查接口**：`GET http://127.0.0.1:8000/api/health`

### 2. 前端服务启动与构建 (Frontend)

```bash
# 1. 切换至前端目录
cd frontend

# 2. 启动前端 Vite 热更新开发服务器
npm run dev

# 3. 生产环境打包构建校验
npm run build
```
* **前端交互大盘**：浏览器访问 `http://localhost:5173`（默认端口）

---

## 三、 Agent 技能体系规范 (`.agent/skills/`)

本工作区内置针对高校机房系统设计的专用 UI/UX 决策技能 `ui-ux-pro-max`。
技能按照 Antigravity 官方规范（`skills/<name>/SKILL.md`）部署，开箱即用：

```bash
# 执行本地免网络设计检索（支持 style, color, ux, landing, product, typography 等领域）
python .agent/skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain style
```

---

## 四、 毕业设计与论文撰写快速导航

* **写论文第 1~3 章（需求与架构）**：参考 [docs/architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md)。
* **写论文第 4 章（数据库设计）**：参考 [docs/thesis_materials/01_database_design/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/)。
* **写论文第 5 章（核心算法与实现）**：参考 [docs/thesis_materials/04_core_algorithms/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/04_core_algorithms/)。
* **写论文第 6 章（测试用例与分析）**：参考 [docs/thesis_materials/03_test_cases/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/)。
* **跨会话开发续接**：对 AI 说 `“请阅读 docs/task_checklist.md 并继续下一步”` 即可零偏差恢复上下文。
