"""
@purpose: 降級策略分析模型單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.models.domain.quality import QualityEvaluationResult


class TestFallbackAnalysisModel:
    """降級策略分析模型測試類"""

    @pytest.fixture
    def mock_eb_mm_model(self):
        """創建 Mock Eb-MM 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        return model

    @pytest.fixture
    def mock_langchain_model(self):
        """創建 Mock LangChain Embedding 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        return model

    @pytest.fixture
    def mock_llm_model(self):
        """創建 Mock LLM 模型"""
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
            triples_json='[{"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}]',
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
    async def test_extract_knowledge_eb_mm_success(
        self, mock_eb_mm_model, quality_evaluator, high_quality_knowledge
    ):
        """測試 Eb-MM 模型成功提取知識"""
        # 模擬高質量結果
        mock_eb_mm_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        # 模擬質量評估器返回高質量分數
        with patch.object(
            quality_evaluator,
            "evaluate",
            return_value=QualityEvaluationResult(
                overall_score=0.8,
                entity_score=0.4,
                triple_score=0.4,
                entity_count=4,
                triple_count=1,
                meets_threshold=True,
                threshold=0.7,
            ),
        ):
            model = FallbackAnalysisModel(
                eb_mm_model=mock_eb_mm_model,
                quality_evaluator=quality_evaluator,
            )
            
            result = await model.extract_knowledge(
                "測試文本", "test_user", "test_session"
            )
            
            assert result == high_quality_knowledge
            mock_eb_mm_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_knowledge_eb_mm_low_quality_fallback(
        self,
        mock_eb_mm_model,
        mock_langchain_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """測試 Eb-MM 質量不達標，降級到 LangChain"""
        # Eb-MM 返回低質量結果
        mock_eb_mm_model.extract_knowledge = AsyncMock(
            return_value=low_quality_knowledge
        )
        
        # LangChain 返回高質量結果
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        # 模擬質量評估：Eb-MM 低質量，LangChain 高質量
        def mock_evaluate(knowledge, threshold=None):
            if knowledge == low_quality_knowledge:
                return QualityEvaluationResult(
                    overall_score=0.3,
                    entity_score=0.0,
                    triple_score=0.0,
                    entity_count=0,
                    triple_count=0,
                    meets_threshold=False,
                    threshold=threshold or 0.7,
                )
            else:
                return QualityEvaluationResult(
                    overall_score=0.8,
                    entity_score=0.4,
                    triple_score=0.4,
                    entity_count=4,
                    triple_count=1,
                    meets_threshold=True,
                    threshold=threshold or 0.7,
                )
        
        with patch.object(quality_evaluator, "evaluate", side_effect=mock_evaluate):
            model = FallbackAnalysisModel(
                eb_mm_model=mock_eb_mm_model,
                langchain_model=mock_langchain_model,
                quality_evaluator=quality_evaluator,
            )
            
            result = await model.extract_knowledge(
                "測試文本", "test_user", "test_session"
            )
            
            # 應該使用 LangChain 的結果
            assert result == high_quality_knowledge
            mock_eb_mm_model.extract_knowledge.assert_called_once()
            mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_knowledge_all_models_fail(self, quality_evaluator):
        """測試所有模型都失敗，返回空結果"""
        model = FallbackAnalysisModel(
            eb_mm_model=None,
            langchain_model=None,
            llm_model=None,
            quality_evaluator=quality_evaluator,
        )
        
        result = await model.extract_knowledge(
            "測試文本", "test_user", "test_session"
        )
        
        # 應該返回空的知識資產
        assert result.user_id == "test_user"
        assert result.session_id == "test_session"
        assert result.entities == []
        assert result.triples_json == "[]"

    @pytest.mark.asyncio
    async def test_extract_knowledge_eb_mm_unavailable_fallback(
        self, mock_eb_mm_model, mock_langchain_model, quality_evaluator, high_quality_knowledge
    ):
        """測試 Eb-MM 不可用，降級到 LangChain"""
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        with patch.object(
            quality_evaluator,
            "evaluate",
            return_value=QualityEvaluationResult(
                overall_score=0.8,
                entity_score=0.4,
                triple_score=0.4,
                entity_count=4,
                triple_count=1,
                meets_threshold=True,
                threshold=0.7,
            ),
        ):
            model = FallbackAnalysisModel(
                eb_mm_model=mock_eb_mm_model,
                langchain_model=mock_langchain_model,
                quality_evaluator=quality_evaluator,
            )
            
            result = await model.extract_knowledge(
                "測試文本", "test_user", "test_session"
            )
            
            # 應該使用 LangChain 的結果
            assert result == high_quality_knowledge
            mock_eb_mm_model.extract_knowledge.assert_not_called()
            mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_personality_eb_mm_success(
        self, mock_eb_mm_model, quality_evaluator
    ):
        """測試 Eb-MM 模型成功分析個性"""
        expected_insights = PersonalityInsights(
            style_tags={"formal": 10},
            sentiment="positive",
            language_patterns=["pattern1"],
            confidence_score=0.8,
        )
        mock_eb_mm_model.analyze_personality = AsyncMock(
            return_value=expected_insights
        )
        
        model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            quality_evaluator=quality_evaluator,
        )
        
        result = await model.analyze_personality("測試文本")
        
        assert result == expected_insights
        mock_eb_mm_model.analyze_personality.assert_called_once_with("測試文本")

    @pytest.mark.asyncio
    async def test_check_available(self, mock_eb_mm_model, quality_evaluator):
        """測試檢查模型可用性"""
        model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            quality_evaluator=quality_evaluator,
        )
        
        result = await model.check_available()
        
        assert result is True
        mock_eb_mm_model.check_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_available_no_models(self, quality_evaluator):
        """測試沒有模型時檢查可用性"""
        model = FallbackAnalysisModel(
            eb_mm_model=None,
            langchain_model=None,
            llm_model=None,
            quality_evaluator=quality_evaluator,
        )
        
        result = await model.check_available()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_knowledge_quality_evaluation_disabled(
        self, mock_eb_mm_model, quality_evaluator, high_quality_knowledge
    ):
        """測試質量評估禁用時直接返回結果"""
        from src.config.settings import AISettings
        
        mock_eb_mm_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        settings = AISettings(quality_evaluation_enabled=False)
        model = FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            quality_evaluator=quality_evaluator,
            settings=settings,
        )
        
        result = await model.extract_knowledge(
            "測試文本", "test_user", "test_session"
        )
        
        # 應該直接返回結果，不進行質量評估
        assert result == high_quality_knowledge
        mock_eb_mm_model.extract_knowledge.assert_called_once()

