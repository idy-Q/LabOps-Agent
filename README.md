# 基于轻量级 ReAct 架构的智能自治运维系统（LabOps-Agent）

> 🚀 **面向高校实验室与机房基础设施的垂直领域智能自治运维 Agent 系统**  
> 本项目基于原生轻量级 **ReAct（Reasoning + Acting）白盒推理调度引擎** 与 **RAG 运维规程检索增强**，深度打通监控采集、规范研判、工单闭环与资产借调防冒名审计全流程。采用前后端分离但同仓协同的极简架构，支持生产级 Docker Compose 容器编排与宿主机本地双轨极速拉起，开箱即用。

---

## 一、 系统核心特性

- 🧠 **白盒化原生 ReAct 调度引擎**：摒弃复杂的庞大封装框架（如 LangChain），由手写约 150 行标准 ReAct 状态机循环调度，透明执行 Thought -> Action -> Observation 闭环，链路清晰可控。
- 🔄 **真实业务状态与双向联动**：拒绝“无状态对话套壳”，Agent 执行结果真实写入 SQLite 关系型数据库。前端采用**左右分栏联动大盘**，对话中提单或借调资产，右侧看板无感局部自动增补刷新。
- ⚡ **细粒度 SSE 结构化流式交互**：解构大模型响应流，实时推送 `<think>` 思考折叠过程、Tool Call 工具调用卡片、规章制度 Citation 溯源徽章与业务变更 Mutation 事件。
- 🛡️ **企业级 RBAC 权限与防冒名机制**：内置超级管理员、教师、学生多级权限；密码加盐哈希存储；`admin666` 安全提权口令防御；资产借调实名凭据只读绑定，彻底杜绝冒名登记与越权操作。
- 🐳 **双轨极速部署与生产级容器化**：提供 Windows / Linux / macOS 双轨一键极速启动脚本（自动侦测并自适应 Docker 与本地轻量环境，桌面零遮挡），同时提供完整的 Multi-stage Docker Compose 编排体系与 Nginx 生产网关。
- 🧩 **自包含 Agent 技能体系**：内置 Antigravity 标准 Agent 技能扩展库（含 `ui-ux-pro-max` 等），支持离线快速设计领域检索。

---

## 二、 工作区目录结构

```text
LabOps-Agent/
├── backend/                       # 【后端核心服务 - FastAPI】
│   ├── app/                       # 核心业务源码 (ReAct 调度引擎、Tools 注册中心、RAG 知识库、REST/SSE API、用户鉴权)
│   ├── tests/                     # 自动化测试套件 (覆盖工具集、调度引擎、RAG、鉴权及接口，115 项用例全绿)
│   ├── demo_cli.py                # 终端极简演示 CLI 交互脚本
│   ├── requirements.txt           # Python 依赖清单
│   ├── Dockerfile                 # 后端生产级轻量镜像构建 (python:3.11-slim + urllib 健康探针)
│   └── .venv/                     # Python 独立虚拟环境
│
├── frontend/                      # 【前端交互界面 - Vue 3 + Tailwind CSS】
│   ├── src/                       # 响应式交互大盘 (左右分栏联动大盘、全景毛玻璃认证弹窗、防冒名借调)
│   ├── package.json               # 前端工程与依赖配置
│   ├── vite.config.js             # Vite 构建与开发服务器配置
│   ├── Dockerfile                 # 前端 Multi-stage 构建 (Node 20 -> Nginx Alpine 镜像 < 30MB)
│   └── nginx.conf                 # 前端镜像内置 Nginx 规则
│
├── nginx/                         # 【网关与反向代理层】
│   └── default.conf               # 权威 Nginx 反代配置 (前端静态托管 + /api/ 反代 + SSE 流式防缓冲长超时穿透 + /docs 直达)
│
├── docs/                          # 【系统架构与设计文档中心】
│   ├── README.md                  # 文档中心总览与技术规范索引
│   └── architecture_and_development_plan.md  # 顶层系统架构设计与落地规划方案
│
├── scripts/                       # 【快捷体验脚本】
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
├── .gitignore                     # Git 忽略规则（已隔离运行时 DB、向量库、缓存、临时文件与本地备用材料）
└── README.md                      # 本项目说明文档
```

---

## 三、 快速上手与运行部署指南

### 1. 双轨一键极速启动与一键下线 (推荐: 双击即跑)

系统提供双轨启动器，自动检测宿主机 Docker 环境：若检测到 Docker 则提供容器化拉起；若 Docker 未开启则自动平滑切入本地轻量化开发环境，确保在各类环境下 100% 开箱即用无缝启动。采用**任务栏智能最小化**机制，桌面零弹窗遮挡，启动后 3 秒直接弹出默认浏览器进入系统大盘！

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

## 四、 系统典型预置账号与权限控制说明

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

## 五、 Agent 技能体系规范 (`.agent/skills/`)

本工作区内置针对高校机房系统设计的专用 UI/UX 决策技能 `ui-ux-pro-max`。
技能按照 Antigravity 官方规范（`skills/<name>/SKILL.md`）部署，开箱即用：

```bash
# 执行本地免网络设计检索（支持 style, color, ux, landing, product, typography 等领域）
python .agent/skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain style
```

---

## 六、 更多架构与技术规范

更多关于系统架构推导、时序流转图、数据库表结构及接口契约的设计细节，欢迎查阅：
- 📑 **系统文档中心**：[docs/README.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/README.md)
- 📐 **系统架构设计方案**：[docs/architecture_and_development_plan.md](file:///d:/%E6%96%87%E6%A1%A3%E5%8D%B7/Program%20language/%E6%AF%95%E8%AE%BE/docs/architecture_and_development_plan.md)
