#!/bin/bash
# ==============================================================================
# 面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) - macOS 一键启动脚本
# ==============================================================================

cd "$(dirname "$0")" || exit 1

echo "=============================================================================="
echo "       面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent)"
echo "       macOS 平台轻量启动器 (支持 Apple Silicon M系列 / Intel 芯片)"
echo "=============================================================================="
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "[错误] 未检测到 Python 3 环境！"
    echo "请在 Mac 终端运行 'brew install python' 或访问 https://www.python.org/ 安装 Python 3。"
    echo "按任意键退出..."
    read -n 1
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "[1/4] 检测到本地环境: ${PYTHON_VERSION}"

VENV_DIR=".venv_mac"
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/4] 首次运行：正在创建轻量隔离虚拟环境 (${VENV_DIR})..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[错误] 虚拟环境创建失败，尝试直接使用全局 python3 运行..."
        PY_CMD="python3"
    else
        PY_CMD="${VENV_DIR}/bin/python3"
    fi
else
    PY_CMD="${VENV_DIR}/bin/python3"
fi

echo "[3/4] 正在核验核心依赖库..."
$PY_CMD -c "import fastapi, uvicorn, sqlalchemy, pydantic" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[提示] 检测到缺少必要依赖，正在自动快速安装 (使用清华镜像源加速)..."
    $PY_CMD -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple >/dev/null 2>&1
    $PY_CMD -m pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv requests httpx openai pytest chromadb -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "[提示] 国内镜像安装受阻，尝试官方源安装..."
        $PY_CMD -m pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv requests httpx openai pytest chromadb
    fi
fi

PORT_PID=$(lsof -ti:8000)
if [ -n "$PORT_PID" ]; then
    echo "[提示] 检测到 8000 端口被占用 (PID: ${PORT_PID})，尝试自动释放..."
    kill -9 "$PORT_PID" >/dev/null 2>&1
    sleep 1
fi

echo "[4/4] 正在拉起 LabOps-Agent 运维大盘服务..."
cd backend || exit 1
$PY_CMD -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

cleanup() {
    echo ""
    echo "[*] 正在安全停止后台服务..."
    kill "$SERVER_PID" 2>/dev/null
    exit 0
}
trap cleanup INT TERM EXIT

HEALTH_OK=0
for i in {1..15}; do
    sleep 1
    if curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        HEALTH_OK=1
        break
    fi
done

if [ "$HEALTH_OK" -eq 1 ]; then
    echo ""
    echo "=============================================================================="
    echo " [成功] LabOps-Agent 自治运维系统已就绪！"
    echo "=============================================================================="
    echo " * 统一门户与大盘:   http://127.0.0.1:8000/"
    echo " * 接口文档:         http://127.0.0.1:8000/docs"
    echo ""
    echo " 演示账号："
    echo "  - 超级管理员: admin        / admin666"
    echo "  - 教师用户:   teacher_li   / 123456"
    echo "  - 学生用户:   student_chen / 123456"
    echo "=============================================================================="
    echo "[*] 正在打开默认浏览器..."
    open "http://127.0.0.1:8000/"
    echo "提示：请保持当前终端窗口开启。关闭窗口或按 Ctrl+C 即可停止服务。"
    wait "$SERVER_PID"
else
    echo "[错误] 服务启动超时，请检查控制台报错。"
    wait "$SERVER_PID"
fi
