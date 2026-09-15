#!/usr/bin/env bash
# ==============================================================================
# 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - Linux/macOS 双轨一键启动器
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="$1"

echo "=============================================================================="
echo "       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - 双轨一键启动器"
echo "=============================================================================="
echo ""

start_docker() {
    echo "=============================================================================="
    echo "[*] 正在通过 Docker Compose 编排启动全栈容器服务..."
    echo "=============================================================================="
    cd "$SCRIPT_DIR"
    if ! docker compose up -d --build; then
        echo ""
        echo "[错误] Docker Compose 启动失败，请检查 Docker 服务是否正常运行。"
        echo "是否切换至本地轻量模式启动？(Y/n)"
        read -r -p "" RETRY_CHOICE || RETRY_CHOICE="Y"
        [ -z "$RETRY_CHOICE" ] && RETRY_CHOICE="Y"
        if [ "$RETRY_CHOICE" != "n" ] && [ "$RETRY_CHOICE" != "N" ]; then
            start_local
            return
        fi
        exit 1
    fi

    echo ""
    echo "=============================================================================="
    echo " [成功] LabOps-Agent 容器化集群启动成功！"
    echo "=============================================================================="
    echo " * 前端大盘与全栈入口:   http://localhost/"
    echo " * 后端 Swagger 接口文档: http://localhost/docs (或 http://localhost:8000/docs)"
    echo " * 后端健康检查端点:     http://localhost/api/health"
    echo ""
    echo " 典型演示账号（密码已加盐）："
    echo "  - 超级管理员: admin        / admin666  (具备全量资产调度与闭环归档权限)"
    echo "  - 教师用户:   teacher_li   / 123456    (具备设备实名借调权限，工单仅可受理)"
    echo "  - 学生用户:   student_chen / 123456    (只读受限，借调/改状按钮自动禁用)"
    echo "=============================================================================="
    echo "提示：如需停止容器集群，请在根目录执行: docker compose down"
}

start_local() {
    echo "=============================================================================="
    echo "[*] 正在启动本地轻量化开发服务 (Backend + Frontend)..."
    echo "=============================================================================="

    cd "$SCRIPT_DIR/backend"
    echo "[*] 启动后端 FastAPI ASGI 服务 (端口 8000)..."
    if [ -f ".venv/bin/python" ]; then
        .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
    elif [ -f ".venv/Scripts/python.exe" ]; then
        .venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
    elif [ -f ".venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
        python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
    else
        python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
    fi
    BACKEND_PID=$!

    cd "$SCRIPT_DIR/frontend"
    echo "[*] 启动前端 Vite 交互大盘 (端口 5173)..."
    npm run dev &
    FRONTEND_PID=$!

    cleanup() {
        echo ""
        echo "[*] 正在停止本地开发服务..."
        kill "$BACKEND_PID" 2>/dev/null || true
        kill "$FRONTEND_PID" 2>/dev/null || true
        echo "[*] 已清理所有后台子进程。"
        exit 0
    }
    trap cleanup INT TERM

    echo ""
    echo "=============================================================================="
    echo " [成功] 本地轻量化双轨服务运行中 (按 Ctrl+C 即可同时停止前后端)"
    echo "=============================================================================="
    echo " * 前端开发大盘:         http://localhost:5173/"
    echo " * 后端 Swagger 接口文档: http://127.0.0.1:8000/docs"
    echo " * 后端健康检查端点:     http://127.0.0.1:8000/api/health"
    echo "=============================================================================="

    wait
}

if [ "$MODE" = "docker" ]; then
    start_docker
    exit 0
elif [ "$MODE" = "local" ]; then
    start_local
    exit 0
fi

echo "[1/2] 正在检测本地运行环境..."
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "[OK] 检测到 Docker 引擎正在运行。"
    echo ""
    USER_CHOICE="1"
    read -r -p "请选择启动模式 (1: Docker 容器化, 2: 本地轻量模式, 默认 1): " INPUT_CHOICE || true
    [ -n "$INPUT_CHOICE" ] && USER_CHOICE="$INPUT_CHOICE"
    if [ "$USER_CHOICE" = "2" ]; then
        start_local
    else
        start_docker
    fi
else
    echo "[提示] 检测到 Docker 未开启或未安装 Docker 引擎。"
    echo "[提示] 自动平滑切换至【本地轻量化启动模式】..."
    echo ""
    start_local
fi

