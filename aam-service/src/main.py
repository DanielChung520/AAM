"""
@purpose: FastAPI 應用程序入口文件，包含基礎路由、健康檢查、異常處理和應用生命週期管理
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from src.core.interfaces.i_analysis_model import IAnalysisModel

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.langchain_embedding_model import LangChainEmbeddingModel
from src.infrastructure.database import (
    ChromaKnowledgeStore,
    PgPersonaStore,
    create_chromadb_client,
    create_postgres_engine,
    create_postgres_session,
)
from src.infrastructure.messaging import DialogueArchiveConsumer, RabbitMQConnection
from src.api.controllers.mcp_controller import router as mcp_router
from src.api.controllers.token_controller import router as token_router

# 配置結構化日誌
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

# 配置 Python 标准库 logging（structlog 需要）
# 这确保 structlog 的日志能够输出到 stdout
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=getattr(logging, settings.app.log_level.upper(), logging.INFO),
    force=True,  # 强制重新配置，即使已经配置过
)

# 全局變量，用於存儲消費者實例
consumer: Optional[DialogueArchiveConsumer] = None
consumer_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    應用程序生命週期管理
    處理啟動和關閉事件
    """
    global consumer, consumer_task

    # 啟動事件
    logger.info(
        "應用程序啟動",
        app_name=settings.app.app_name,
        version=settings.app.app_version,
        debug=settings.app.debug,
    )

    try:
        # 初始化數據庫連接（使用重試機制）
        import time
        max_retries = 5
        retry_delay = 2
        
        chromadb_client = None
        chromadb_connected = False
        chromadb_settings = settings.chromadb
        logger.info(
            "開始初始化 ChromaDB 連接",
            host=chromadb_settings.chromadb_host,
            port=chromadb_settings.chromadb_port,
            url=chromadb_settings.chromadb_url,
            max_retries=max_retries,
        )
        for attempt in range(max_retries):
            try:
                chromadb_client = create_chromadb_client()
                # 測試連接是否真的可用
                identity = chromadb_client.get_user_identity()
                logger.info(
                    f"ChromaDB 連接成功（嘗試 {attempt + 1}/{max_retries}）",
                    tenant=identity.tenant,
                    databases=identity.databases,
                )
                chromadb_connected = True
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"ChromaDB 連接失敗（嘗試 {attempt + 1}/{max_retries}），{retry_delay} 秒後重試",
                        error=str(e),
                        error_type=type(e).__name__,
                        exc_info=e,
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"ChromaDB 連接失敗，已重試 {max_retries} 次",
                        error=str(e),
                        error_type=type(e).__name__,
                        host=chromadb_settings.chromadb_host,
                        port=chromadb_settings.chromadb_port,
                        exc_info=e,
                    )
                    # 不抛出異常，繼續使用降級模式
                    chromadb_client = None
                    chromadb_connected = False
        
        postgres_engine = create_postgres_engine()
        postgres_session = create_postgres_session(postgres_engine)

        # 創建 Store 實例（如果 ChromaDB 連接成功）
        knowledge_store = None
        if chromadb_connected:
            try:
                logger.info("開始創建 ChromaKnowledgeStore 實例")
                knowledge_store = ChromaKnowledgeStore()
                # 驗證集合是否存在或可以創建
                collection_name = chromadb_settings.chromadb_collection_name
                logger.info(
                    "ChromaKnowledgeStore 創建成功",
                    collection_name=collection_name,
                )
            except Exception as e:
                logger.warning(
                    "ChromaKnowledgeStore 創建失敗，將使用 MockKnowledgeStore",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=e,
                )
                knowledge_store = None
        else:
            # ChromaDB 連接失敗，使用 MockKnowledgeStore
            from src.infrastructure.database.mock_knowledge_store import MockKnowledgeStore
            knowledge_store = MockKnowledgeStore()
            logger.warning(
                "使用 MockKnowledgeStore（ChromaDB 連接失敗）",
                reason="ChromaDB 連接失敗，應用將在降級模式下運行",
            )
        
        logger.info(
            "準備創建 persona_store",
            postgres_host=settings.postgres.postgres_host,
            postgres_port=settings.postgres.postgres_port,
            postgres_db=settings.postgres.postgres_db,
        )
        try:
            persona_store = PgPersonaStore(engine=postgres_engine)
            logger.info("persona_store 創建成功")
        except Exception as e:
            logger.error(
                "persona_store 創建失敗",
                error=str(e),
                error_type=type(e).__name__,
                postgres_host=settings.postgres.postgres_host,
                postgres_port=settings.postgres.postgres_port,
                exc_info=e,
            )
            raise

        # 創建質量評估器
        quality_evaluator = QualityEvaluator(
            quality_threshold=settings.ai.quality_threshold
        )
        logger.info(
            "質量評估器已初始化",
            quality_threshold=settings.ai.quality_threshold,
            quality_evaluation_enabled=settings.ai.quality_evaluation_enabled,
        )

        # 創建降級策略分析模型
        # 初始時，三個層級模型都設置為 None（後續批次填充）
        # 如果所有模型都不可用，FallbackAnalysisModel 會返回空結果
        eb_mm_model: Optional[IAnalysisModel] = None
        ollama_local_model: Optional[IAnalysisModel] = None
        llm_model: Optional[IAnalysisModel] = None

        # 嘗試創建 EB-mM 模型（優先級 1）
        if settings.ai.eb_mm_enabled:
            try:
                model_service_config = settings.model_service
                provider_type = model_service_config.provider_type_enum
                
                # 確定 EB-mM 模型名稱
                # 優先使用 eb_mm_model_path，否則使用 model_service.model_name，最後使用默認值
                eb_mm_model_name = (
                    settings.ai.eb_mm_model_path 
                    if settings.ai.eb_mm_model_path 
                    else (model_service_config.model_name or "deepseek-r1:8b")
                )
                
                api_base_url = model_service_config.api_base_url or settings.ai.ollama_base_url
                
                # 使用 Provider 工廠創建 Provider（用於 EB-mM）
                eb_mm_provider = ModelProviderFactory.create_provider(
                    provider_type=provider_type,
                    model_name=eb_mm_model_name,
                    api_base_url=api_base_url,
                    timeout=model_service_config.timeout,
                    ollama_base_url=settings.ai.ollama_base_url,
                    ollama_timeout=settings.ai.ollama_timeout,
                )
                
                # 創建統一模型服務（用於 EB-mM）
                eb_mm_unified_service = UnifiedModelService(provider=eb_mm_provider)
                
                # 創建 EB-mM 業務邏輯層
                from src.infrastructure.ai.eb_mm_analysis_model import EbMMAnalysisModel
                eb_mm_model = EbMMAnalysisModel(unified_model_service=eb_mm_unified_service)
                
                logger.info(
                    "EB-mM 模型已創建並配置為優先級 1",
                    extra={
                        "provider_type": provider_type.value,
                        "model_name": eb_mm_model_name,
                        "lora_path": settings.ai.eb_mm_lora_path or "未配置",
                    },
                )
            except Exception as e:
                logger.warning(
                    f"創建 EB-mM 模型失敗: {e}",
                    extra={"error": str(e)},
                )
                eb_mm_model = None

        # 嘗試創建 Ollama 本地模型（優先級 2）
        if settings.ai.ollama_local_model_enabled:
            try:
                model_service_config = settings.model_service
                # 使用 Ollama Provider
                ollama_local_provider = ModelProviderFactory.create_provider(
                    provider_type=ModelProviderType.OLLAMA,
                    model_name=settings.ai.ollama_local_model_name,
                    api_base_url=settings.ai.ollama_base_url,
                    timeout=model_service_config.timeout,
                    ollama_base_url=settings.ai.ollama_base_url,
                    ollama_timeout=settings.ai.ollama_timeout,
                )
                
                # 創建統一模型服務（用於 Ollama 本地模型）
                ollama_local_unified_service = UnifiedModelService(provider=ollama_local_provider)
                
                # 將統一模型服務作為 Ollama 本地模型層級（優先級 2）
                ollama_local_model = ollama_local_unified_service
                
                logger.info(
                    "Ollama 本地模型已創建並配置為優先級 2",
                    extra={
                        "model_name": settings.ai.ollama_local_model_name,
                        "base_url": settings.ai.ollama_base_url,
                    },
                )
            except Exception as e:
                logger.warning(
                    f"創建 Ollama 本地模型失敗: {e}",
                    extra={"error": str(e)},
                )
                ollama_local_model = None

        # 嘗試創建 LLM 抽象層（優先級 3）
        try:
            model_service_config = settings.model_service
            
            # 根據配置選擇 LLM 層 Provider 類型
            llm_layer_provider_type_str = settings.ai.llm_layer_provider_type.lower()
            try:
                llm_layer_provider_type = ModelProviderType(llm_layer_provider_type_str)
            except ValueError:
                logger.warning(
                    f"無效的 LLM 層 Provider 類型: {llm_layer_provider_type_str}，使用默認值 qwen"
                )
                llm_layer_provider_type = ModelProviderType.QWEN
            
            # 使用配置适配器获取Provider配置（实现真正的抽象层）
            from src.config.provider_config_adapter import ProviderConfigAdapter
            
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=llm_layer_provider_type,
                config=model_service_config
            )
            
            # Factory只接收通用参数，不关心Provider特定配置
            provider = ModelProviderFactory.create_provider(
                provider_type=llm_layer_provider_type,
                **provider_config
            )
            
            # 創建統一模型服務
            unified_service = UnifiedModelService(provider=provider)
            
            # 將統一模型服務作為 LLM 抽象層（優先級 3）
            llm_model = unified_service
            logger.info(
                "LLM 抽象層已創建並配置為優先級 3",
                extra={
                    "provider_type": llm_layer_provider_type.value,
                    "model_name": provider_config.get("model_name"),
                },
            )
        except Exception as e:
            logger.warning(
                f"創建 LLM 抽象層失敗: {e}，將使用 MockAnalysisModel",
                extra={"error": str(e)},
            )
            # 如果創建失敗，使用 MockAnalysisModel 作為臨時占位符
            llm_model = None

        # 如果所有模型都不可用，使用 MockAnalysisModel 作為臨時占位符
        # 這樣可以確保系統在沒有真實模型時仍能運行
        if (
            eb_mm_model is None
            and ollama_local_model is None
            and llm_model is None
        ):
            logger.warning(
                "所有模型層級都未配置，使用 MockAnalysisModel 作為臨時占位符"
            )
            # 將 MockAnalysisModel 作為 LLM 層級的占位符
            llm_model = MockAnalysisModel()

        analysis_model = FallbackAnalysisModel(
            eb_mm_model=eb_mm_model,
            ollama_local_model=ollama_local_model,
            llm_model=llm_model,
            quality_evaluator=quality_evaluator,
            settings=settings.ai,
        )
        logger.info("降級策略分析模型已初始化")

        # 創建記憶服務實例
        logger.info("準備創建 memory_service")
        try:
            memory_service = MemoryServiceImpl(
                knowledge_store=knowledge_store,
                persona_store=persona_store,
                analysis_model=analysis_model,
            )
            logger.info("memory_service 實例創建成功")

            # 將記憶服務存儲到 app.state，供依賴注入使用
            app.state.memory_service = memory_service
            logger.info("記憶服務已初始化並存儲到 app.state")
        except Exception as e:
            logger.error(f"創建 memory_service 失敗: {e}", exc_info=e)
            raise

        # 初始化 RabbitMQ 連接
        rabbitmq_connection = RabbitMQConnection(settings.rabbitmq)

        # 創建對話歸檔消費者
        consumer = DialogueArchiveConsumer(
            memory_service=memory_service,
            rabbitmq_connection=rabbitmq_connection,
        )

        # 啟動消費者（在后台任務中運行）
        consumer_task = asyncio.create_task(consumer.start_consuming())

        logger.info("對話歸檔消費者已啟動")

    except Exception as e:
        logger.error(
            "初始化服務時發生錯誤",
            error=str(e),
            exc_info=e,
        )
        # 如果初始化失敗，嘗試創建一個基本的 memory_service（使用 Mock）
        # 這樣可以確保 API 端點至少可以響應，即使功能受限
        try:
            logger.warning("嘗試使用 Mock 模型創建基本的記憶服務（降級模式）")
            from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
            
            # 嘗試創建 PostgreSQL 連接（如果還沒有）
            if 'postgres_engine' not in locals():
                try:
                    postgres_engine = create_postgres_engine()
                    logger.info("PostgreSQL 連接成功（降級模式）")
                except Exception as pg_error:
                    logger.warning(f"PostgreSQL 連接失敗（降級模式）: {pg_error}")
                    postgres_engine = None
            
            # 嘗試創建 Store 實例（即使 ChromaDB 失敗）
            knowledge_store = None
            persona_store = None
            
            try:
                knowledge_store = ChromaKnowledgeStore()
                logger.info("ChromaKnowledgeStore 創建成功（降級模式）")
            except Exception as chroma_error:
                logger.warning(f"ChromaKnowledgeStore 創建失敗（降級模式）: {chroma_error}")
                # 使用 MockKnowledgeStore 作為降級方案
                from src.infrastructure.database.mock_knowledge_store import MockKnowledgeStore
                knowledge_store = MockKnowledgeStore()
                logger.warning("使用 MockKnowledgeStore 作為降級方案（功能受限）")
            
            if postgres_engine:
                try:
                    persona_store = PgPersonaStore(engine=postgres_engine)
                    logger.info("PgPersonaStore 創建成功（降級模式）")
                except Exception as pg_store_error:
                    logger.warning(f"PgPersonaStore 創建失敗（降級模式）: {pg_store_error}")
                    persona_store = None
            
            # 如果 knowledge_store 或 persona_store 為 None，無法創建 MemoryServiceImpl
            # 這種情況下，我們需要跳過創建 memory_service
            if knowledge_store is None or persona_store is None:
                logger.error(
                    "無法創建記憶服務：必要的 Store 實例缺失",
                    has_knowledge_store=knowledge_store is not None,
                    has_persona_store=persona_store is not None,
                )
            else:
                # 創建基本的記憶服務（使用 Mock 分析模型）
                memory_service = MemoryServiceImpl(
                    knowledge_store=knowledge_store,
                    persona_store=persona_store,
                    analysis_model=MockAnalysisModel(),
                )
                app.state.memory_service = memory_service
                logger.warning("已創建基本的記憶服務（使用 Mock 模型），功能可能受限")
        except Exception as fallback_error:
            logger.error(
                "創建基本記憶服務也失敗",
                error=str(fallback_error),
                exc_info=fallback_error,
            )
            # 不設置 memory_service，讓依賴注入處理錯誤
        
        # 不阻止應用啟動，但記錄錯誤
        consumer = None
        consumer_task = None

    yield

    # 關閉事件
    logger.info("應用程序關閉，正在清理資源...")

    # 優雅關閉消費者
    if consumer and consumer_task:
        try:
            logger.info("正在停止對話歸檔消費者...")
            await consumer.stop_consuming(timeout=30.0)

            # 取消任務
            if not consumer_task.done():
                consumer_task.cancel()
                try:
                    await asyncio.wait_for(consumer_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("等待消費者任務完成超時")
                except asyncio.CancelledError:
                    logger.debug("消費者任務已取消")

            logger.info("對話歸檔消費者已停止")

        except Exception as e:
            logger.error(
                "關閉對話歸檔消費者時發生錯誤",
                error=str(e),
                exc_info=e,
            )

    # 關閉 RabbitMQ 連接
    if consumer and consumer.rabbitmq:
        try:
            await consumer.rabbitmq.close()
        except Exception as e:
            logger.warning("關閉 RabbitMQ 連接時發生錯誤", exc_info=e)

    logger.info("應用程序關閉完成")


# 創建 FastAPI 應用實例
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="AI-Augmented Memory (AAM) 微服務 - 提供長期記憶和上下文豐富化能力",
    debug=settings.app.debug,
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 異常處理中間件
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局異常處理器"""
    logger.error(
        "未處理的異常",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "內部服務器錯誤",
            "detail": str(exc) if settings.app.debug else "請聯繫系統管理員",
        },
    )


# 健康檢查端點
@app.get("/health", tags=["健康檢查"])
async def health_check() -> dict[str, str]:
    """
    健康檢查端點
    用於 Kubernetes/Docker 健康檢查
    """
    return {
        "status": "healthy",
        "service": settings.app.app_name,
        "version": settings.app.app_version,
    }


@app.get("/ready", tags=["健康檢查"])
async def readiness_check() -> dict[str, str]:
    """
    就緒檢查端點
    檢查所有依賴服務是否可用
    """
    # TODO: 在這裡檢查數據庫、消息隊列等服務的連接狀態
    # 例如：
    # db_status = await check_database_connection()
    # mq_status = await check_rabbitmq_connection()
    
    return {
        "status": "ready",
        "service": settings.app.app_name,
        "version": settings.app.app_version,
        # "database": db_status,
        # "message_queue": mq_status,
    }


# 根路由
@app.get("/", tags=["根"])
async def root() -> dict[str, str]:
    """根端點"""
    return {
        "message": f"歡迎使用 {settings.app.app_name}",
        "version": settings.app.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# API 路由
app.include_router(mcp_router, prefix="/v1/mcp", tags=["MCP"])
app.include_router(token_router, prefix="/v1/tokens", tags=["Tokens"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api.api_host,
        port=settings.api.api_port,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower(),
    )

