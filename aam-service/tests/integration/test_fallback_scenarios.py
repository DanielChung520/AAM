"""
@purpose: 降級策略場景測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.config.settings import AISettings
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights


class TestFallbackScenarios:
    """降級策略場景測試類"""

    @pytest.fixture
    def mock_eb_mm_model(self):
        """創建 Mock EB-mM 模型"""
        model = AsyncMock()
        return model

    @pytest.fixture
    def mock_ollama_local_model(self):
        """創建 Mock Ollama 本地模型"""
        model = AsyncMock()
        return model

    @pytest.fixture
    def mock_llm_model(self):
        """創建 Mock LLM 抽象層模型"""
        model = AsyncMock()
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
            entities=["Python", "編程語言", "Web開發", "Django"],
            triples_json='[{"subject": "Python", "predicate": "是", "object": "編程語言"}, {"subject": "Django", "predicate": "是", "object": "Web框架"}]',
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
    async def test_scenario_1_eb_mm_available_quality_meets_threshold(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """
        場景 1: EB-mM 可用，質量達標
        預期：使用 EB-mM，不降級
        """
        # Mock EB-mM 可用且返回高質量結果
        mock_eb_mm_model.check_available = AsyncMock(return_value=True)
        mock_eb_mm_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型（啟用質量評估）
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
            text="Python 是一種編程語言，Django 是 Web 框架。",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證使用 EB-mM，不降級
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_scenario_2_eb_mm_available_quality_below_threshold(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """
        場景 2: EB-mM 可用，質量不達標
        預期：降級到 Ollama 本地模型
        """
        # Mock EB-mM 返回低質量結果
        mock_eb_mm_model.check_available = AsyncMock(return_value=True)
        mock_eb_mm_model.extract_knowledge = AsyncMock(return_value=low_quality_knowledge)
        
        # Mock Ollama 本地模型返回高質量結果
        mock_ollama_local_model.check_available = AsyncMock(return_value=True)
        mock_ollama_local_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型（啟用質量評估）
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
        
        # 驗證降級到 Ollama 本地模型
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_called_once()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_scenario_3_eb_mm_unavailable(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """
        場景 3: EB-mM 不可用
        預期：直接使用 Ollama 本地模型
        """
        # Mock EB-mM 不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        
        # Mock Ollama 本地模型可用且返回高質量結果
        mock_ollama_local_model.check_available = AsyncMock(return_value=True)
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
        
        # 驗證直接使用 Ollama 本地模型
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_called_once()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_scenario_4_eb_mm_and_ollama_unavailable(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """
        場景 4: EB-mM 和 Ollama 本地模型都不可用
        預期：降級到 LLM 抽象層（Qwen）
        """
        # Mock EB-mM 和 Ollama 本地模型都不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        mock_ollama_local_model.check_available = AsyncMock(return_value=False)
        
        # Mock LLM 抽象層可用且返回結果
        mock_llm_model.check_available = AsyncMock(return_value=True)
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
        
        # 驗證降級到 LLM 抽象層
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_scenario_5_all_models_unavailable(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
    ):
        """
        場景 5: 所有模型都不可用
        預期：返回空結果或默認值
        """
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
        assert result.user_id == "test_user"
        assert result.session_id == "test_session"
        
        # 驗證沒有調用任何模型的 extract_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_not_called()

    @pytest.mark.asyncio
    async def test_scenario_eb_mm_exception_fallback(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """
        場景 6: EB-mM 拋出異常
        預期：降級到 Ollama 本地模型
        """
        # Mock EB-mM 拋出異常
        mock_eb_mm_model.check_available = AsyncMock(return_value=True)
        mock_eb_mm_model.extract_knowledge = AsyncMock(side_effect=RuntimeError("EB-mM 錯誤"))
        
        # Mock Ollama 本地模型可用且返回高質量結果
        mock_ollama_local_model.check_available = AsyncMock(return_value=True)
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
    async def test_scenario_ollama_quality_below_threshold_fallback_to_llm(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """
        場景 7: Ollama 本地模型質量不達標
        預期：降級到 LLM 抽象層
        """
        # Mock EB-mM 不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        
        # Mock Ollama 本地模型返回低質量結果
        mock_ollama_local_model.check_available = AsyncMock(return_value=True)
        mock_ollama_local_model.extract_knowledge = AsyncMock(return_value=low_quality_knowledge)
        
        # Mock LLM 抽象層返回高質量結果
        mock_llm_model.check_available = AsyncMock(return_value=True)
        mock_llm_model.extract_knowledge = AsyncMock(return_value=high_quality_knowledge)
        
        # 創建降級策略模型（啟用質量評估）
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
        
        # 驗證降級到 LLM 抽象層
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_not_called()
        mock_ollama_local_model.extract_knowledge.assert_called_once()
        mock_llm_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_scenario_quality_evaluation_disabled(
        self,
        mock_eb_mm_model,
        mock_ollama_local_model,
        mock_llm_model,
        quality_evaluator,
        low_quality_knowledge,
    ):
        """
        場景 8: 質量評估已禁用
        預期：直接返回結果，不觸發降級
        """
        # Mock EB-mM 返回低質量結果
        mock_eb_mm_model.check_available = AsyncMock(return_value=True)
        mock_eb_mm_model.extract_knowledge = AsyncMock(return_value=low_quality_knowledge)
        
        # 創建降級策略模型（禁用質量評估）
        settings = AISettings(quality_evaluation_enabled=False, quality_threshold=0.7)
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
        
        # 驗證直接返回結果，不降級
        assert result == low_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()
        mock_ollama_local_model.extract_knowledge.assert_not_called()
        mock_llm_model.extract_knowledge.assert_not_called()

