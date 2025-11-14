"""
@purpose: 實現 PostgreSQL 用戶畫像存儲，封裝關係數據庫的存取邏輯
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import PostgresSettings, get_settings
from src.core.interfaces.i_persona_store import IPersonaStore
from src.infrastructure.database.models import UserProfileTable
from src.models.domain.database import UserProfileDB


class PgPersonaStore(IPersonaStore):
    """PostgreSQL 用戶畫像存儲實現"""

    def __init__(
        self,
        postgres_settings: PostgresSettings | None = None,
        engine: AsyncEngine | None = None,
    ):
        """
        初始化 PostgreSQL 用戶畫像存儲
        
        Args:
            postgres_settings: PostgreSQL 配置設置，如果為 None 則從全局配置加載
            engine: SQLAlchemy 異步引擎，如果為 None 則創建新實例
        """
        if postgres_settings is None:
            postgres_settings = get_settings().postgres
        
        self.settings = postgres_settings
        
        if engine is None:
            self.engine = create_async_engine(
                self.settings.postgres_async_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
            )
        else:
            self.engine = engine
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


    async def save_or_update(self, profile: UserProfileDB) -> None:
        """
        保存或更新用戶畫像
        
        Args:
            profile: 用戶畫像數據庫模型
        """
        async with self.async_session_maker() as session:
            # 檢查記錄是否存在
            stmt = select(UserProfileTable).where(
                UserProfileTable.user_id == profile.user_id
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            # 更新 last_updated 時間戳
            profile.last_updated = datetime.utcnow()
            
            if existing:
                # 更新現有記錄
                update_stmt = (
                    update(UserProfileTable)
                    .where(UserProfileTable.user_id == profile.user_id)
                    .values(
                        style_tags=profile.style_tags,
                        sentiment_history=profile.sentiment_history,
                        last_updated=profile.last_updated,
                    )
                )
                await session.execute(update_stmt)
            else:
                # 創建新記錄
                new_record = UserProfileTable.from_domain_model(profile)
                session.add(new_record)
            
            await session.commit()

    async def get(self, user_id: str) -> Optional[UserProfileDB]:
        """
        獲取用戶畫像
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶畫像對象，如果不存在則返回 None
        """
        async with self.async_session_maker() as session:
            stmt = select(UserProfileTable).where(
                UserProfileTable.user_id == user_id
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            
            if record is None:
                return None
            
            return record.to_domain_model()

    async def close(self) -> None:
        """
        關閉數據庫連接
        """
        await self.engine.dispose()

