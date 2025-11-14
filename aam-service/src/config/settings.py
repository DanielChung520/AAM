"""
@purpose: 基於 Pydantic BaseSettings 的配置管理類，自動從環境變量加載配置
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.interfaces.i_model_provider import ModelProviderType


class AppSettings(BaseSettings):
    """應用程序基礎配置"""
    app_name: str = Field(default="AAM Service", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class APISettings(BaseSettings):
    """API 配置"""
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_key: str = Field(alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "your-secret-api-key-change-in-production":
            raise ValueError("API_KEY 必須設置且不能使用默認值")
        return v


class ChromaDBSettings(BaseSettings):
    """ChromaDB 配置"""
    chromadb_host: str = Field(default="chromadb", alias="CHROMADB_HOST")
    chromadb_port: int = Field(default=8000, alias="CHROMADB_PORT")
    chromadb_collection_name: str = Field(
        default="knowledge_assets", alias="CHROMADB_COLLECTION_NAME"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def chromadb_url(self) -> str:
        """構建 ChromaDB 連接 URL"""
        return f"http://{self.chromadb_host}:{self.chromadb_port}"


class PostgresSettings(BaseSettings):
    """PostgreSQL 配置"""
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="aam_personas", alias="POSTGRES_DB")
    postgres_user: str = Field(default="aam_user", alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def postgres_url(self) -> str:
        """構建 PostgreSQL 連接 URL（同步）"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_async_url(self) -> str:
        """構建 PostgreSQL 連接 URL（異步）"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class RabbitMQSettings(BaseSettings):
    """RabbitMQ 配置"""
    rabbitmq_host: str = Field(default="rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default="admin", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(default="admin", alias="RABBITMQ_PASSWORD")
    rabbitmq_queue: str = Field(
        default="aam.dialogue.archive", alias="RABBITMQ_QUEUE"
    )
    rabbitmq_exchange: str = Field(
        default="aam.exchange", alias="RABBITMQ_EXCHANGE"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def rabbitmq_url(self) -> str:
        """構建 RabbitMQ 連接 URL"""
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )


class RedisSettings(BaseSettings):
    """Redis 配置"""
    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def redis_url(self) -> str:
        """構建 Redis 連接 URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class ModelServiceSettings(BaseSettings):
    """統一模型服務配置"""
    provider_type: str = Field(
        default="ollama",
        alias="MODEL_PROVIDER_TYPE",
        description="模型服務提供商類型（ollama, vllm, openai, anthropic, custom）"
    )
    model_name: Optional[str] = Field(
        default=None,
        alias="MODEL_NAME",
        description="模型名稱（可选，如果未指定则从配置文件获取默认模型）"
    )
    model_config_path: Optional[str] = Field(
        default=None,
        alias="MODEL_CONFIG_PATH",
        description="模型配置文件路径（默认：config/models.json）"
    )
    api_base_url: Optional[str] = Field(
        default=None,
        alias="MODEL_API_BASE_URL",
        description="API 基礎 URL（通用）"
    )
    api_key: Optional[str] = Field(
        default=None,
        alias="MODEL_API_KEY",
        description="API 密鑰（如果需要）"
    )
    timeout: int = Field(
        default=120,
        alias="MODEL_TIMEOUT",
        description="請求超時時間（秒）"
    )
    
    # vLLM 特定配置（可選）
    vllm_api_base_url: Optional[str] = Field(
        default=None,
        alias="VLLM_API_BASE_URL",
        description="vLLM API 基礎 URL"
    )
    
    # OpenAI 特定配置（可選）
    openai_api_base_url: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_BASE_URL",
        description="OpenAI API 基礎 URL"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="OpenAI API 密鑰"
    )
    
    # Qwen 特定配置（移除硬編碼的API Key）
    qwen_api_base_url: Optional[str] = Field(
        default="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        alias="QWEN_API_BASE_URL",
        description="Qwen API 基礎 URL"
    )
    qwen_api_key: Optional[str] = Field(
        default=None,  # 改為None，必須從環境變量讀取
        alias="QWEN_API_KEY",
        description="Qwen API 密鑰（必須設置，通過環境變量QWEN_API_KEY）"
    )
    qwen_model_name: Optional[str] = Field(
        default="qwen-turbo",
        alias="QWEN_MODEL_NAME",
        description="Qwen 模型名稱"
    )
    qwen_timeout: int = Field(
        default=120,
        alias="QWEN_TIMEOUT",
        description="Qwen 請求超時時間（秒）"
    )
    
    # Gemini 特定配置
    gemini_api_base_url: Optional[str] = Field(
        default="https://generativelanguage.googleapis.com/v1beta",
        alias="GEMINI_API_BASE_URL",
        description="Gemini API 基礎 URL"
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        alias="GEMINI_API_KEY",
        description="Gemini API 密鑰（必須設置，通過環境變量GEMINI_API_KEY）"
    )
    gemini_model_name: Optional[str] = Field(
        default="gemini-2.5-flash",
        alias="GEMINI_MODEL_NAME",
        description="Gemini 模型名稱（如 gemini-2.5-flash, gemini-pro-latest 等）"
    )
    gemini_timeout: int = Field(
        default=120,
        alias="GEMINI_TIMEOUT",
        description="Gemini 請求超時時間（秒）"
    )
    
    # 未來MoE配置（預留）
    moe_enabled: bool = Field(
        default=False,
        alias="MOE_ENABLED",
        description="是否啟用MoE（Mixture of Experts）"
    )
    moe_providers: Optional[str] = Field(
        default=None,
        alias="MOE_PROVIDERS",
        description="MoE Provider列表（逗號分隔，如：qwen,ollama）"
    )
    moe_routing_strategy: str = Field(
        default="round_robin",
        alias="MOE_ROUTING_STRATEGY",
        description="MoE 路由策略（round_robin, load_balance, quality_based）"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("qwen_api_key")
    @classmethod
    def validate_qwen_api_key(cls, v: Optional[str], info) -> Optional[str]:
        """
        驗證Qwen API Key
        
        注意：此驗證器僅在明確使用Qwen Provider時檢查。
        實際使用時，Provider Factory會進行更嚴格的驗證。
        """
        # 如果提供了API Key但為空字符串，視為未設置
        if v == "":
            return None
        return v
    
    @property
    def provider_type_enum(self) -> ModelProviderType:
        """將字符串轉換為 ModelProviderType 枚舉"""
        try:
            return ModelProviderType(self.provider_type.lower())
        except ValueError:
            return ModelProviderType.OLLAMA  # 默認值


class AISettings(BaseSettings):
    """AI 模型配置"""
    model_name: str = Field(
        default="microsoft/DialoGPT-medium", alias="MODEL_NAME"
    )
    model_cache_dir: str = Field(default="./model_cache", alias="MODEL_CACHE_DIR")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    lora_rank: int = Field(default=8, alias="LORA_RANK")
    lora_alpha: int = Field(default=16, alias="LORA_ALPHA")
    lora_target_modules: str = Field(
        default="q_proj,v_proj", alias="LORA_TARGET_MODULES"
    )
    
    # Ollama 配置（保留以向後兼容）
    ollama_enabled: bool = Field(default=False, alias="OLLAMA_ENABLED")
    ollama_model_name: str = Field(default="llama3", alias="OLLAMA_MODEL_NAME")
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_timeout: int = Field(default=120, alias="OLLAMA_TIMEOUT")
    
    # Eb-MM 配置（Enterprise Bot mini-Model）
    eb_mm_enabled: bool = Field(
        default=False,
        alias="EB_MM_ENABLED",
        description="是否啟用 Eb-MM 模型（優先級 1）"
    )
    eb_mm_model_path: str = Field(
        default="",
        alias="EB_MM_MODEL_PATH",
        description="Eb-MM 模型路徑（基礎模型）"
    )
    eb_mm_lora_path: str = Field(
        default="",
        alias="EB_MM_LORA_PATH",
        description="Eb-MM LoRA 適配器路徑（可選）"
    )
    
    # Ollama 本地模型配置（優先級 2）
    ollama_local_model_enabled: bool = Field(
        default=False,
        alias="OLLAMA_LOCAL_MODEL_ENABLED",
        description="是否啟用 Ollama 本地模型（優先級 2）"
    )
    ollama_local_model_name: str = Field(
        default="llama3",
        alias="OLLAMA_LOCAL_MODEL_NAME",
        description="Ollama 本地模型名稱（優先級 2）"
    )
    
    # LangChain Embedding 配置（降級選項 2，保留以向後兼容）
    langchain_embedding_enabled: bool = Field(
        default=False,
        alias="LANGCHAIN_EMBEDDING_ENABLED",
        description="是否啟用 LangChain Embedding 模型（優先級 2，已棄用，使用 ollama_local_model_enabled）"
    )
    langchain_embedding_model: str = Field(
        default="gpt-3.5-turbo",
        alias="LANGCHAIN_EMBEDDING_MODEL",
        description="LangChain Embedding LLM 模型名稱（如 gpt-3.5-turbo, gpt-4 等）"
    )
    langchain_embedding_provider: str = Field(
        default="openai",
        alias="LANGCHAIN_EMBEDDING_PROVIDER",
        description="LangChain Embedding 提供商（openai, anthropic 等）"
    )
    langchain_embedding_api_key: Optional[str] = Field(
        default=None,
        alias="LANGCHAIN_EMBEDDING_API_KEY",
        description="LangChain Embedding API 密鑰（如果為 None，則從環境變量獲取）"
    )
    langchain_embedding_timeout: int = Field(
        default=120,
        alias="LANGCHAIN_EMBEDDING_TIMEOUT",
        description="LangChain Embedding 請求超時時間（秒）"
    )
    
    # LLM 抽象層配置（優先級 3）
    llm_layer_provider_type: str = Field(
        default="qwen",
        alias="LLM_LAYER_PROVIDER_TYPE",
        description="LLM 層 Provider 類型（qwen, ollama, vllm 等）"
    )
    
    # LLM 降級配置（可選，用於外部 API，優先級 3，保留以向後兼容）
    llm_fallback_enabled: bool = Field(
        default=False,
        alias="LLM_FALLBACK_ENABLED",
        description="是否啟用 LLM 降級選項（優先級 3，已棄用）"
    )
    llm_provider: str = Field(
        default="openai",
        alias="LLM_PROVIDER",
        description="LLM 提供商（openai, anthropic 等，已棄用，使用 llm_layer_provider_type）"
    )
    llm_model_name: str = Field(
        default="gpt-3.5-turbo",
        alias="LLM_MODEL_NAME",
        description="LLM 模型名稱（已棄用）"
    )
    
    # 質量評估配置
    quality_threshold: float = Field(
        default=0.7,
        alias="QUALITY_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="質量閾值（0.0-1.0），低於此值將觸發降級"
    )
    quality_evaluation_enabled: bool = Field(
        default=True,
        alias="QUALITY_EVALUATION_ENABLED",
        description="是否啟用質量評估"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def lora_target_modules_list(self) -> list[str]:
        """將逗號分隔的字符串轉換為列表"""
        return [m.strip() for m in self.lora_target_modules.split(",")]


class SecuritySettings(BaseSettings):
    """安全配置"""
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    # JWT Token 配置（用於 MCP Server）
    token_expire_hours: int = Field(
        default=24, alias="TOKEN_EXPIRE_HOURS", description="Token 有效期（小時）"
    )
    token_issuer: str = Field(
        default="aam-agent", alias="TOKEN_ISSUER", description="Token 發行者標識"
    )
    enable_user_id_validation: bool = Field(
        default=True,
        alias="ENABLE_USER_ID_VALIDATION",
        description="是否啟用 user_id 驗證",
    )
    # 企業級認證配置（用於服務器間相互認證）
    enterprise_secret_key: Optional[str] = Field(
        default=None,
        alias="ENTERPRISE_SECRET_KEY",
        description="企業 Secret Key（用於服務器間相互認證，如 SmartQ）",
    )
    enable_enterprise_auth: bool = Field(
        default=False,
        alias="ENABLE_ENTERPRISE_AUTH",
        description="是否啟用企業級認證（服務器間相互認證）",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY 必須設置且不能使用默認值")
        return v


class TrainingSettings(BaseSettings):
    """LoRA 训练配置"""
    training_enabled: bool = Field(
        default=False,
        alias="TRAINING_ENABLED",
        description="是否启用训练"
    )
    training_data_export_days: int = Field(
        default=7,
        alias="TRAINING_DATA_EXPORT_DAYS",
        ge=1,
        description="导出过去 N 天的数据"
    )
    training_quality_threshold: float = Field(
        default=0.0,
        alias="TRAINING_QUALITY_THRESHOLD",
        ge=0.0,
        le=1.0,
        description="数据质量阈值"
    )
    training_output_dir: str = Field(
        default="./models",
        alias="TRAINING_OUTPUT_DIR",
        description="训练输出目录"
    )
    base_model_name: str = Field(
        default="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        alias="BASE_MODEL_NAME",
        description="基础模型名称"
    )
    lora_rank: int = Field(
        default=8,
        alias="LORA_RANK",
        ge=1,
        description="LoRA rank 参数"
    )
    lora_alpha: int = Field(
        default=16,
        alias="LORA_ALPHA",
        ge=1,
        description="LoRA alpha 参数"
    )
    lora_target_modules: str = Field(
        default="q_proj,v_proj",
        alias="LORA_TARGET_MODULES",
        description="LoRA target modules（逗号分隔）"
    )
    lora_dropout: float = Field(
        default=0.1,
        alias="LORA_DROPOUT",
        ge=0.0,
        le=1.0,
        description="LoRA dropout 参数"
    )
    training_batch_size: int = Field(
        default=4,
        alias="TRAINING_BATCH_SIZE",
        ge=1,
        description="训练批次大小"
    )
    training_learning_rate: float = Field(
        default=2e-4,
        alias="TRAINING_LEARNING_RATE",
        gt=0.0,
        description="学习率"
    )
    training_num_epochs: int = Field(
        default=3,
        alias="TRAINING_NUM_EPOCHS",
        ge=1,
        description="训练轮数"
    )
    model_storage_type: Literal["local", "s3"] = Field(
        default="local",
        alias="MODEL_STORAGE_TYPE",
        description="模型存储类型（local 或 s3）"
    )
    s3_bucket_name: Optional[str] = Field(
        default=None,
        alias="S3_BUCKET_NAME",
        description="S3 存储桶名称（可选）"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def lora_target_modules_list(self) -> list[str]:
        """將逗號分隔的字符串轉換為列表"""
        return [m.strip() for m in self.lora_target_modules.split(",")]


class Settings(BaseSettings):
    """統一配置類，聚合所有配置組"""

    app: AppSettings = Field(default_factory=AppSettings)
    api: APISettings = Field(default_factory=APISettings)
    chromadb: ChromaDBSettings = Field(default_factory=ChromaDBSettings)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ai: AISettings = Field(default_factory=AISettings)
    model_service: ModelServiceSettings = Field(default_factory=ModelServiceSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    training: TrainingSettings = Field(default_factory=TrainingSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """獲取配置實例（單例模式）"""
    return Settings()

