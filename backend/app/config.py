"""面向高校实验室的轻量化智能自治运维系统 (LabOps-Agent) 全局配置管理模块"""

from pathlib import Path
from typing import List, Any, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# 项目路径推导
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
DEFAULT_DATA_DIR = APP_DIR / "data"
DEFAULT_DB_FILE = DEFAULT_DATA_DIR / "labops.db"

import os

# 前端静态编译产物托管路径推导 (支持便携整合包模式与自定义指定)
STATIC_WEB_ENV = os.getenv("STATIC_WEB_DIR")
if STATIC_WEB_ENV:
    DEFAULT_WEB_DIR = Path(STATIC_WEB_ENV)
else:
    DEFAULT_WEB_DIR = BACKEND_DIR / "web"



class Settings(BaseSettings):
    """系统全局运行配置"""

    # 基础服务信息
    APP_NAME: str = "LabOps-Agent"
    APP_TITLE: str = "面向高校实验室的轻量化智能自治运维系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 跨域设置 (支持逗号分隔、* 通配符或 JSON 格式列表)
    CORS_ORIGINS: Union[List[str], str] = ["*"]

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

    # LLM 与 ReAct 引擎基础配置
    REACT_MAX_STEPS: int = 6
    AGENT_MOCK_MODE: str = "auto"  # auto (无Key自动Mock), mock (强制Mock), real (强制真实LLM)

    # 1. 传统/向后兼容配置 (兼容既有 .env 与单元测试 monkeypatch)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_MODEL_NAME: str = "deepseek-chat"

    # 2. 商业大模型主通道 (Primary Channel，默认 DeepSeek)
    PRIMARY_API_KEY: str = ""
    PRIMARY_BASE_URL: str = "https://api.deepseek.com/v1"
    PRIMARY_MODEL_NAME: str = "deepseek-chat"

    # 3. 商业大模型备用通道 (Fallback Channel，默认阿里通义千问 Qwen)
    FALLBACK_API_KEY: str = ""
    FALLBACK_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    FALLBACK_MODEL_NAME: str = "qwen3.8-flash"

    # 4. HTTP 网络与快速失败 (Fail-Fast) 熔断超时设置 (秒)
    LLM_CONNECT_TIMEOUT: float = 3.0  # 连接超时，防止云端崩溃时长时间挂起假死
    LLM_READ_TIMEOUT: float = 15.0  # 读取超时

    # 数据持久化目录与前端静态目录
    DATA_DIR: Path = DEFAULT_DATA_DIR
    WEB_DIR: Path = DEFAULT_WEB_DIR

    def get_primary_channel(self) -> dict:
        """获取主通道配置 (优先读取 PRIMARY_，若未配置则回落读取 OPENAI_ 传统配置)"""
        api_key = (self.PRIMARY_API_KEY or self.OPENAI_API_KEY or "").strip()
        base_url = (self.PRIMARY_BASE_URL or self.OPENAI_BASE_URL or "https://api.deepseek.com/v1").strip()
        model_name = (self.PRIMARY_MODEL_NAME or self.OPENAI_MODEL_NAME or "deepseek-chat").strip()
        name = "DeepSeek" if "deepseek" in base_url.lower() or "deepseek" in model_name.lower() else "主模型"
        return {
            "name": name,
            "api_key": api_key,
            "base_url": base_url,
            "model_name": model_name,
        }

    def get_fallback_channel(self) -> dict:
        """获取备用通道配置 (默认阿里通义千问 Qwen)"""
        api_key = (self.FALLBACK_API_KEY or "").strip()
        base_url = (self.FALLBACK_BASE_URL or "https://dashscope.aliyuncs.com/compatible-mode/v1").strip()
        model_name = (self.FALLBACK_MODEL_NAME or "qwen3.8-flash").strip()
        name = "通义千问" if "dashscope" in base_url.lower() or "qwen" in model_name.lower() else "备用模型"
        return {
            "name": name,
            "api_key": api_key,
            "base_url": base_url,
            "model_name": model_name,
        }


    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", BACKEND_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, __context) -> None:
        # 确保数据目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
