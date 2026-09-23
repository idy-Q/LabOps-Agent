"""面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) 后端服务主入口

包含：
1. FastAPI 实例初始化与生命周期挂载
2. CORS 跨域中间件配置
3. 健康检查端点 (/api/health)
4. 工单管理与资产管理 RESTful API 路由挂载
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.init_db import init_db
from app.tools.regulation_tools import _init_kb
from app.api import tickets, assets, chat, metrics, auth, regulations, notifications

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器：启动时自动校验数据库并预置种子数据与向量知识库"""
    logger.info("正在启动 %s (v%s)...", settings.APP_NAME, settings.APP_VERSION)
    init_db(seed=True)
    _init_kb()
    logger.info("数据底座与规章知识库初始化完毕，服务准备就绪。")
    yield
    logger.info("服务关闭完成。")


app = FastAPI(
    title=f"{settings.APP_TITLE} ({settings.APP_NAME})",
    description="面向高校实验室的轻量化智能自治运维系统后端服务 API",
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
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证与权限"])
app.include_router(chat.router, prefix="/api/chat", tags=["Agent 对话交互"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["机房运行监控大盘"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["运维工单管理"])
app.include_router(assets.router, prefix="/api/assets", tags=["机房资产管理"])
app.include_router(regulations.router, prefix="/api/regulations", tags=["规章规程知识中心"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["站内待办与超期督促通知"])


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


# 统一门户与静态前端托管 (支持免安装便携整合包与前后端一体化生产模式)
if settings.WEB_DIR.is_dir() and (settings.WEB_DIR / "index.html").is_file():
    assets_dir = settings.WEB_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_spa_root():
        """提供前端单页应用统一门户入口"""
        return FileResponse(settings.WEB_DIR / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_fallback(full_path: str):
        """处理前端静态资源文件直链与 SPA History 模式路由回退"""
        # API 路由 404 返回标准 JSON 异常，避免 SPA 回退掩盖接口错误
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")

        try:
            target_path = (settings.WEB_DIR / full_path).resolve()
            web_root = settings.WEB_DIR.resolve()
            if target_path.is_file() and target_path.is_relative_to(web_root):
                return FileResponse(target_path)
        except (ValueError, Exception):
            pass

        return FileResponse(settings.WEB_DIR / "index.html")
else:
    @app.get("/", include_in_schema=False)
    def root():
        """根路径重定向至 Swagger API 交互文档"""
        return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
