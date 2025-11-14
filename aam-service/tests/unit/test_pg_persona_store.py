"""
@purpose: 測試 PostgreSQL 用戶畫像存儲的保存和查詢功能
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

# 測試 PgPersonaStore 需要 SQLAlchemy，如果沒有安裝則跳過
try:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
    from src.config.settings import PostgresSettings
    from src.infrastructure.database.pg_persona_store import PgPersonaStore
    from src.infrastructure.database.models import UserProfileTable
    from src.models.domain.database import UserProfileDB
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="SQLAlchemy not available")


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not available")
class TestPgPersonaStore:
    """測試 PgPersonaStore 類"""

    @pytest.fixture
    def mock_engine(self):
        """創建模擬異步引擎"""
        engine = Mock(spec=AsyncEngine)
        return engine

    @pytest.fixture
    def mock_session(self):
        """創建模擬異步會話"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def user_profile(self):
        """創建測試用的用戶畫像"""
        return UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )

    @patch("src.infrastructure.database.pg_persona_store.create_async_engine")
    def test_init(self, mock_create_engine, mock_engine):
        """測試初始化"""
        mock_create_engine.return_value = mock_engine
        
        settings = PostgresSettings(
            postgres_host="localhost",
            postgres_port=5432,
            postgres_db="test_db",
            postgres_user="test_user",
            postgres_password="test_password",
        )
        
        store = PgPersonaStore(postgres_settings=settings)
        
        assert store.settings == settings
        assert store.engine == mock_engine

    @pytest.mark.asyncio
    async def test_save_or_update_new_record(self, mock_session, user_profile):
        """測試保存新記錄"""
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.add = Mock()
        
        # 模擬查詢返回 None（記錄不存在）
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        store = PgPersonaStore()
        store.async_session_maker = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aenter__ = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # 使用 context manager
        async with store.async_session_maker() as session:
            await store.save_or_update(user_profile)
        
        # 驗證 add 被調用（創建新記錄）
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_or_update_existing_record(self, mock_session, user_profile):
        """測試更新現有記錄"""
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        
        # 模擬查詢返回現有記錄
        existing_record = UserProfileTable.from_domain_model(user_profile)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_record
        mock_session.execute.return_value = mock_result
        
        store = PgPersonaStore()
        store.async_session_maker = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aenter__ = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # 使用 context manager
        async with store.async_session_maker() as session:
            await store.save_or_update(user_profile)
        
        # 驗證 execute 被調用（更新操作）
        assert mock_session.execute.call_count >= 1
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_existing_user(self, mock_session, user_profile):
        """測試獲取現有用戶畫像"""
        existing_record = UserProfileTable.from_domain_model(user_profile)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_record
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        store = PgPersonaStore()
        store.async_session_maker = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aenter__ = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await store.get("user123")
        
        assert result is not None
        assert result.user_id == "user123"
        assert result.style_tags == user_profile.style_tags

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, mock_session):
        """測試獲取不存在的用戶畫像"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        store = PgPersonaStore()
        store.async_session_maker = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aenter__ = Mock(return_value=mock_session)
        store.async_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await store.get("nonexistent_user")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_close(self, mock_engine):
        """測試關閉數據庫連接"""
        store = PgPersonaStore()
        store.engine = mock_engine
        mock_engine.dispose = AsyncMock()
        
        await store.close()
        
        mock_engine.dispose.assert_called_once()

