"""
@purpose: 数据库连接管理
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from typing import Optional, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import get_settings

settings = get_settings()

# 同步引擎（用于 Alembic 迁移）
sync_engine = create_engine(
    settings.database.database_url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
)

# 同步会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_db() -> Session:
    """
    获取数据库会话（依赖注入）
    用于 FastAPI 路由
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 异步引擎（如果需要异步操作，延迟创建）
async_engine: Optional[Any] = None
AsyncSessionLocal: Optional[Any] = None


def _init_async_engine():
    """延迟初始化异步引擎（仅在需要时）"""
    global async_engine, AsyncSessionLocal
    if async_engine is None:
        try:
            async_database_url = settings.database.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
            async_engine = create_async_engine(
                async_database_url,
                echo=settings.database.echo,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
            )
            AsyncSessionLocal = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        except ImportError:
            # asyncpg 未安装，跳过异步引擎初始化
            pass


async def get_async_db() -> AsyncSession:
    """
    获取异步数据库会话（依赖注入）
    用于 FastAPI 异步路由
    """
    _init_async_engine()
    if AsyncSessionLocal is None:
        raise RuntimeError("异步数据库引擎未初始化，请安装 asyncpg")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
