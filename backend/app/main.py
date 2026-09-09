"""LabOps-Agent 后端服务主入口

包含：
1. FastAPI 实例初始化与生命周期挂载
2. CORS 跨域中间件配置
3. 健康检查端点 (/api/health)
4. 工单管理与资产管理 RESTful API 路由挂载
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db.init_db import init_db
from app.api import tickets, assets

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器：启动时自动校验数据库并预置种子数据"""
    logger.info("正在启动 %s (v%s)...", settings.APP_NAME, settings.APP_VERSION)
    init_db(seed=True)
    logger.info("数据底座初始化完毕，服务准备就绪。")
    yield
    logger.info("服务关闭完成。")


app = FastAPI(
    title=settings.APP_NAME,
    description="高校机房智能运维与资产管理系统后端服务 API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置跨域请求中间件 (支持前端 Vue 3 跨域访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载业务路由
app.include_router(tickets.router, prefix="/api/tickets", tags=["运维工单管理"])
app.include_router(assets.router, prefix="/api/assets", tags=["机房资产管理"])


@app.get("/", include_in_schema=False)
def root():
    """根路径重定向至 Swagger API 交互文档"""
    return RedirectResponse(url="/docs")


@app.get(
    "/api/health",
    tags=["系统健康"],
    summary="服务健康检查",
    description="返回当前系统运行健康状态及基本配置信息",
)
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
