"""
@purpose: 數據庫基礎設施模塊導出和連接管理
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import ChromaDBSettings, PostgresSettings, get_settings
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.models import Base, UserProfileTable
from src.infrastructure.database.pg_persona_store import PgPersonaStore


def create_chromadb_client(
    settings: Optional[ChromaDBSettings] = None,
) -> chromadb.HttpClient:
    """
    創建 ChromaDB 客戶端
    
    Args:
        settings: ChromaDB 配置設置，如果為 None 則從全局配置加載
        
    Returns:
        ChromaDB HTTP 客戶端實例
    """
    if settings is None:
        settings = get_settings().chromadb
    
    return chromadb.HttpClient(
        host=settings.chromadb_host,
        port=settings.chromadb_port,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )


def create_postgres_engine(
    settings: Optional[PostgresSettings] = None,
    pool_size: int = 10,
    max_overflow: int = 20,
) -> AsyncEngine:
    """
    創建 PostgreSQL 異步引擎
    
    Args:
        settings: PostgreSQL 配置設置，如果為 None 則從全局配置加載
        pool_size: 連接池大小
        max_overflow: 最大溢出連接數
        
    Returns:
        SQLAlchemy 異步引擎實例
    """
    if settings is None:
        settings = get_settings().postgres
    
    return create_async_engine(
        settings.postgres_async_url,
        echo=False,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )


def create_postgres_session(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """
    創建 PostgreSQL 異步會話工廠
    
    Args:
        engine: SQLAlchemy 異步引擎
        
    Returns:
        異步會話工廠
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


__all__ = [
    # 數據庫模型
    "Base",
    "UserProfileTable",
    # Store 實現
    "ChromaKnowledgeStore",
    "PgPersonaStore",
    # 連接工廠函數
    "create_chromadb_client",
    "create_postgres_engine",
    "create_postgres_session",
]

