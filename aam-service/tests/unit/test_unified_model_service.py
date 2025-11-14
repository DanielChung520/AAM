"""
@purpose: 統一模型服務單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.core.interfaces.i_model_provider import ModelProviderType


class TestUnifiedModelService:
    """統一模型服務測試類"""

    @pytest.fixture
    def mock_provider(self):
        """創建 Mock Provider"""
        provider = MagicMock()
        provider.provider_type = ModelProviderType.OLLAMA
        provider.check_available = AsyncMock(return_value=True)
        provider.generate = AsyncMock()
        provider.get_config = MagicMock(return_value={
            "provider_type": "ollama",
            "model_name": "llama3",
        })
        return provider

    @pytest.fixture
    def unified_service(self, mock_provider):
        """創建統一模型服務實例"""
        return UnifiedModelService(provider=mock_provider)

    @pytest.mark.asyncio
    async def test_extract_knowledge_success(self, unified_service, mock_provider):
        """測試知識提取（成功）"""
        # Mock NER 提取結果
        ner_result = json.dumps({"entities": ["實體1", "實體2"]})
        # Mock KT 提取結果
        kt_result = json.dumps({
            "triples": [
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}
            ]
        })
        
        # 設置 generate 的返回值（第一次調用返回 NER，第二次返回 KT）
        mock_provider.generate = AsyncMock(side_effect=[ner_result, kt_result])
        
        knowledge = await unified_service.extract_knowledge(
            text="測試文本",
            user_id="user1",
            session_id="session1",
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        assert knowledge.user_id == "user1"
        assert knowledge.session_id == "session1"
        assert len(knowledge.entities) == 2
        assert "實體1" in knowledge.entities
        
        triples = json.loads(knowledge.triples_json)
        assert len(triples) == 1
        assert triples[0]["subject"] == "主體1"

    @pytest.mark.asyncio
    async def test_extract_knowledge_unavailable(self, unified_service, mock_provider):
        """測試知識提取（服務不可用）"""
        mock_provider.check_available = AsyncMock(return_value=False)
        
        with pytest.raises(RuntimeError, match="不可用"):
            await unified_service.extract_knowledge(
                text="測試文本",
                user_id="user1",
                session_id="session1",
            )

    @pytest.mark.asyncio
    async def test_analyze_personality_success(self, unified_service, mock_provider):
        """測試個性分析（成功）"""
        personality_result = json.dumps({
            "style_tags": {"formal": 0.8, "casual": 0.2},
            "sentiment": "positive",
            "language_patterns": ["模式1", "模式2"],
            "confidence_score": 0.85,
        })
        
        mock_provider.generate = AsyncMock(return_value=personality_result)
        
        personality = await unified_service.analyze_personality("測試文本")
        
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment == "positive"
        assert personality.confidence_score == 0.85
        assert "formal" in personality.style_tags
        assert len(personality.language_patterns) == 2

    @pytest.mark.asyncio
    async def test_analyze_personality_unavailable(self, unified_service, mock_provider):
        """測試個性分析（服務不可用）"""
        mock_provider.check_available = AsyncMock(return_value=False)
        
        with pytest.raises(RuntimeError, match="不可用"):
            await unified_service.analyze_personality("測試文本")

    @pytest.mark.asyncio
    async def test_analyze_personality_invalid_json(self, unified_service, mock_provider):
        """測試個性分析（無效的 JSON）"""
        mock_provider.generate = AsyncMock(return_value="無效的 JSON")
        
        # 應該返回默認值而不是拋出異常
        personality = await unified_service.analyze_personality("測試文本")
        
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment == "neutral"
        assert personality.confidence_score == 0.5

    @pytest.mark.asyncio
    async def test_check_available(self, unified_service, mock_provider):
        """測試可用性檢查"""
        mock_provider.check_available = AsyncMock(return_value=True)
        
        result = await unified_service.check_available()
        assert result is True

