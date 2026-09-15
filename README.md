# LabOps-Agent

LabOps-Agent 是一个面向高校实验室与机房场景的轻量化智能自治运维系统。系统采用自研 ReAct（Reasoning + Acting）推理循环与 RAG 规程知识检索，集成了设备运行监控、故障报修闭环、管理规范问答以及设备借用登记等功能。

通过自然语言交互，Agent 可以解析运维意图并调用对应的业务工具，执行结果直接写入底层关系型数据库，并通过 SSE（Server-Sent Events）事件流驱动前端大盘实时局部刷新。

---

## 技术栈

- **前端**：Vue 3、Vite、Tailwind CSS、Pinia
- **后端**：FastAPI、Python 3.11、Pydantic、SQLAlchemy
- **数据与检索**：SQLite（业务数据）、ChromaDB（本地规章向量库）
- **网关与容器化**：Docker、Docker Compose、Nginx

---

## 核心功能

- **ReAct 智能调度**：基于状态机实现 Thought-Action-Observation 循环，将自然语言请求拆解为明确的工具调用链路，支持多轮推理与状态回传。
- **RAG 规章知识库**：基于本地向量数据库检索机房管理规范与安全应急条例，回答包含引用来源溯源。
- **业务双向联动**：对话中触发的报修提单、状态变更与设备借调直接写入数据库，前端看板无感自动局部增补刷新。
- **权限与借用控制**：内置基于角色的访问控制（RBAC），支持管理员、教师与学生分级权限；借用流程实名绑定当前登录用户，防止非本人操作。
- **结构化流式交互**：前端通过 SSE 接收后端返回，提供思考过程折叠、工具调用卡片与最终回复的结构化展示。

---

## 快速开始

### 方式一：Docker Compose（推荐）

需确保本机已安装并启动 Docker。

```bash
# 构建并后台启动全部服务
docker compose up -d --build

# 查看服务运行状态
docker compose ps
```

启动完成后可直接访问：
- **Web 前端大盘**：`http://localhost`
- **Swagger 接口文档**：`http://localhost/docs`
- **后端健康检查**：`http://localhost/api/health`

如需停止服务：
```bash
docker compose down
```

---

### 方式二：一键脚本运行

项目内置了环境自动适配启动脚本：
- **Windows**：双击运行根目录下的 `start.bat`（停止服务双击 `stop.bat`）
- **Linux / macOS**：在终端运行 `./start.sh`（停止服务运行 `./stop.sh`）

脚本会自动检测系统环境：若检测到 Docker 则优先使用容器启动；若无 Docker 环境则尝试拉起本地 Python 虚拟环境与 Vite 服务。

---

### 方式三：本地开发模式

#### 1. 后端服务 (FastAPI)

```bash
cd backend

# 创建并激活虚拟环境 (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行单测
pytest tests/

# 启动开发服务器
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. 前端服务 (Vue 3)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产构建
npm run build
```

前端本地开发地址为：`http://localhost:5173`。

---

### 方式四：纯终端 CLI 体验

无需启动前端，可在终端直接体验 ReAct 循环调度：

```bash
cd backend
python demo_cli.py
```
Windows 用户亦可直接双击运行 `scripts/run_cli.bat`。

---

## 环境配置

复制配置模板即可开始使用：

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

核心配置项说明：

| 配置项 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `AGENT_MOCK_MODE` | `auto` | `auto`：未配置 API Key 时自动启用内置 Mock 调度器，已配置时自动调用外部大模型；<br>`mock`：强制使用内置确定性 Mock 调度器（离线可用）；<br>`real`：强制使用真实大模型 |
| `OPENAI_API_KEY` | *(空)* | 模型服务商 API Key（如 DeepSeek、OpenAI 等） |
| `OPENAI_BASE_URL` | `https://api.deepseek.com/v1` | 兼容 OpenAI 格式的接口地址 |
| `OPENAI_MODEL_NAME` | `deepseek-chat` | 模型名称 |
| `PORT` | `8000` | 后端服务监听端口 |

> **提示**：系统在未填写 API Key 时默认以 `auto` 模式运行，可直接通过内置 Mock 逻辑体验完整的业务链路。

---

## 预置账号

系统预置了 4 个不同角色的测试账号（密码加盐存储）：

| 账号 | 初始密码 | 姓名 | 角色 | 部门 / 班级 | 权限说明 |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `admin` | `admin666` | 王主管 | `ADMIN` | 网络中心运维部 | 系统超级管理员，具备资产调配与全部工单处置权限 |
| `teacher_li` | `123456` | 李老师 | `TEACHER` | 物联网工程教研室 | 设备借调登记与报修权限，借用人信息实名绑定 |
| `teacher_zhang` | `123456` | 张老师 | `TEACHER` | 网络安全教研室 | 设备借调登记与报修权限，借用人信息实名绑定 |
| `student_chen` | `123456` | 陈同学 | `STUDENT` | 计科2201班 | 普通查看与报修提单权限，受限角色无法借调核心设备 |

---

## 项目结构

```text
LabOps-Agent/
├── backend/                  # 后端服务
│   ├── app/                  # 核心源码 (ReAct 调度器、Tools 注册、RAG 向量库、API 路由)
│   ├── tests/                # 自动化测试用例
│   ├── demo_cli.py           # 命令行交互演示脚本
│   ├── requirements.txt      # Python 依赖清单
│   └── Dockerfile            # 后端 Docker 镜像构建文件
├── frontend/                 # 前端服务
│   ├── src/                  # Vue 3 源码 (运维大盘、对话组件、借调弹窗)
│   ├── package.json          # Node 依赖配置
│   ├── vite.config.js        # Vite 构建配置
│   └── Dockerfile            # 前端多阶段构建文件
├── nginx/                    # 网关配置
│   └── default.conf          # Nginx 反向代理与 SSE 长连接配置
├── docs/                     # 架构与技术文档
│   ├── README.md             # 文档索引
│   └── architecture_and_development_plan.md  # 系统架构设计方案
├── scripts/                  # 辅助体验脚本
├── docker-compose.yml        # 全栈容器编排
├── start.bat / start.sh      # 跨平台一键启动脚本
├── stop.bat / stop.sh        # 跨平台一键停止脚本
└── README.md                 # 项目说明文档
```

---

## 架构与技术文档

关于系统状态机设计、数据模型定义及时序交互图，请参阅：
- [系统架构与落地设计方案](docs/architecture_and_development_plan.md)
- [文档中心导航](docs/README.md)

