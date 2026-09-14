#!/usr/bin/env bash
echo "=============================================================================="
echo "      高校机房智能自治运维系统 (LabOps-Agent) - 一键服务停止器"
echo "=============================================================================="
echo ""

echo "[*] 正在释放 8000 与 5173 端口进程..."
if command -v lsof >/dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
elif command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null
    fuser -k 5173/tcp 2>/dev/null
fi

echo "[*] 正在停止 Docker 容器集群 (若有)..."
docker compose down 2>/dev/null

echo ""
echo "[成功] 前后端服务与容器集群已全部安全停止！"
