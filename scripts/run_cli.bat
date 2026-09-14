@echo off
chcp 65001 >nul
title LabOps-Agent 终端演示 CLI (ReAct 状态机极速体验)

echo ==============================================================================
echo       高校机房智能自治运维系统 (LabOps-Agent) - 终端 ReAct 演示 CLI
echo ==============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"

REM 探测 Python 解释器优先级：backend/.venv -> 项目根目录 .venv -> 系统 PATH
set "PYTHON_EXE="
if exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"
) else if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if "%PYTHON_EXE%"=="" (
    echo [错误] 未找到可用的 Python 运行环境！
    echo 推荐解决办法：
    echo   1. 运行项目根目录下的 start.bat 自动配置运行环境；
    echo   2. 或在 backend 目录下执行 python -m venv .venv 并安装依赖。
    echo.
    pause
    exit /b 1
)

echo [*] 正在准备运行环境并启动终端 ReAct 交互引擎...
echo [*] 工作路径: "%BACKEND_DIR%"
echo [*] 解释器:   "%PYTHON_EXE%"
echo.

set "PYTHONIOENCODING=utf-8"
cd /d "%BACKEND_DIR%"
"%PYTHON_EXE%" demo_cli.py
set "EXIT_CODE=%errorlevel%"

if %EXIT_CODE% neq 0 (
    echo.
    echo [提示] 进程已退出，返回代码: %EXIT_CODE%
)

echo.
echo ==============================================================================
echo 终端演示会话已结束。按任意键关闭窗口...
echo ==============================================================================
pause >nul
exit /b 0

