# 基于轻量级 ReAct 架构的智能自治运维系统（LabOps-Agent）

> 🎓 **计算机科学与技术 / 软件工程 本科毕业设计工程全量套件**  
> 本工作区严格遵循清晰的职责分离规范：**毕设工程代码**、**整理沉淀文档与答辩材料**、**AI Agent 扩展技能库** 互相独立、边界清晰，保障系统开箱即用与长期可维护性。

---

## 一、 工作区顶层目录职责划分

工作区各层级结构已完成妥善梳理与物理/逻辑分离：

```text
毕设/
├── backend/                       # 【毕设项目工程 - 后端服务】
│   ├── app/                       # FastAPI 核心源码 (ReAct 调度引擎、Tools 注册中心、RAG 知识库、REST/SSE API、用户认证与鉴权)
│   ├── tests/                     # 自动化回归测试套件 (覆盖工具集、调度引擎、RAG、用户鉴权、端到端接口，115 项全绿)
│   ├── demo_cli.py                # 终端极简演示 CLI 交互脚本
│   ├── requirements.txt           # Python 依赖清单
│   ├── Dockerfile                 # 后端生产级轻量镜像构建 (python:3.11-slim + urllib 健康探针)
│   ├── .dockerignore              # 后端构建上下文隔离配置
│   └── .venv/                     # Python 独立虚拟环境
│
├── frontend/                      # 【毕设项目工程 - 前端界面】
│   ├── src/                       # Vue 3 + Tailwind CSS 响应式交互界面 (左右分栏联动大盘、全景毛玻璃认证弹窗、防冒名借调)
│   ├── package.json               # 前端工程与依赖配置
│   ├── vite.config.js             # Vite 构建与开发服务器配置
│   ├── Dockerfile                 # 前端 Multi-stage 多阶段构建 (Node 20 -> Nginx Alpine 极轻托管 < 30MB)
│   ├── nginx.conf                 # 前端镜像内置 Nginx 规则 (与根目录权威配置保持同步)
│   └── .dockerignore              # 前端构建上下文隔离配置
│
├── nginx/                         # 【网关与反向代理层】
│   └── default.conf               # 权威 Nginx 反代配置 (前端静态托管 + /api/ 反代 + SSE 流式防缓冲长超时穿透 + /docs 直达)
│
├── docs/                          # 【整理出的文档中心 - 架构规划与答辩归档】
│   ├── README.md                  # 文档中心总览与索引指引
│   ├── architecture_and_development_plan.md  # 顶层系统架构设计与落地规划方案
│   ├── task_checklist.md          # 跨会话续接唯一事实来源（Single Source of Truth）、全周期任务清单与看板
│   └── thesis_materials/          # 毕业论文写作与答辩专用素材沉淀
│       ├── 01_database_design/    # 数据库建表 DDL (schema.sql)、5 张核心表逻辑设计数据字典与论文第4章导航 (含 README)
│       ├── 02_screenshots/        # 系统核心功能界面规范截图说明
│       ├── 03_test_cases/         # 全周期 6 份阶段测试报告、115 项用例矩阵与论文第6章导航 (含 README)
│       ├── 04_core_algorithms/    # ReAct 引擎与 RAG 算法形式化推导及 Algorithm 1 伪代码
│       └── 05_demo_video/         # 3~5 分钟标准答辩演示操作台本、口述词与 6 大考点防拷问锦囊
│
├── scripts/                       # 【辅助运维与快捷工具集】
│   ├── run_cli.bat                # 终端极速体验手写 ReAct 调度脚本 (Windows 双击直达)
│   └── run_cli.sh                 # 终端极速体验手写 ReAct 调度脚本 (Linux/macOS)
│
├── .agent/                        # 【AI 辅助开发技能库 - 遵循 Antigravity 官方标准规范】
│   └── skills/                    # 规范化 Agent 技能目录 (含 ui-ux-pro-max 及 6 项子技能套件)
│
├── docker-compose.yml             # 全栈多容器服务编排 (backend + frontend + 命名卷 labops_data 数据持久化)
├── start.bat                      # Windows 双轨一键极速启动器 (方案A: 任务栏静默/桌面零遮挡/自动弹浏览器)
├── start.sh                       # Linux/macOS 双轨一键极速启动器
├── stop.bat                       # Windows 一键服务停止器 (一键安全释放 8000/5173 端口与进程)
├── stop.sh                        # Linux/macOS 一键服务停止器
├── .gitignore                     # Git 忽略规则（已隔离运行时 DB、ChromaDB、缓存与临时文件）
└── README.md                      # 本说明文档
```

---

## 二、 毕设项目工程启动与验收指南

### 1. 双轨一键极速启动与一键下线 (推荐: 双击即跑)

系统提供双轨启动器，自动检测宿主机 Docker 环境：若检测到 Docker 则提供容器化拉起；若 Docker 未开启则自动平滑切入本地轻量化开发环境，确保“在答辩老师机器上 100% 跑起来”。采用**任务栏智能最小化**机制，桌面零弹窗遮挡，启动后 3 秒直接弹出默认浏览器进入系统大盘！

