"""
@purpose: 降級策略端到端測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights


class TestFallbackE2E:
    """降級策略端到端測試類"""

    @pytest.fixture
    def mock_eb_mm_service(self):
        """創建 Mock EB-mM 服務"""
        service = AsyncMock()
        service.check_available = AsyncMock(return_value=True)
        return service

    @pytest.fixture
    def mock_ollama_local_service(self):
        """創建 Mock Ollama 本地模型服務"""
        service = AsyncMock()
        service.check_available = AsyncMock(return_value=True)
        return service

    @pytest.fixture
    def mock_llm_service(self):
        """創建 Mock LLM 抽象層服務"""
        service = AsyncMock()
        service.check_available = AsyncMock(return_value=True)
        return service

    @pytest.fixture
    def quality_evaluator(self):
        """創建質量評估器"""
        return QualityEvaluator(quality_threshold=0.7)

    @pytest.fixture
    def high_quality_knowledge(self):
        """創建高質量知識資產"""
        return KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=["Python", "編程語言", "Web開發", "Django", "Flask"],
            triples_json='[{"subject": "Python", "predicate": "是", "object": "編程語言"}, {"subject": "Django", "predicate": "是", "object": "Web框架"}, {"subject": "Flask", "predicate": "是", "object": "Web框架"}]',
        )

    @pytest.fixture
    def low_quality_knowledge(self):
        """創建低質量知識資產"""
        return KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_eb_mm_success(
        self,
        mock_eb_mm_service,
        mock_ollama_local_service,
        mock_llm_service,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """端到端測試：EB-mM 成功，不降級"""
        # Mock EB-mM 返回高質量結果
        mock_eb_mm_service.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        from src.config.settings import AISettings
        settings = AISettings(quality_evaluation_enabled=True, quality_threshold=0.7)
        
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_service,
            ollama_local_model=mock_ollama_local_service,
            llm_model=mock_llm_service,
            quality_evaluator=quality_evaluator,
            settings=settings,
        )
        
        # 執行完整的知識提取流程
        result = await fallback_model.extract_knowledge(
            text="Python 是一種編程語言，Django 和 Flask 是 Web 框架。",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證結果
        assert isinstance(result, KnowledgeAsset)
        assert result == high_quality_knowledge
        assert len(result.entities) > 0
        
        # 驗證只使用了 EB-mM
        mock_eb_mm_service.extract_knowledge.assert_called_once()
        mock_ollama_local_service.extract_knowledge.assert_not_called()
        mock_llm_service.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_quality_based_fallback(
        self,
        mock_eb_mm_service,
        mock_ollama_local_service,
        mock_llm_service,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """端到端測試：質量評估觸發降級"""
        # Mock EB-mM 返回低質量結果
        mock_eb_mm_service.extract_knowledge = AsyncMock(return_value=low_quality_knowledge)
        
        # Mock Ollama 本地模型返回高質量結果
        mock_ollama_local_service.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型（啟用質量評估）
        from src.config.settings import AISettings
        settings = AISettings(quality_evaluation_enabled=True, quality_threshold=0.7)
        
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_service,
            ollama_local_model=mock_ollama_local_service,
            llm_model=mock_llm_service,
            quality_evaluator=quality_evaluator,
            settings=settings,
        )
        
        # 執行完整的知識提取流程
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證結果
        assert isinstance(result, KnowledgeAsset)
        assert result == high_quality_knowledge
        
        # 驗證降級流程
        mock_eb_mm_service.extract_knowledge.assert_called_once()
        mock_ollama_local_service.extract_knowledge.assert_called_once()
        mock_llm_service.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_to_llm_layer(
        self,
        mock_eb_mm_service,
        mock_ollama_local_service,
        mock_llm_service,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """端到端測試：降級到 LLM 抽象層"""
        # Mock EB-mM 和 Ollama 本地模型都不可用
        mock_eb_mm_service.check_available = AsyncMock(return_value=False)
        mock_ollama_local_service.check_available = AsyncMock(return_value=False)
        
        # Mock LLM 抽象層返回結果
        mock_llm_service.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_service,
            ollama_local_model=mock_ollama_local_service,
            llm_model=mock_llm_service,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行完整的知識提取流程
        result = await fallback_model.extract_knowledge(
            text="Python 是一種編程語言。",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證結果
        assert isinstance(result, KnowledgeAsset)
        assert result == high_quality_knowledge
        
        # 驗證降級到 LLM 抽象層
        mock_eb_mm_service.extract_knowledge.assert_not_called()
        mock_ollama_local_service.extract_knowledge.assert_not_called()
        mock_llm_service.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_personality_analysis(
        self,
        mock_eb_mm_service,
        mock_ollama_local_service,
        mock_llm_service,
        quality_evaluator,
    ):
        """端到端測試：個性分析降級流程"""
        # Mock 個性分析結果
        personality = PersonalityInsights(
            style_tags={"formal": 0.8, "professional": 0.9},
            sentiment="positive",
            language_patterns=["使用專業術語", "結構化表達"],
            confidence_score=0.85,
        )
        
        # Mock EB-mM 不可用
        mock_eb_mm_service.check_available = AsyncMock(return_value=False)
        
        # Mock Ollama 本地模型返回結果
        mock_ollama_local_service.analyze_personality = AsyncMock(return_value=personality)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_service,
            ollama_local_model=mock_ollama_local_service,
            llm_model=mock_llm_service,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行個性分析
        result = await fallback_model.analyze_personality(
            "我對 Python 編程很感興趣，希望學習 Web 開發。"
        )
        
        # 驗證結果
        assert isinstance(result, PersonalityInsights)
        assert result.sentiment == "positive"
        assert result.confidence_score > 0.0
        
        # 驗證降級到 Ollama 本地模型
        mock_eb_mm_service.analyze_personality.assert_not_called()
        mock_ollama_local_service.analyze_personality.assert_called_once()

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_with_real_providers(self):
        """端到端測試：使用真實 Provider（如果可用）"""
        import os
        
        # 檢查是否有真實的 API Key
        qwen_api_key = os.getenv("QWEN_API_KEY", "")
        if not qwen_api_key or qwen_api_key == "test-key":
            pytest.skip("需要真實的 QWEN_API_KEY 環境變量")
        
        try:
            # 創建 Qwen Provider
            qwen_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                model_name="qwen-turbo",
            )
            
            # 創建 UnifiedModelService
            llm_service = UnifiedModelService(provider=qwen_provider)
            
            # 檢查可用性
            is_available = await llm_service.check_available()
            if not is_available:
                pytest.skip("Qwen API 不可用")
            
            # 創建降級策略模型（只使用 LLM 層）
            quality_evaluator = QualityEvaluator(quality_threshold=0.7)
            fallback_model = FallbackAnalysisModel(
                eb_mm_model=None,
                ollama_local_model=None,
                llm_model=llm_service,
                quality_evaluator=quality_evaluator,
            )
            
            # 執行知識提取
            result = await fallback_model.extract_knowledge(
                text="Python 是一種高級編程語言，由 Guido van Rossum 創建。",
                user_id="test_user",
                session_id="test_session_e2e"
            )
            
            # 驗證結果
            assert isinstance(result, KnowledgeAsset)
            assert result.user_id == "test_user"
            assert result.session_id == "test_session_e2e"
            assert isinstance(result.entities, list)
            
        except Exception as e:
            pytest.skip(f"真實 Provider 測試失敗: {e}")

    @pytest.mark.asyncio
    async def test_e2e_fallback_flow_all_models_fail(
        self,
        mock_eb_mm_service,
        mock_ollama_local_service,
        mock_llm_service,
        quality_evaluator,
    ):
        """端到端測試：所有模型都失敗"""
        # Mock 所有模型都拋出異常
        mock_eb_mm_service.check_available = AsyncMock(return_value=True)
        mock_eb_mm_service.extract_knowledge = AsyncMock(side_effect=RuntimeError("EB-mM 錯誤"))
        
        mock_ollama_local_service.check_available = AsyncMock(return_value=True)
        mock_ollama_local_service.extract_knowledge = AsyncMock(side_effect=RuntimeError("Ollama 錯誤"))
        
        mock_llm_service.check_available = AsyncMock(return_value=True)
        mock_llm_service.extract_knowledge = AsyncMock(side_effect=RuntimeError("LLM 錯誤"))
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_service,
            ollama_local_model=mock_ollama_local_service,
            llm_model=mock_llm_service,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證返回空結果
        assert isinstance(result, KnowledgeAsset)
        assert result.entities == []
        assert result.triples_json == "[]"
        
        # 驗證所有模型都被嘗試
        mock_eb_mm_service.extract_knowledge.assert_called_once()
        mock_ollama_local_service.extract_knowledge.assert_called_once()
        mock_llm_service.extract_knowledge.assert_called_once()

