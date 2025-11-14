"""
@purpose: 測試記憶服務的核心業務邏輯實現
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.services.memory_service import MemoryServiceImpl
from src.models.api.mcp import (
    EnrichedMCP,
    PartialMCP,
    RetrievedDoc,
    SessionContext,
    UserProfile,
)
from src.models.domain.database import KnowledgeAsset, UserProfileDB
from src.models.domain.dialogue import DialogueArchiveMessage
from src.models.domain.personality import PersonalityInsights


class TestMemoryServiceImplEnrich:
    """測試 MemoryServiceImpl.enrich() 方法"""

    @pytest.fixture
    def mock_knowledge_store(self):
        """創建模擬的知識庫"""
        return Mock()

    @pytest.fixture
    def mock_persona_store(self):
        """創建模擬的用戶畫像存儲"""
        return Mock()

    @pytest.fixture
    def mock_analysis_model(self):
        """創建模擬的 AI 分析模型"""
        return Mock()

    @pytest.fixture
    def memory_service(
        self, mock_knowledge_store, mock_persona_store, mock_analysis_model
    ):
        """創建 MemoryServiceImpl 實例"""
        return MemoryServiceImpl(
            knowledge_store=mock_knowledge_store,
            persona_store=mock_persona_store,
            analysis_model=mock_analysis_model,
        )

    @pytest.fixture
    def partial_mcp(self):
        """創建測試用的 PartialMCP"""
        return PartialMCP(
            user_profile=UserProfile(user_id="user123"),
            session_context=SessionContext(
                session_id="session123",
                current_query="What is Python?",
                short_term_memory=[],
            ),
        )

    @pytest.mark.asyncio
    async def test_enrich_normal_flow(
        self, memory_service, partial_mcp, mock_knowledge_store, mock_persona_store
    ):
        """測試正常流程：並行查詢知識庫和用戶畫像"""
        # 設置 Mock 返回值
        mock_docs = [
            RetrievedDoc(
                source="chromadb:doc1", content="Python is a programming language", score=0.9
            )
        ]
        mock_knowledge_store.search = AsyncMock(return_value=mock_docs)
        
        mock_profile = UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )
        mock_persona_store.get = AsyncMock(return_value=mock_profile)
        
        # 執行測試
        result = await memory_service.enrich(partial_mcp)
        
        # 驗證結果
        assert isinstance(result, EnrichedMCP)
        assert result.user_profile.user_id == "user123"
        assert result.user_profile.long_term_style_tags == ["formal", "casual"]
        assert result.user_profile.current_sentiment == "positive"
        assert len(result.retrieved_knowledge.docs) == 1
        assert result.session_context.session_id == "session123"
        
        # 驗證方法被調用
        mock_knowledge_store.search.assert_called_once_with("What is Python?", "user123")
        mock_persona_store.get.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_enrich_empty_knowledge_results(
        self, memory_service, partial_mcp, mock_knowledge_store, mock_persona_store
    ):
        """測試知識庫返回空結果的情況"""
        mock_knowledge_store.search = AsyncMock(return_value=[])
        mock_persona_store.get = AsyncMock(return_value=None)
        
        result = await memory_service.enrich(partial_mcp)
        
        assert isinstance(result, EnrichedMCP)
        assert len(result.retrieved_knowledge.docs) == 0
        assert result.user_profile.long_term_style_tags == []
        assert result.user_profile.current_sentiment == "neutral"

    @pytest.mark.asyncio
    async def test_enrich_user_profile_not_found(
        self, memory_service, partial_mcp, mock_knowledge_store, mock_persona_store
    ):
        """測試用戶畫像不存在的情況"""
        mock_docs = [
            RetrievedDoc(
                source="chromadb:doc1", content="Some content", score=0.8
            )
        ]
        mock_knowledge_store.search = AsyncMock(return_value=mock_docs)
        mock_persona_store.get = AsyncMock(return_value=None)
        
        result = await memory_service.enrich(partial_mcp)
        
        assert isinstance(result, EnrichedMCP)
        assert result.user_profile.user_id == "user123"
        assert result.user_profile.long_term_style_tags == []
        assert result.user_profile.current_sentiment == "neutral"
        assert len(result.retrieved_knowledge.docs) == 1

    @pytest.mark.asyncio
    async def test_enrich_knowledge_store_error(
        self, memory_service, partial_mcp, mock_knowledge_store, mock_persona_store
    ):
        """測試知識庫查詢失敗的處理"""
        mock_knowledge_store.search = AsyncMock(side_effect=Exception("Database error"))
        mock_persona_store.get = AsyncMock(return_value=None)
        
        result = await memory_service.enrich(partial_mcp)
        
        # 應該返回空結果而非拋出異常
        assert isinstance(result, EnrichedMCP)
        assert len(result.retrieved_knowledge.docs) == 0

    @pytest.mark.asyncio
    async def test_enrich_persona_store_error(
        self, memory_service, partial_mcp, mock_knowledge_store, mock_persona_store
    ):
        """測試用戶畫像查詢失敗的處理"""
        mock_docs = [
            RetrievedDoc(
                source="chromadb:doc1", content="Some content", score=0.8
            )
        ]
        mock_knowledge_store.search = AsyncMock(return_value=mock_docs)
        mock_persona_store.get = AsyncMock(side_effect=Exception("Database error"))
        
        result = await memory_service.enrich(partial_mcp)
        
        # 應該返回默認用戶畫像而非拋出異常
        assert isinstance(result, EnrichedMCP)
        assert result.user_profile.long_term_style_tags == []
        assert result.user_profile.current_sentiment == "neutral"


class TestMemoryServiceImplArchive:
    """測試 MemoryServiceImpl.archive() 方法"""

    @pytest.fixture
    def mock_knowledge_store(self):
        """創建模擬的知識庫"""
        return Mock()

    @pytest.fixture
    def mock_persona_store(self):
        """創建模擬的用戶畫像存儲"""
        return Mock()

    @pytest.fixture
    def mock_analysis_model(self):
        """創建模擬的 AI 分析模型"""
        return Mock()

    @pytest.fixture
    def memory_service(
        self, mock_knowledge_store, mock_persona_store, mock_analysis_model
    ):
        """創建 MemoryServiceImpl 實例"""
        return MemoryServiceImpl(
            knowledge_store=mock_knowledge_store,
            persona_store=mock_persona_store,
            analysis_model=mock_analysis_model,
        )

    @pytest.fixture
    def dialogue_message(self):
        """創建測試用的對話歸檔消息"""
        return DialogueArchiveMessage(
            dialog_id="dialog123",
            user_id="user123",
            timestamp=datetime.utcnow(),
            turn=1,
            user_query="What is Python?",
            ai_response="Python is a programming language.",
        )

    @pytest.mark.asyncio
    async def test_archive_normal_flow(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試正常流程：並行調用 AI 模型，保存知識和更新畫像"""
        # 設置 Mock 返回值
        mock_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="dialog123",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=["Python", "programming"],
            triples_json='[{"subject": "Python", "predicate": "is", "object": "programming_language"}]',
        )
        mock_analysis_model.extract_knowledge = AsyncMock(return_value=mock_knowledge)
        
        mock_personality = PersonalityInsights(
            style_tags={"formal": 5},
            sentiment="positive",
            confidence_score=0.9,
        )
        mock_analysis_model.analyze_personality = AsyncMock(return_value=mock_personality)
        
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=None)  # 新用戶
        mock_persona_store.save_or_update = AsyncMock()
        
        # 執行測試
        await memory_service.archive(dialogue_message)
        
        # 驗證方法被調用
        mock_analysis_model.extract_knowledge.assert_called_once()
        mock_analysis_model.analyze_personality.assert_called_once()
        mock_knowledge_store.save.assert_called_once()
        mock_persona_store.get.assert_called_once_with("user123")
        mock_persona_store.save_or_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_new_user_profile(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試新用戶畫像創建"""
        mock_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="dialog123",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        mock_analysis_model.extract_knowledge = AsyncMock(return_value=mock_knowledge)
        
        mock_personality = PersonalityInsights(
            style_tags={"casual": 3},
            sentiment="positive",
        )
        mock_analysis_model.analyze_personality = AsyncMock(return_value=mock_personality)
        
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=None)  # 新用戶
        mock_persona_store.save_or_update = AsyncMock()
        
        await memory_service.archive(dialogue_message)
        
        # 驗證保存的畫像包含新的個性分析結果
        call_args = mock_persona_store.save_or_update.call_args[0][0]
        assert call_args.user_id == "user123"
        assert call_args.style_tags == {"casual": 3}
        assert call_args.sentiment_history == {"positive": 1}

    @pytest.mark.asyncio
    async def test_archive_existing_user_profile_update(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試現有用戶畫像更新（計數累加）"""
        mock_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="dialog123",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        mock_analysis_model.extract_knowledge = AsyncMock(return_value=mock_knowledge)
        
        mock_personality = PersonalityInsights(
            style_tags={"formal": 2},
            sentiment="positive",
        )
        mock_analysis_model.analyze_personality = AsyncMock(return_value=mock_personality)
        
        # 現有用戶畫像
        existing_profile = UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )
        
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=existing_profile)
        mock_persona_store.save_or_update = AsyncMock()
        
        await memory_service.archive(dialogue_message)
        
        # 驗證保存的畫像包含累加後的計數
        call_args = mock_persona_store.save_or_update.call_args[0][0]
        assert call_args.style_tags["formal"] == 12  # 10 + 2
        assert call_args.style_tags["casual"] == 5  # 保持不變
        assert call_args.sentiment_history["positive"] == 21  # 20 + 1

    @pytest.mark.asyncio
    async def test_archive_ai_model_error(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試 AI 模型調用失敗的處理"""
        mock_analysis_model.extract_knowledge = AsyncMock(
            side_effect=Exception("Model error")
        )
        mock_analysis_model.analyze_personality = AsyncMock(
            side_effect=Exception("Model error")
        )
        
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=None)
        mock_persona_store.save_or_update = AsyncMock()
        
        # 不應該拋出異常，應該繼續處理
        await memory_service.archive(dialogue_message)
        
        # 驗證仍然嘗試保存（使用默認值）
        mock_knowledge_store.save.assert_called_once()
        mock_persona_store.save_or_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_knowledge_save_error(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試知識保存失敗的處理"""
        mock_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="dialog123",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        mock_analysis_model.extract_knowledge = AsyncMock(return_value=mock_knowledge)
        mock_analysis_model.analyze_personality = AsyncMock(
            return_value=PersonalityInsights()
        )
        
        mock_knowledge_store.save = AsyncMock(side_effect=Exception("Save error"))
        mock_persona_store.get = AsyncMock(return_value=None)
        mock_persona_store.save_or_update = AsyncMock()
        
        # 不應該拋出異常，應該繼續處理畫像更新
        await memory_service.archive(dialogue_message)
        
        # 驗證畫像更新仍然執行
        mock_persona_store.save_or_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_profile_update_error(
        self,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
        mock_analysis_model,
    ):
        """測試用戶畫像更新失敗的處理"""
        mock_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="dialog123",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        mock_analysis_model.extract_knowledge = AsyncMock(return_value=mock_knowledge)
        mock_analysis_model.analyze_personality = AsyncMock(
            return_value=PersonalityInsights()
        )
        
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=None)
        mock_persona_store.save_or_update = AsyncMock(side_effect=Exception("Update error"))
        
        # 不應該拋出異常
        await memory_service.archive(dialogue_message)
        
        # 驗證知識保存仍然執行
        mock_knowledge_store.save.assert_called_once()


