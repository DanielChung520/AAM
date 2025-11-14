"""
@purpose: 語義分析集成測試（測試降級流程）
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.langchain_embedding_model import LangChainEmbeddingModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.models.domain.quality import QualityEvaluationResult


class TestSemanticAnalysisIntegration:
    """語義分析集成測試類"""

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
    async def test_fallback_eb_mm_to_langchain(
        self,
        mock_eb_mm_model,
        mock_langchain_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """測試 Eb-MM 失敗後降級到 LangChain Embedding"""
        # Eb-MM 返回低質量結果
        mock_eb_mm_model.extract_knowledge = AsyncMock(
            return_value=low_quality_knowledge
        )
        
        # LangChain Embedding 返回高質量結果
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
            
            # 應該使用 LangChain Embedding 的結果
            assert result == high_quality_knowledge
            mock_eb_mm_model.extract_knowledge.assert_called_once()
            mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_langchain_to_llm(
        self,
        mock_langchain_model,
        mock_llm_model,
        quality_evaluator,
        low_quality_knowledge,
        high_quality_knowledge,
    ):
        """測試 LangChain Embedding 失敗後降級到 LLM"""
        # LangChain Embedding 返回低質量結果
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=low_quality_knowledge
        )
        
        # LLM 返回高質量結果
        mock_llm_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        # 模擬質量評估：LangChain 低質量
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
                langchain_model=mock_langchain_model,
                llm_model=mock_llm_model,
                quality_evaluator=quality_evaluator,
            )
            
            result = await model.extract_knowledge(
                "測試文本", "test_user", "test_session"
            )
            
            # 應該使用 LLM 的結果
            assert result == high_quality_knowledge
            mock_langchain_model.extract_knowledge.assert_called_once()
            mock_llm_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_unavailable_to_langchain(
        self,
        mock_eb_mm_model,
        mock_langchain_model,
        quality_evaluator,
        high_quality_knowledge,
    ):
        """測試 Eb-MM 不可用時直接使用 LangChain Embedding"""
        # Eb-MM 不可用
        mock_eb_mm_model.check_available = AsyncMock(return_value=False)
        
        # LangChain Embedding 可用並返回高質量結果
        mock_langchain_model.check_available = AsyncMock(return_value=True)
        mock_langchain_model.extract_knowledge = AsyncMock(
            return_value=high_quality_knowledge
        )
        
        # 模擬質量評估：LangChain 高質量
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
            
            # 應該直接使用 LangChain Embedding，不嘗試 Eb-MM
            assert result == high_quality_knowledge
            mock_langchain_model.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_langchain_embedding_model_integration(self):
        """測試 LangChain Embedding 模型集成"""
        with patch("src.infrastructure.ai.langchain_embedding_model.ChatOpenAI") as mock_chat:
            mock_chat_instance = AsyncMock()
            mock_chat.return_value = mock_chat_instance
            
            # 創建 LangChain Embedding 模型
            model = LangChainEmbeddingModel(
                model_name="gpt-3.5-turbo",
                api_key="test-api-key",
            )
            model.llm = mock_chat_instance
            
            # 模擬 NER 和 KT 提取
            model._extract_ner = AsyncMock(return_value=["實體1", "實體2"])
            model._extract_kt = AsyncMock(return_value=[
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}
            ])
            
            # 測試知識提取
            result = await model.extract_knowledge(
                "測試文本", "test_user", "test_session"
            )
            
            assert isinstance(result, KnowledgeAsset)
            assert result.user_id == "test_user"
            assert result.session_id == "test_session"
            assert len(result.entities) == 2

    @pytest.mark.asyncio
    async def test_personality_analysis_integration(self):
        """測試個性分析集成"""
        with patch("src.infrastructure.ai.langchain_embedding_model.ChatOpenAI") as mock_chat:
            mock_chat_instance = AsyncMock()
            mock_chat.return_value = mock_chat_instance
            
            # 創建 LangChain Embedding 模型
            model = LangChainEmbeddingModel(
                model_name="gpt-3.5-turbo",
                api_key="test-api-key",
            )
            model.llm = mock_chat_instance
            
            # 模擬個性分析結果
            personality_data = {
                "style_tags": ["formal", "technical"],
                "emotion": "positive",
                "language_patterns": ["簡潔", "專業"],
                "confidence_score": 0.85
            }
            
            mock_response = MagicMock()
            mock_response.content = json.dumps(personality_data)
            model.llm.ainvoke = AsyncMock(return_value=mock_response)
            
            with patch.object(model.json_parser, "parse", return_value=personality_data):
                result = await model.analyze_personality("測試文本")
                
                assert isinstance(result, PersonalityInsights)
                assert result.sentiment == "positive"
                assert len(result.style_tags) == 2

