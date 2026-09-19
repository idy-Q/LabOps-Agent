"""LabOps-Agent 方案 A: 免安装便携整合包构建脚本

负责将 Python 独立运行时、前端静态编译产物、后端业务代码、启动脚本打包组装至
02-免安装便携包_LabOps-Portable/ 目录中，生成真正的零依赖开箱即用绿色版。
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def print_step(step: str):
    print(f"\n======================================================\n[BUILD] {step}\n======================================================")

def main():
    script_dir = Path(__file__).resolve().parent
    dev_root = script_dir.parent
    workspace_root = dev_root.parent
    portable_root = workspace_root / "02-免安装便携包_LabOps-Portable"

    print(f"工作区根目录: {workspace_root}")
    print(f"开发工程目录: {dev_root}")
    print(f"便携包输出目录: {portable_root}")

    portable_root.mkdir(parents=True, exist_ok=True)

    # 1. 确保前端已完成生产编译
    print_step("1. 编译前端 Vue 3 生产静态资源")
    frontend_dir = dev_root / "frontend"
    frontend_dist = frontend_dir / "dist"
    if not (frontend_dist / "index.html").exists():
        print("正在执行 npm run build...")
        subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, check=True)
    else:
        print("检测到现有 frontend/dist 构建产物，重新构建以确保最新状态...")
        subprocess.run(["npm.cmd", "run", "build"], cwd=frontend_dir, check=True)

    # 复制前端编译产物至便携包 web/ 目录
    portable_web = portable_root / "web"
    if portable_web.exists():
        shutil.rmtree(portable_web)
    print(f"复制前端静态产物至: {portable_web}")
    shutil.copytree(frontend_dist, portable_web)

    # 2. 复制自包含 Python 运行时
    print_step("2. 构建自包含便携式 Python 运行时")
    python_base = Path(sys.base_prefix)
    if not (python_base / "python.exe").exists():
        python_base = Path(r"C:\Python314")
    venv_site_packages = dev_root / "backend" / ".venv" / "Lib" / "site-packages"
    portable_runtime = portable_root / "runtime"

    if not portable_runtime.exists():
        portable_runtime.mkdir(parents=True, exist_ok=True)

    # 2.1 复制根目录的 python.exe, pythonw.exe 及 dll
    print("复制 Python 解释器核心可执行文件与核心动态链接库...")
    for item in python_base.iterdir():
        if item.is_file() and (item.suffix.lower() in [".exe", ".dll", ".cat"] or item.name.startswith("LICENSE")):
            dest = portable_runtime / item.name
            if not dest.exists():
                shutil.copy2(item, dest)

    # 2.2 复制 DLLs 目录
    portable_dlls = portable_runtime / "DLLs"
    if not portable_dlls.exists():
        print("复制 DLLs 模块目录...")
        shutil.copytree(python_base / "DLLs", portable_dlls)

    # 2.3 复制 Python 标准库 (Lib)
    portable_lib = portable_runtime / "Lib"
    if not (portable_lib / "os.py").exists():
        print("复制 Python 标准库...")
        shutil.copytree(
            python_base / "Lib",
            portable_lib,
            ignore=shutil.ignore_patterns("test", "tests", "idlelib", "tkinter", "turtledemo", "__pycache__", "site-packages")
        )

    # 2.4 复制 site-packages 依赖库
    portable_site_packages = portable_lib / "site-packages"
    if not portable_site_packages.exists():
        portable_site_packages.mkdir(parents=True, exist_ok=True)

    print("同步第三方依赖库 (site-packages) 至便携运行时...")
    # 使用 robocopy 或自定义拷贝，过滤无用缓存
    # 使用 Python shutil 逐项复制第三方库
    for item in venv_site_packages.iterdir():
        dest = portable_site_packages / item.name
        if dest.exists():
            continue
        if item.is_dir():
            if item.name.startswith("__") or item.name.endswith(".dist-info"):
                # dist-info 保留或复制
                if item.name.startswith("__"):
                    continue
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif item.is_file():
            shutil.copy2(item, dest)

    print("自包含运行时环境准备就绪。")

    # 3. 复制后端核心代码
    print_step("3. 复制后端应用核心代码与数据底座")
    app_src = dev_root / "backend" / "app"
    app_dest = portable_root / "app"
    if app_dest.exists():
        shutil.rmtree(app_dest)
    print(f"复制应用核心至: {app_dest}")
    shutil.copytree(
        app_src,
        app_dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pytest_cache")
    )

    # 4. 生成开箱即用 .env
    print_step("4. 生成便携环境开箱即用 .env 配置文件")
    env_content = """# LabOps-Agent 方案 A 免安装便携整合包配置文件
