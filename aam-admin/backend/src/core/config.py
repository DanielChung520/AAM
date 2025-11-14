"""
@purpose: 配置管理模块，处理环境变量和应用配置
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from functools import lru_cache
from typing import Optional
import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """应用基础设置"""

    app_name: str = "AAM Admin Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)


class APISettings(BaseSettings):
    """API 设置"""

    api_host: str = "0.0.0.0"
    api_port: int = 8003
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_prefix="API_", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS origins，支持字符串、列表或逗号分隔的字符串"""
        if isinstance(v, str):
            # 尝试解析 JSON 格式（可能是 JSON 字符串）
            try:
                # 如果字符串看起来像 JSON 数组
                if v.strip().startswith("[") and v.strip().endswith("]"):
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            # 尝试逗号分隔的字符串
            if "," in v:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            # 单个字符串
            return [v] if v else []
        # 如果已经是列表，直接返回
        if isinstance(v, list):
            return v
        return v


class DatabaseSettings(BaseSettings):
    """数据库设置"""

    database_url: str = "postgresql://admin:admin@localhost:5433/aam_admin"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

    model_config = SettingsConfigDict(env_prefix="DB_", case_sensitive=False)


class DockerSettings(BaseSettings):
    """Docker 设置"""

    docker_host: Optional[str] = None  # None 表示使用默认的 Docker socket
    docker_base_url: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="DOCKER_", case_sensitive=False)


class AuthSettings(BaseSettings):
    """认证设置"""

    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 天 (7 * 24 * 60 = 10080 分钟)
    refresh_token_expire_days: int = 30  # 30 天
    aam_service_url: str = "http://localhost:8000"  # AAM 服务地址

    model_config = SettingsConfigDict(env_prefix="AUTH_", case_sensitive=False)


class Settings(BaseSettings):
    """应用总设置"""

    app: AppSettings = AppSettings()
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    docker: DockerSettings = DockerSettings()
    auth: AuthSettings = AuthSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（单例）"""
    return Settings()
