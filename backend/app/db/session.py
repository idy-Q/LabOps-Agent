"""数据库连接与会话管理"""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings

# 判断是否为 SQLite 连接，SQLite 默认限制多线程共享连接，需配置 check_same_thread=False
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# 初始化 SQLAlchemy 引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型声明基类 (SQLAlchemy 2.0 风格)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖项：获取数据库会话并在请求结束时自动释放"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
