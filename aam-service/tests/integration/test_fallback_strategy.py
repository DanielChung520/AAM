"""
@purpose: 降級策略基礎測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.models.domain.quality import QualityEvaluationResult


class TestFallbackStrategy:
    """降級策略基礎測試類"""

    @pytest.fixture
    def mock_eb_mm_model(self):
        """創建 Mock EB-mM 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        return model

    @pytest.fixture
    def mock_ollama_local_model(self):
        """創建 Mock Ollama 本地模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        return model

    @pytest.fixture
    def mock_llm_model(self):
        """創建 Mock LLM 抽象層模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        return model

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
            entities=["實體1", "實體2", "實體3", "實體4"],
            triples_json='[{"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}, {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"}]',
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
    async def test_fallback_priority_order(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """測試降級優先級順序（EB-mM → Ollama 本地模型 → LLM 抽象層）"""
        # Mock EB-mM 返回高質量結果
        mock_eb_mm_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證使用 EB-mM（優先級 1）
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_unavailable(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """測試 EB-mM 不可用時降級到 Ollama 本地模型"""
        # Mock EB-mM 不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        
        # Mock Ollama 本地模型返回高質量結果
        mock_ollama_local_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證使用 Ollama 本地模型（優先級 2）
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_called_once()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_quality_threshold(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """測試質量評估觸發降級"""
        # Mock EB-mM 返回低質量結果
        mock_eb_mm_model.extract_knowledge = AsyncMock(return_value=low_quality_knowledge)
        
        # Mock Ollama 本地模型返回高質量結果
        mock_ollama_local_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型（啟用質量評估）
        from src.config.settings import AISettings
        settings = AISettings(quality_evaluation_enabled=True, quality_threshold=0.7)
        
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
            settings=settings,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證降級到 Ollama 本地模型（因為 EB-mM 質量不達標）
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_called_once()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_fallback_all_models_unavailable(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
    ):
        """測試所有模型都不可用"""
        # Mock 所有模型都不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        mock_ollama_local_model.check_available = AsyncMock(return_value=False)
        mock_llm_model.check_available = AsyncMock(return_value=False)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
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

    @pytest.mark.asyncio
    async def test_fallback_exception_handling(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """測試異常情況觸發降級"""
        # Mock EB-mM 拋出異常
        mock_eb_mm_model.extract_knowledge = AsyncMock(side_effect=RuntimeError("EB-mM 錯誤"))
        
        # Mock Ollama 本地模型返回高質量結果
        mock_ollama_local_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證降級到 Ollama 本地模型
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_llm_layer_final_fallback(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """測試 LLM 抽象層作為最後保障"""
        # Mock EB-mM 和 Ollama 本地模型都不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        mock_ollama_local_model.check_available = AsyncMock(return_value=False)
        
        # Mock LLM 抽象層返回結果
        mock_llm_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證使用 LLM 抽象層（優先級 3）
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_check_available(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
    ):
        """測試降級策略模型可用性檢查"""
        # Mock EB-mM 可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=True)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 檢查可用性
        result = await fallback_model.check_available()
        
        # 驗證至少有一個模型可用
        assert result is True
        mock_eb_mm_model.check_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_personality_analysis(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
    ):
        """測試降級策略個性分析"""
        # Mock 個性分析結果
        personality = PersonalityInsights(
            style_tags={"formal": 0.8},
            sentiment="positive",
            language_patterns=["專業"],
            confidence_score=0.85,
        )
        
        mock_eb_mm_model.analyze_personality = AsyncMock(return_value=personality)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行個性分析
        result = await fallback_model.analyze_personality("測試文本")
        
        # 驗證結果
        assert isinstance(result, PersonalityInsights)
        assert result.sentiment == "positive"
        mock_eb_mm_model.analyze_personality.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_personality_analysis_fallback(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
    ):
        """測試個性分析降級"""
        # Mock EB-mM 不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        
        # Mock 個性分析結果
        personality = PersonalityInsights(
            style_tags={"casual": 0.6},
            sentiment="neutral",
            language_patterns=["日常"],
            confidence_score=0.7,
        )
        
        mock_ollama_local_model.analyze_personality = AsyncMock(return_value=personality)
        
        # 創建降級策略模型
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行個性分析
        result = await fallback_model.analyze_personality("測試文本")
        
        # 驗證降級到 Ollama 本地模型
        assert isinstance(result, PersonalityInsights)
        mock_eb_mm_model.analyze_personality.assert_not_called()
        mock_ollama_local_model.analyze_personality.assert_called_once()

