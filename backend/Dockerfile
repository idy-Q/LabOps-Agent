# ==============================================================================
# LabOps-Agent 后端服务容器化构建配置 (FastAPI + SQLAlchemy + ChromaDB)
# 采用官方纯净 Python 3.11-slim 镜像，确保安全、极小体积与高移植性
# ==============================================================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 环境变量：
# 1. PYTHONUNBUFFERED=1 保障标准输出即时刷新至 Docker 容器日志
# 2. PYTHONDONTWRITEBYTECODE=1 阻止生成 .pyc 缓存文件保持镜像纯净
# 3. PORT=8000 默认服务端口
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 优先复制依赖声明清单并预安装依赖，最大化利用 Docker 分层缓存机制
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制代码与初始规章语料数据
COPY app/ ./app/
COPY .env.example ./.env.example

# 建立数据目录兼容软链接：使 /app/data 与 /app/app/data 等价
RUN ln -s /app/app/data /app/data

# 暴露 FastAPI ASGI 服务端口
EXPOSE 8000

# 基于 Python 内置标准库 urllib 实现轻量级健康探针，无须额外安装 curl/wget
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').getcode() == 200 else 1)"

# 启动 Uvicorn 高性能异步 Web 服务
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