* **启动系统**：
  - **Windows 用户**：直接双击根目录下 `start.bat`（或在终端运行 `.\start.bat`）
  - **Linux / macOS 用户**：在终端执行 `./start.sh`
* **一键停止与端口释放**：
  - **Windows 用户**：直接双击根目录下 `stop.bat`
  - **Linux / macOS 用户**：在终端执行 `./stop.sh`

---

### 2. Docker Compose 全栈容器化交付 (生产标准)

```bash
# 1. 在项目根目录执行一键构建并后台拉起全栈容器集群
docker compose up -d --build

# 2. 查看容器运行状态与健康探针
docker compose ps
```
* **系统统一门户与前端大盘**：浏览器访问 `http://localhost/`（80 端口统一入口）
* **Swagger 交互接口文档**：浏览器访问 `http://localhost/docs`（由 Nginx 直接反代穿透）
* **后端健康检查端点**：`GET http://localhost/api/health`
* **停止并清理容器集群**：`docker compose down`（数据通过命名卷 `labops_data` 持久化，重启不丢失）

---

### 3. 本地轻量化开发与单测回归模式 (Local Mode)

#### 后端服务启动与测试 (Backend)
```bash
# 1. 切换至后端目录并激活虚拟环境 (Windows PowerShell)
cd backend
.\.venv\Scripts\activate

# 2. 运行全套自动化测试回归 (确保 115 项全绿)
pytest tests/

# 3. 启动 FastAPI 本地开发服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 前端服务启动与构建 (Frontend)
```bash
# 1. 切换至前端目录
cd frontend

# 2. 启动前端 Vite 热更新开发服务器
npm run dev

# 3. 生产环境打包构建校验
npm run build
```
* **前端本地交互大盘**：浏览器访问 `http://localhost:5173`（默认端口）

---

### 4. 终端 ReAct 引擎极速体验 (CLI Mode)

系统额外提供了便捷的终端交互脚本，无需拉起浏览器和前端大盘，即可在纯控制台环境下沉浸式体验手写白盒 ReAct 状态机的思维链推理、工具调用与数据库状态闭环：

* **Windows 双击直达**：直接双击运行 `scripts/run_cli.bat`；
* **Linux / macOS 终端**：运行 `./scripts/run_cli.sh`；
* **终端命令行手动调用**：
  ```bash
  cd backend
  .\.venv\Scripts\python.exe demo_cli.py
  ```

---

## 三、 系统典型预置账号与权限控制说明

系统内置基于角色的访问控制（RBAC）与资产借调防冒名闭环机制。数据库已预置 4 位典型角色用户（密码统一加盐不可逆存储）：

| 登录工号/学号 | 初始密码 | 真实姓名 | 身份角色 | 归属部门 / 班级 | 权限特征与业务限制 |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `admin` | `admin666` | 王主管 | `ADMIN` | 网络中心运维部 | 超级管理员权限，支持全量资产调度与工单归档 |
| `teacher_li` | `123456` | 李老师 | `TEACHER` | 物联网工程教研室 | 具备机房设备正常借调登记权限（借用人实名只读锁定） |
| `teacher_zhang` | `123456` | 张老师 | `TEACHER` | 网络安全教研室 | 具备机房设备正常借调登记权限（借用人实名只读锁定） |
| `student_chen` | `123456` | 陈同学 | `STUDENT` | 计科2201班 | 学生权限受限：**资产借用按钮自动置灰禁用**，杜绝越权借机 |

* 🛡️ **超级管理员专属安全激活口令**：`admin666`（用于前端新用户注册申请 `ADMIN` 角色时的提权防御拦截验证）。
* 🔒 **借调防冒名机制**：借用设备时，“借用人”自动绑定当前登录用户的真实姓名与部门并锁定为 `readonly`，彻底杜绝冒名顶替他人登记借用核心设备。

---

## 四、 Agent 技能体系规范 (`.agent/skills/`)

本工作区内置针对高校机房系统设计的专用 UI/UX 决策技能 `ui-ux-pro-max`。
技能按照 Antigravity 官方规范（`skills/<name>/SKILL.md`）部署，开箱即用：

```bash
# 执行本地免网络设计检索（支持 style, color, ux, landing, product, typography 等领域）
python .agent/skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain style
```

---

## 五、 毕业设计与论文撰写快速导航

* **写论文第 1~3 章（需求与架构）**：参考 [docs/architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md)。
* **写论文第 4 章（数据库设计）**：参考 [docs/thesis_materials/01_database_design/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/01_database_design/)。
* **写论文第 5 章（核心算法与实现）**：参考 [docs/thesis_materials/04_core_algorithms/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/04_core_algorithms/)。
* **写论文第 6 章（测试用例与分析）**：参考 [docs/thesis_materials/03_test_cases/](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/) 与 [phase5_deployment_and_acceptance_report.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/03_test_cases/phase5_deployment_and_acceptance_report.md)。
* **毕业答辩与中期检查演示演练**：参考 [presentation_script.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/thesis_materials/05_demo_video/presentation_script.md)（3~5 分钟标准操作台本、逐秒口述词与 6 大考点防拷问锦囊）。
* **跨会话开发续接**：对 AI 说 `“请阅读 docs/task_checklist.md 并继续下一步”` 即可零偏差恢复上下文。