class TestMemoryServiceImplHelpers:
    """測試 MemoryServiceImpl 輔助方法"""

    @pytest.fixture
    def memory_service(self):
        """創建 MemoryServiceImpl 實例（不需要真實依賴）"""
        return MemoryServiceImpl(
            knowledge_store=Mock(),
            persona_store=Mock(),
            analysis_model=Mock(),
        )

    def test_convert_user_profile_to_enriched_with_profile(self, memory_service):
        """測試 _convert_user_profile_to_enriched() 有畫像的情況"""
        profile = UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )
        
        result = memory_service._convert_user_profile_to_enriched(profile, "user123")
        
        assert result.user_id == "user123"
        assert set(result.long_term_style_tags) == {"formal", "casual"}
        assert result.current_sentiment == "positive"

    def test_convert_user_profile_to_enriched_without_profile(self, memory_service):
        """測試 _convert_user_profile_to_enriched() 無畫像的情況"""
        result = memory_service._convert_user_profile_to_enriched(None, "user123")
        
        assert result.user_id == "user123"
        assert result.long_term_style_tags == []
        assert result.current_sentiment == "neutral"

    def test_convert_user_profile_to_enriched_empty_tags(self, memory_service):
        """測試 _convert_user_profile_to_enriched() 空標籤的情況"""
        profile = UserProfileDB(
            user_id="user123",
            style_tags={},
            sentiment_history={"neutral": 1},
            last_updated=datetime.utcnow(),
        )
        
        result = memory_service._convert_user_profile_to_enriched(profile, "user123")
        
        assert result.long_term_style_tags == []
        assert result.current_sentiment == "neutral"

    def test_merge_personality_insights_new_user(self, memory_service):
        """測試 _merge_personality_insights() 新用戶的情況"""
        personality = PersonalityInsights(
            style_tags={"formal": 5},
            sentiment="positive",
        )
        
        result = memory_service._merge_personality_insights(None, personality, "user123")
        
        assert result.user_id == "user123"
        assert result.style_tags == {"formal": 5}
        assert result.sentiment_history == {"positive": 1}

    def test_merge_personality_insights_existing_user(self, memory_service):
        """測試 _merge_personality_insights() 現有用戶的情況"""
        existing_profile = UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )
        
        personality = PersonalityInsights(
            style_tags={"formal": 2, "technical": 1},
            sentiment="positive",
        )
        
        result = memory_service._merge_personality_insights(
            existing_profile, personality, "user123"
        )
        
        assert result.style_tags["formal"] == 12  # 10 + 2
        assert result.style_tags["casual"] == 5  # 保持不變
        assert result.style_tags["technical"] == 1  # 新增
        assert result.sentiment_history["positive"] == 21  # 20 + 1
        assert result.sentiment_history["negative"] == 3  # 保持不變