APP_NAME=LabOps-Agent
APP_VERSION=1.0.0
DEBUG=False
HOST=127.0.0.1
PORT=8000

# 跨域设置
CORS_ORIGINS=*

# Agent 运行模式：auto (无 Key 自动使用本地离线确定性 Mock 调度大脑), mock, real
AGENT_MOCK_MODE=auto
REACT_MAX_STEPS=6

# 如需接入真实商业大模型 (如 DeepSeek)，请在此填入 API Key：
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL_NAME=deepseek-chat
"""
    (portable_root / ".env").write_text(env_content, encoding="utf-8")

    # 5. 生成 启动系统.bat 与 停止系统.bat
    print_step("5. 创建一键启停批处理脚本与说明文档")
    
    start_bat_content = """@echo off
chcp 65001 >nul
title 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 便携整合版

echo ==============================================================================
echo       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent)
echo       方案 A: 免安装绿色便携整合版 (开箱即用 · 零环境依赖)
echo ==============================================================================
echo.

set "PORTABLE_DIR=%~dp0"
cd /d "%PORTABLE_DIR%"

REM 强制隔离宿主外部 Python 环境变量与全局用户包，确保纯净绿色运行
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PYTHONIOENCODING=utf-8"

REM 1. 检测 8000 端口占用情况
echo [1/3] 正在检测端口可用性 (8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [提示] 检测到 8000 端口已被进程 PID: %%a 占用，正在尝试自动释放...
    taskkill /f /t /pid %%a >nul 2>&1
    ping 127.0.0.1 -n 2 >nul
)

REM 2. 启动自包含 Python FastAPI 服务 (前后端一体化静态托管)
echo [2/3] 正在启动自包含 LabOps-Agent 运维大盘服务 (后台运行)...
start "LabOps-Agent 便携服务" /min /d "%PORTABLE_DIR%" "%PORTABLE_DIR%runtime\\python.exe" -s -E -m uvicorn app.main:app --host 127.0.0.1 --port 8000

REM 3. 等待服务就绪并自动拉起浏览器
echo [3/3] 正在检测服务健康状态并拉起浏览器...
set "HEALTH_OK=0"
for /L %%i in (1,1,15) do (
    ping 127.0.0.1 -n 2 >nul
    "%PORTABLE_DIR%runtime\\python.exe" -s -E -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=1)" >nul 2>&1
    if not errorlevel 1 (
        set "HEALTH_OK=1"
        goto LAUNCH_SUCCESS
    )
)

echo.
echo ==============================================================================
echo  [错误] 服务启动超时 (15秒内未收到健康检查端点响应)！
echo ==============================================================================
echo  可能的原因：
echo   1. 8000 端口被系统其它软件或防火墙拦截占用；
echo   2. 请检查后台服务终端或日志了解详细异常报错。
echo ==============================================================================
echo.
pause
exit /b 1

:LAUNCH_SUCCESS
echo.
echo ==============================================================================
echo  [成功] LabOps-Agent 自治运维系统已成功启动并就绪！
echo ==============================================================================
echo  * 统一门户与大盘:   http://127.0.0.1:8000/
echo  * 后端 Swagger 接口: http://127.0.0.1:8000/docs
echo  * 后端健康检查端点: http://127.0.0.1:8000/api/health
echo.
echo  典型演示账号（密码已加盐）：
echo   - 超级管理员: admin        / admin666  (全量权限：工单调度、状态审批、审计日志)
echo   - 教师用户:   teacher_li   / 123456    (教学权限：实名借调、工单受理)
echo   - 学生用户:   student_chen / 123456    (受限权限：只读查看、权限隔离告警)
echo ==============================================================================
echo.
start "" "http://127.0.0.1:8000/"
echo [已打开浏览器] 正在访问系统首页...
echo.
echo 提示：
echo   1. 服务已在任务栏后台最小化运行，请勿强行关闭后台命令行窗口；
echo   2. 如需停止系统，请双击同目录下的 【停止系统.bat】 即可安全退出并释放端口。
echo ==============================================================================
echo.
pause
exit /b 0
"""
    (portable_root / "启动系统.bat").write_text(start_bat_content, encoding="utf-8")

    stop_bat_content = """@echo off
chcp 65001 >nul
title 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 一键停止器

echo ==============================================================================
echo       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 一键服务停止器
echo ==============================================================================
echo.

