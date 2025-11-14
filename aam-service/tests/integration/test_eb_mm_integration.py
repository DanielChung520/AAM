"""
@purpose: EB-mM 模型集成測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest
from unittest.mock import AsyncMock, Mock, MagicMock

from src.infrastructure.ai.eb_mm_analysis_model import EbMMAnalysisModel
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.langchain_embedding_model import LangChainEmbeddingModel
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.config.settings import AISettings


class TestEbMMIntegration:
    """EB-mM 模型集成測試類"""

    @pytest.fixture
    def mock_eb_mm_provider(self):
        """創建 Mock EB-mM Provider"""
        provider = AsyncMock()
        provider.provider_type = Mock()
        provider.provider_type.value = "ollama"
        provider.check_available = AsyncMock(return_value=True)
        provider.generate = AsyncMock()
        provider.get_config = Mock(return_value={})
        return provider

    @pytest.fixture
    def mock_langchain_model(self):
        """創建 Mock LangChain Embedding 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        model.extract_knowledge = AsyncMock()
        model.analyze_personality = AsyncMock()
        return model

    @pytest.fixture
    def mock_llm_model(self):
        """創建 Mock LLM 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        model.extract_knowledge = AsyncMock()
        model.analyze_personality = AsyncMock()
        return model

    @pytest.fixture
    def quality_evaluator(self):
        """創建質量評估器"""
        settings = AISettings()
        return QualityEvaluator(settings=settings)

    @pytest.fixture
    def eb_mm_model(self, mock_eb_mm_provider):
        """創建 EB-mM 模型實例"""
        unified_service = UnifiedModelService(provider=mock_eb_mm_provider)
        return EbMMAnalysisModel(unified_model_service=unified_service)

    @pytest.fixture
    def fallback_model(self, eb_mm_model, mock_langchain_model, mock_llm_model, quality_evaluator):
        """創建降級策略模型"""
        settings = AISettings()
        return FallbackAnalysisModel(
            eb_mm_model=eb_mm_model,
            langchain_model=mock_langchain_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
            settings=settings,
        )

    @pytest.mark.asyncio
    async def test_eb_mm_extract_knowledge_success(
        self, eb_mm_model, mock_eb_mm_provider
    ):
        """測試 EB-mM 知識提取成功"""
        # 模擬 Provider 返回結果
        mock_eb_mm_provider.generate = AsyncMock(side_effect=[
            json.dumps({"entities": ["實體1", "實體2"]}),  # NER
            json.dumps({"key_points": ["知識點1"]}),  # KE
            json.dumps({"triples": [{"subject": "主體", "predicate": "謂詞", "object": "客體"}]})  # KT
        ])
        
        knowledge = await eb_mm_model.extract_knowledge(
            text="測試文本包含實體1和實體2",
            user_id="user123",
            session_id="session456"
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        assert knowledge.user_id == "user123"
        assert knowledge.session_id == "session456"
        assert len(knowledge.entities) == 2

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_to_langchain(
        self, fallback_model, eb_mm_model, mock_langchain_model, mock_eb_mm_provider
    ):
        """測試 EB-mM 失敗後降級到 LangChain Embedding"""
        # 模擬 EB-mM 失敗
        mock_eb_mm_provider.check_available = AsyncMock(return_value=False)
        
        # 模擬 LangChain Embedding 成功
        high_quality_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2", "實體3"],
            triples_json=json.dumps([
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
                {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"}
            ]),
        )
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        knowledge = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="user123",
            session_id="session456"
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        # 驗證使用了 LangChain Embedding
        mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_unavailable_to_langchain(
        self, fallback_model, eb_mm_model, mock_langchain_model, mock_eb_mm_provider
    ):
        """測試 EB-mM 不可用時直接使用 LangChain Embedding"""
        # 模擬 EB-mM 不可用
        mock_eb_mm_provider.check_available = AsyncMock(return_value=False)
        
        # 模擬 LangChain Embedding 成功
        high_quality_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2"],
            triples_json=json.dumps([
                {"subject": "主體", "predicate": "謂詞", "object": "客體"}
            ]),
        )
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        knowledge = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="user123",
            session_id="session456"
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        # 驗證 EB-mM 未被調用
        mock_eb_mm_provider.generate.assert_not_called()
        # 驗證使用了 LangChain Embedding
        mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_low_quality_to_langchain(
        self, fallback_model, eb_mm_model, mock_langchain_model, mock_eb_mm_provider
    ):
        """測試 EB-mM 質量不達標時降級到 LangChain Embedding"""
        # 模擬 EB-mM 返回低質量結果
        mock_eb_mm_provider.generate = AsyncMock(side_effect=[
            json.dumps({"entities": []}),  # 空實體
            json.dumps({"key_points": []}),  # 空知識點
            json.dumps({"triples": []})  # 空三元組
        ])
        
        # 模擬 LangChain Embedding 返回高質量結果
        high_quality_knowledge = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2", "實體3"],
            triples_json=json.dumps([
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}
            ]),
        )
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        knowledge = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="user123",
            session_id="session456"
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        # 驗證使用了 LangChain Embedding（因為 EB-mM 質量不達標）
        mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_eb_mm_analyze_personality_success(
        self, eb_mm_model, mock_eb_mm_provider
    ):
        """測試 EB-mM 個性分析成功"""
        mock_eb_mm_provider.generate = AsyncMock(return_value=json.dumps({
            "style_tags": {"formal": 0.8, "technical": 0.9},
            "sentiment": "positive",
            "language_patterns": ["簡潔", "專業"],
            "tone": "專業",
            "confidence_score": 0.85
        }))
        
        personality = await eb_mm_model.analyze_personality("測試文本")
        
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment == "positive"
        assert personality.confidence_score == 0.85

    @pytest.mark.asyncio
    async def test_provider_switching_ollama_to_vllm(
        self, mock_eb_mm_provider
    ):
        """測試 Provider 切換（Ollama → vLLM）"""
        # 創建 Ollama Provider
        mock_eb_mm_provider.provider_type.value = "ollama"
        unified_service_ollama = UnifiedModelService(provider=mock_eb_mm_provider)
        eb_mm_model_ollama = EbMMAnalysisModel(unified_model_service=unified_service_ollama)
        
        # 創建 vLLM Provider
        mock_vllm_provider = AsyncMock()
        mock_vllm_provider.provider_type = Mock()
        mock_vllm_provider.provider_type.value = "vllm"
        mock_vllm_provider.check_available = AsyncMock(return_value=True)
        mock_vllm_provider.generate = AsyncMock()
        mock_vllm_provider.get_config = Mock(return_value={})
        
        unified_service_vllm = UnifiedModelService(provider=mock_vllm_provider)
        eb_mm_model_vllm = EbMMAnalysisModel(unified_model_service=unified_service_vllm)
        
        # 驗證兩個模型都可以正常工作
        assert await eb_mm_model_ollama.check_available() is True
        assert await eb_mm_model_vllm.check_available() is True

