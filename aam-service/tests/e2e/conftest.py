"""
@purpose: E2E 測試配置和 Fixture
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-13
"""
import os
import time
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock

from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.pg_persona_store import PgPersonaStore
from src.infrastructure.ai.embedding_service import EmbeddingService
from src.config.settings import get_settings, ChromaDBSettings


def is_running_in_docker() -> bool:
    """
    檢測是否在 Docker 容器內運行
    
    Returns:
        bool: 如果在 Docker 容器內返回 True，否則返回 False
    """
    # 方法1: 檢查 /.dockerenv 文件
    if os.path.exists("/.dockerenv"):
        return True
    
    # 方法2: 檢查環境變量
    if os.environ.get("DOCKER_CONTAINER") == "true":
        return True
    
    # 方法3: 檢查 cgroup（Linux 容器）
    try:
        with open("/proc/self/cgroup", "r") as f:
            content = f.read()
            if "docker" in content or "containerd" in content:
                return True
    except (FileNotFoundError, PermissionError):
        pass
    
    return False


@pytest.fixture(scope="session")
def test_settings():
    """
    測試配置
    
    自動檢測運行環境：
    - Docker 容器內：使用服務名（chromadb, postgres）和容器內端口
    - 宿主机：使用 localhost 和映射端口
    """
    in_docker = is_running_in_docker()
    
    if in_docker:
        # Docker 容器內：使用服務名連接
        return {
            "chromadb_host": os.getenv("CHROMADB_HOST", "chromadb"),
            "chromadb_port": int(os.getenv("CHROMADB_PORT", "8000")),  # 容器內端口
            "postgres_host": os.getenv("POSTGRES_HOST", "postgres"),
            "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
            "postgres_db": os.getenv("POSTGRES_DB", "aam_personas"),
            "postgres_user": os.getenv("POSTGRES_USER", "aam_user"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD", "aam_password"),
        }
    else:
        # 宿主机：使用 localhost 和映射端口
        return {
            "chromadb_host": os.getenv("CHROMADB_HOST", "localhost"),
            "chromadb_port": int(os.getenv("CHROMADB_PORT", "8001")),  # Docker 映射端口
            "postgres_host": os.getenv("POSTGRES_HOST", "localhost"),
            "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
            "postgres_db": os.getenv("POSTGRES_DB", "aam_personas"),
            "postgres_user": os.getenv("POSTGRES_USER", "aam_user"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD", "aam_password"),
        }


@pytest_asyncio.fixture(scope="function")
async def knowledge_store(test_settings) -> AsyncGenerator[ChromaKnowledgeStore, None]:
    """
    創建測試用的 ChromaDB 知識庫
    
    注意: 使用獨立的 collection 名稱，確保測試隔離
    """
    from chromadb import HttpClient
    
    # 使用測試專用的 collection 名稱
    collection_name = f"test_knowledge_{os.getpid()}"
    
    # 創建 ChromaDB 客戶端
    from chromadb import HttpClient
    client = HttpClient(
        host=test_settings["chromadb_host"],
        port=test_settings["chromadb_port"],
    )
    
    # 創建 EmbeddingService
    embedding_service = EmbeddingService()
    
    # 創建測試專用的 ChromaDB 設置（使用 test_settings 的值）
    chromadb_settings = ChromaDBSettings(
        chromadb_host=test_settings["chromadb_host"],
        chromadb_port=test_settings["chromadb_port"],
        chromadb_collection_name=collection_name,
    )
    
    # 創建 ChromaKnowledgeStore（使用測試設置）
    store = ChromaKnowledgeStore(
        chromadb_settings=chromadb_settings,
        embedding_service=embedding_service,
    )
    
    yield store
    
    # 清理: 刪除測試 collection
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def persona_store(test_settings) -> AsyncGenerator[PgPersonaStore, None]:
    """
    創建測試用的 PostgreSQL 用戶畫像存儲
    
    注意: 使用測試數據庫，確保測試隔離
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy import text
    
    # 構建 PostgreSQL 異步 URL
    postgres_url = (
        f"postgresql+asyncpg://{test_settings['postgres_user']}:"
        f"{test_settings['postgres_password']}@"
        f"{test_settings['postgres_host']}:{test_settings['postgres_port']}/"
        f"{test_settings['postgres_db']}"
    )
    
    # 創建測試專用的引擎
    engine = create_async_engine(postgres_url, echo=False)
    
    # 創建 PgPersonaStore
    store = PgPersonaStore(engine=engine)
    
    # 清理測試數據（測試前）
    async with AsyncSession(engine) as session:
        await session.execute(
            text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%'")
        )
        await session.commit()
    
    yield store
    
    # 清理: 刪除測試數據（測試後）
    try:
        async with AsyncSession(engine) as session:
            await session.execute(
                text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%'")
            )
            await session.commit()
        await store.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def analysis_model():
    """
    創建測試用的分析模型
    
    可以使用 Mock 模型（快速）或真實模型（完整驗證）
    """
    # 使用 Mock 模型進行快速測試
    # 如果需要真實模型測試，可以替換為 FallbackAnalysisModel
    return MockAnalysisModel()


@pytest.fixture(scope="function")
def memory_service(
    knowledge_store,
    persona_store,
    analysis_model,
) -> MemoryServiceImpl:
    """
    創建測試用的記憶服務實例
    """
    return MemoryServiceImpl(
        knowledge_store=knowledge_store,
        persona_store=persona_store,
        analysis_model=analysis_model,
    )


@pytest.fixture(scope="function")
def mock_analysis_model_with_results():
    """
    創建模擬分析模型，返回預設的結果
    
    用於驗證存儲邏輯，不依賴真實的 AI 模型
    """
    from src.models.domain.database import KnowledgeAsset
    from src.models.domain.personality import PersonalityInsights
    
    model = Mock()
    
    # 模擬 extract_knowledge
    async def mock_extract_knowledge(text: str, user_id: str, session_id: str):
        # 使用當前時間戳確保唯一性（每次調用都不同）
        current_timestamp = int(time.time() * 1000)  # 使用毫秒級時間戳確保唯一性
        
        # 根據文本內容返回不同的結果
        if "Python" in text:
            return KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=current_timestamp,
                source_type="dialogue",
                entities=["Python", "Guido van Rossum", "Django", "Flask"],
                triples_json='[{"subject": "Python", "predicate": "创建者", "object": "Guido van Rossum"}]',
            )
        elif "AI 项目" in text:
            return KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=current_timestamp,
                source_type="dialogue",
                entities=["AI 项目", "Apache Spark", "Hadoop"],
                triples_json='[{"subject": "AI 项目", "predicate": "需要", "object": "数据准备"}]',
            )
        else:
            return KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=current_timestamp,
                source_type="dialogue",
                entities=["今天", "公园"],
                triples_json='[{"subject": "用户", "predicate": "计划", "object": "去公园"}]',
            )
    
    # 模擬 analyze_personality
    async def mock_analyze_personality(text: str):
        if "Python" in text or "AI" in text:
            return PersonalityInsights(
                user_id="",
                style_tags={"technical": 9, "formal": 8},  # 使用整數
                sentiment="positive",
                language_patterns=["专业", "详细"],
                confidence_score=0.85,
            )
        else:
            return PersonalityInsights(
                user_id="",
                style_tags={"casual": 9, "friendly": 8},  # 使用整數
                sentiment="positive",
                language_patterns=["轻松", "友好"],
                confidence_score=0.75,
            )
    
    model.extract_knowledge = AsyncMock(side_effect=mock_extract_knowledge)
    model.analyze_personality = AsyncMock(side_effect=mock_analyze_personality)
    model.check_available = AsyncMock(return_value=True)
    
    return model