echo [*] 正在检测并安全停止 LabOps-Agent 8000 端口服务...
set "FOUND=0"
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /t /pid %%a >nul 2>&1
    set "FOUND=1"
)

if "%FOUND%"=="1" (
    echo [成功] 已成功停止正在运行的 LabOps-Agent 服务并释放 8000 端口！
) else (
    echo [提示] 未发现运行在 8000 端口的系统进程，系统未在运行。
)

echo.
echo ==============================================================================
echo 服务停止操作完毕。
echo ==============================================================================
echo.
pause
exit /b 0
"""
    (portable_root / "停止系统.bat").write_text(stop_bat_content, encoding="utf-8")

    readme_content = """# 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 便携整合版

## 1. 方案说明
本整合包为 **方案 A: 免安装便携整合包（开箱即用绿色版）**。
- **零环境依赖**：内置完整自包含的轻量 Python 运行环境与预编译依赖库，**无需**安装 Python、Node.js、Nginx 或任何数据库软件；
- **前后端一体化**：前端 Vue 3 + Tailwind CSS 生产静态资源已编译并统一托管于后端 FastAPI 8000 端口；
- **纯本地嵌入式存储**：集成 SQLite 实体数据库与 ChromaDB 向量知识库，开箱已内置完备的高校实验室资产种子数据与机房管理规章；
- **双模 Agent 调度**：内置确定性离线 Mock 智能决策调度引擎与 DeepSeek 商业大模型接口，无网/离线环境下仍可 100% 顺畅演示全部自治运维流程。

## 2. 快速使用
1. **启动系统**：
   - 双击运行根目录下的 `启动系统.bat`；
   - 系统将自动检测端口、拉起后台服务并自动在默认浏览器中打开 `http://127.0.0.1:8000/`。
2. **停止系统**：
   - 双击运行根目录下的 `停止系统.bat`，即可安全下线服务并释放端口。

## 3. 预置体验账号
| 角色 | 用户名 | 密码 | 权限范围 |
| :--- | :--- | :--- | :--- |
| **超级管理员** | `admin` | `admin666` | 全量资产增删改查、状态强更、工单派发与流转闭环、全量审计日志查看 |
| **教师用户** | `teacher_li` | `123456` | 资产台账查看、设备实名借调与归还、运维工单接单受理 |
| **学生用户** | `student_chen` | `123456` | 只读查看资产与健康状态；越权操作（借调/改状/工单处理）触发前端智能安全拦截 |

## 4. 目录结构
```
02-免安装便携包_LabOps-Portable/
├── 启动系统.bat        # 双击一键启动系统并拉起浏览器
├── 停止系统.bat        # 双击一键停止后台服务
├── README.md          # 本使用说明
├── .env               # 系统环境变量配置（如需配置真实大模型 Key）
├── app/               # 系统核心后端服务代码与数据底座
│   ├── data/          # SQLite 数据库文件 (labops.db) 与机房运维知识库
│   └── ...
├── web/               # Vue 3 前端静态编译产物 (HTML/CSS/JS)
└── runtime/           # 自包含便携 Python 运行时与全量依赖库
```

## 5. 常见问题
- **端口冲突**：如果 8000 端口被其它软件占用，`启动系统.bat` 会自动提示并尝试释放；或者可在 `.env` 中修改 `PORT=8001`。
- **大模型配置**：默认采用离线确定性 Mock 引擎。若需连接 DeepSeek，请记事本打开 `.env`，填入 `OPENAI_API_KEY=sk-xxxx`，重启即可无缝切换至商业大模型。
"""
    (portable_root / "README.md").write_text(readme_content, encoding="utf-8")

    # 6. 验证便携运行时
    print_step("6. 验证便携运行时独立性与模块可用性")
    env = {**os.environ, "PYTHONHOME": "", "PYTHONPATH": "", "PYTHONNOUSERSITE": "1", "PYTHONIOENCODING": "utf-8"}
    test_cmd = [
        str(portable_runtime / "python.exe"),
        "-s",
        "-E",
        "-c",
        "import fastapi, uvicorn, sqlalchemy, pydantic, starlette; import app.main; print('[PASS] 便携 Python 运行时核心依赖与应用服务入口全部自包含加载成功!')"
    ]
    res = subprocess.run(test_cmd, cwd=portable_root, env=env, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    if res.returncode != 0:
        print("STDERR:", res.stderr)
        raise RuntimeError("便携运行时依赖加载失败！")

    print("\n======================================================")
    print("[SUCCESS] 方案 A 免安装便携整合包构建完成！")
    print("======================================================")

if __name__ == "__main__":
    main()
