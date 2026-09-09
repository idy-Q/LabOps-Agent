"""LabOps-Agent 全局配置管理模块"""

from pathlib import Path
from typing import List, Any
import json
from pydantic import field_validator
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

    # 跨域设置 (支持逗号分隔或 JSON 格式列表)
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
        return v

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
