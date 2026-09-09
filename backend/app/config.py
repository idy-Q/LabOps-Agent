"""LabOps-Agent 全局配置管理模块"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目路径推导
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
DEFAULT_DATA_DIR = APP_DIR / "data"
DEFAULT_DB_FILE = DEFAULT_DATA_DIR / "labops.db"


class Settings(BaseSettings):
    """系统全局运行配置"""

    # 基础服务信息
    APP_NAME: str = "LabOps-Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 跨域设置
    CORS_ORIGINS: List[str] = ["*"]

    # 数据库配置 (默认 SQLite 嵌入式文件)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

    # LLM 与 ReAct 引擎配置 (预留阶段 2 使用)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_MODEL_NAME: str = "deepseek-chat"

    # 数据持久化目录
    DATA_DIR: Path = DEFAULT_DATA_DIR

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, __context) -> None:
        # 确保数据目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
