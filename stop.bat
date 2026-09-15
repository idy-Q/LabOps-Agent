@echo off
chcp 65001 >nul
title 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 一键服务停止器

echo ==============================================================================
echo       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 一键服务停止器
echo ==============================================================================
echo.

echo [*] 正在检测并释放 8000 端口 (FastAPI 后端)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [*] 正在检测并释放 5173 端口 (Vite 前端)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [*] 正在检查并停止 Docker 容器集群 (若有)...
docker compose down >nul 2>&1

echo.
echo ==============================================================================
echo  [成功] 前后端后台服务与容器集群已全部安全停止，端口已就绪释放！
echo ==============================================================================
echo.
pause
exit /b 0
