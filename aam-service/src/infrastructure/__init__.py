"""
@purpose: 基礎設施模塊統一導出入口
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
# AI 服務 - 使用延遲導入避免在測試環境中直接導入未安裝的依賴
try:
    from src.infrastructure.ai.embedding_service import EmbeddingService
    _AI_AVAILABLE = True
except ImportError:
    # 在測試環境中，某些依賴可能未安裝
    _AI_AVAILABLE = False
    EmbeddingService = None

# 數據庫服務 - 使用延遲導入避免在測試環境中直接導入未安裝的依賴
try:
    from src.infrastructure.database.models import Base, UserProfileTable
    from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
    from src.infrastructure.database.pg_persona_store import PgPersonaStore
    from src.infrastructure.database import (
        create_chromadb_client,
        create_postgres_engine,
        create_postgres_session,
    )
    _DATABASE_AVAILABLE = True
except ImportError:
    # 在測試環境中，某些依賴可能未安裝
    _DATABASE_AVAILABLE = False
    Base = None
    UserProfileTable = None
    ChromaKnowledgeStore = None
    PgPersonaStore = None
    create_chromadb_client = None
    create_postgres_engine = None
    create_postgres_session = None

__all__ = [
    # AI 服務（如果可用）
    *(["EmbeddingService"] if _AI_AVAILABLE else []),
    # 數據庫模型（如果可用）
    *(["Base", "UserProfileTable", "ChromaKnowledgeStore", "PgPersonaStore",
       "create_chromadb_client", "create_postgres_engine", "create_postgres_session"] if _DATABASE_AVAILABLE else []),
]

