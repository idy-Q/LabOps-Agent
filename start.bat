@echo off
chcp 65001 >nul
title 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 一键启动器

echo ==============================================================================
echo       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 双轨一键启动器
echo ==============================================================================
echo.

set "ROOT_DIR=%~dp0"
set "USER_CHOICE=1"

REM 检测 Docker 运行环境
echo [1/2] 正在检测本地运行环境...
docker info >nul 2>&1
if errorlevel 1 goto DOCKER_NOT_FOUND

echo [OK] 检测到 Docker 引擎正在运行。
echo.
echo 请选择启动模式 (直接回车默认使用 [1] Docker 模式):
echo   [1] Docker 容器化启动 (推荐: 前后端一体化 Nginx 80 端口)
echo   [2] 本地轻量化启动 (FastAPI + Vite 独立开发服务)
echo.
set /p "USER_CHOICE=请输入选项 1 或 2 [默认 1]: "
if "%USER_CHOICE%"=="2" goto START_LOCAL
goto START_DOCKER

:DOCKER_NOT_FOUND
echo [提示] 检测到 Docker Desktop 未开启或未安装 Docker 引擎。
echo [提示] 自动平滑切换至 本地轻量化启动模式...
echo.
goto START_LOCAL

:START_DOCKER
echo ==============================================================================
echo [2/2] 正在通过 Docker Compose 编排启动全栈容器服务...
echo ==============================================================================
docker compose up -d --build
if errorlevel 1 goto DOCKER_FAIL

echo.
echo ==============================================================================
echo  [成功] LabOps-Agent 容器化集群启动成功！
echo ==============================================================================
echo  * 统一门户与大盘:   http://localhost/
echo  * 后端 Swagger 接口: http://localhost/docs
echo  * 后端健康检查端点: http://localhost/api/health
echo.
echo 正在自动拉起默认浏览器访问系统...
ping 127.0.0.1 -n 3 >nul
start "" "http://localhost/"
echo.
echo 提示：如需停止容器集群，请运行根目录的 stop.bat 或执行: docker compose down
echo ==============================================================================
pause
exit /b 0

:DOCKER_FAIL
echo.
echo [错误] Docker Compose 启动失败，请检查 Docker Desktop 是否正常运行。
echo 是否切换至本地轻量模式启动？(Y/N)
set "RETRY_CHOICE=Y"
set /p "RETRY_CHOICE=请输入 (Y/N) [默认 Y]: "
if /i "%RETRY_CHOICE%"=="Y" goto START_LOCAL
pause
exit /b 1

:START_LOCAL
echo ==============================================================================
echo [2/2] 正在启动本地轻量化开发服务 (方案A: 后台终端默认最小化静默运行)...
echo ==============================================================================

echo [*] 正在启动后端 FastAPI ASGI 服务 (端口 8000，任务栏最小化)...
start "LabOps-Backend (FastAPI)" /min /d "%ROOT_DIR%backend" cmd /k "chcp 65001 >nul & .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [*] 正在启动前端 Vite 交互大盘 (端口 5173，任务栏最小化)...
start "LabOps-Frontend (Vite)" /min /d "%ROOT_DIR%frontend" cmd /k "chcp 65001 >nul & npm run dev"

echo.
echo ==============================================================================
echo  [成功] 本地轻量化双轨服务已就绪 (桌面无弹窗遮挡)！
echo ==============================================================================
echo  * 前端开发大盘:     http://localhost:5173/
echo  * 后端 Swagger 接口: http://127.0.0.1:8000/docs
echo  * 后端健康检查端点: http://127.0.0.1:8000/api/health
echo.
echo  典型演示账号（密码已加盐）：
echo   - 超级管理员: admin        / admin666  (具备全量资产调度与闭环归档权限)
echo   - 教师用户:   teacher_li   / 123456    (具备设备实名借调权限，工单仅可受理)
echo   - 学生用户:   student_chen / 123456    (只读受限，借调/改状按钮自动禁用)
echo ==============================================================================
echo.
echo 正在等待服务就绪并自动拉起默认浏览器访问系统 (3秒)...
ping 127.0.0.1 -n 4 >nul
start "" "http://localhost:5173/"
echo [完成] 已自动在默认浏览器中打开前端交互界面！
echo.
echo [提示] 前后端终端已最小化至任务栏。如需查看实时服务输出日志，
echo        可随时在任务栏点击对应窗口展开；如需一键下线，运行 stop.bat 即可。
echo.
pause
exit /b 0
