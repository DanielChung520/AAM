"""
@purpose: 降級策略性能測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset


class TestFallbackPerformance:
    """降級策略性能測試類"""

    @pytest.fixture
    def mock_eb_mm_model(self):
        """創建 Mock EB-mM 模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        
        # 模擬快速響應（0.1秒）
        async def fast_extract(*args, **kwargs):
            await asyncio.sleep(0.1)
            return KnowledgeAsset(
                user_id="test_user",
                session_id="test_session",
                timestamp=int(time.time()),
                source_type="dialogue",
                entities=[],
                triples_json="[]",
            )
        
        model.extract_knowledge = fast_extract
        return model

    @pytest.fixture
    def mock_ollama_local_model(self):
        """創建 Mock Ollama 本地模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        
        # 模擬中等響應（0.5秒）
        async def medium_extract(*args, **kwargs):
            await asyncio.sleep(0.5)
            return KnowledgeAsset(
                user_id="test_user",
                session_id="test_session",
                timestamp=int(time.time()),
                source_type="dialogue",
                entities=[],
                triples_json="[]",
            )
        
        model.extract_knowledge = medium_extract
        return model

    @pytest.fixture
    def mock_llm_model(self):
        """創建 Mock LLM 抽象層模型"""
        model = AsyncMock()
        model.check_available = AsyncMock(return_value=True)
        
        # 模擬較慢響應（1.0秒）
        async def slow_extract(*args, **kwargs):
            await asyncio.sleep(1.0)
            return KnowledgeAsset(
                user_id="test_user",
                session_id="test_session",
                timestamp=int(time.time()),
                source_type="dialogue",
                entities=[],
                triples_json="[]",
            )
        
        model.extract_knowledge = slow_extract
        return model

    @pytest.fixture
    def quality_evaluator(self):
        """創建質量評估器"""
        return QualityEvaluator(quality_threshold=0.7)

    @pytest.fixture
    def fallback_model(
        self, mock_eb_mm_model, mock_ollama_local_model, mock_llm_model, quality_evaluator
    ):
        """創建降級策略模型"""
        return FallbackAnalysisModel(
            eb_mm_model=mock_eb_mm_model,
            ollama_local_model=mock_ollama_local_model,
            llm_model=mock_llm_model,
            quality_evaluator=quality_evaluator,
        )

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_fallback_decision_time(self, fallback_model):
        """測試降級決策時間"""
        text = "測試文本"
        user_id = "test_user"
        session_id = "test_session"
        
        start_time = time.time()
        result = await fallback_model.extract_knowledge(text, user_id, session_id)
        end_time = time.time()
        
        decision_time = end_time - start_time
        
        # 預期降級決策時間 < 1秒（使用 EB-mM，最快）
        assert decision_time < 1.0, f"降級決策時間過長: {decision_time:.2f}秒"
        assert result is not None, "應返回知識資產"
        
        print(f"\n降級決策時間: {decision_time:.2f}秒")

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_fallback_response_time_comparison(
        self, mock_eb_mm_model, mock_ollama_local_model, mock_llm_model, quality_evaluator
    ):
        """測試各層級模型的響應時間對比"""
        text = "測試文本"
        user_id = "test_user"
        session_id = "test_session"
        
        # 測試 EB-mM 響應時間
        start_time = time.time()
        eb_mm_result = await mock_eb_mm_model.extract_knowledge(text, user_id, session_id)
        eb_mm_time = time.time() - start_time
        
        # 測試 Ollama 本地模型響應時間
        start_time = time.time()
        ollama_result = await mock_ollama_local_model.extract_knowledge(text, user_id, session_id)
        ollama_time = time.time() - start_time
        
        # 測試 LLM 抽象層響應時間
        start_time = time.time()
        llm_result = await mock_llm_model.extract_knowledge(text, user_id, session_id)
        llm_time = time.time() - start_time
        
        print(f"\nEB-mM 響應時間: {eb_mm_time:.2f}秒")
        print(f"Ollama 本地模型響應時間: {ollama_time:.2f}秒")
        print(f"LLM 抽象層響應時間: {llm_time:.2f}秒")
        
        # 驗證響應時間順序（EB-mM < Ollama < LLM）
        assert eb_mm_time < ollama_time, "EB-mM 應比 Ollama 快"
        assert ollama_time < llm_time, "Ollama 應比 LLM 快"

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_quality_evaluation_time(self, quality_evaluator):
        """測試質量評估時間"""
        from src.models.domain.database import KnowledgeAsset
        
        # 創建測試知識資產
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=int(time.time()),
            source_type="dialogue",
            entities=[
                {"text": "實體1", "type": "PERSON"},
                {"text": "實體2", "type": "ORG"},
            ],
            triples_json='[{"subject": "主體", "predicate": "謂語", "object": "客體"}]',
        )
        
        start_time = time.time()
        quality_result = quality_evaluator.evaluate(knowledge)
        end_time = time.time()
        
        evaluation_time = end_time - start_time
        
        # 預期質量評估時間 < 5秒
        assert evaluation_time < 5.0, f"質量評估時間過長: {evaluation_time:.2f}秒"
        assert quality_result is not None, "應返回質量評估結果"
        
        print(f"\n質量評估時間: {evaluation_time:.4f}秒")

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_fallback_flow_time(self, fallback_model):
        """測試整體降級流程時間"""
        text = "測試文本"
        user_id = "test_user"
        session_id = "test_session"
        
        # 測試完整降級流程（EB-mM → Ollama → LLM）
        # 模擬 EB-mM 不可用
        fallback_model.eb_mm_model.check_available = AsyncMock(return_value=False)
        
        start_time = time.time()
        result = await fallback_model.extract_knowledge(text, user_id, session_id)
        end_time = time.time()
        
        flow_time = end_time - start_time
        
        # 預期整體流程時間 < 2秒（降級到 Ollama）
        assert flow_time < 2.0, f"整體流程時間過長: {flow_time:.2f}秒"
        assert result is not None, "應返回知識資產"
        
        print(f"\n整體降級流程時間: {flow_time:.2f}秒")

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_fallback_with_quality_check_time(self, fallback_model, quality_evaluator):
        """測試包含質量檢查的降級流程時間"""
        text = "測試文本"
        user_id = "test_user"
        session_id = "test_session"
        
        # 創建低質量知識資產（觸發降級）
        low_quality_knowledge = KnowledgeAsset(
            user_id=user_id,
            session_id=session_id,
            timestamp=int(time.time()),
            source_type="dialogue",
            entities=[],  # 空實體，質量低
            triples_json="[]",  # 空三元組，質量低
        )
        
        # 模擬 EB-mM 返回低質量結果
        async def low_quality_extract(*args, **kwargs):
            await asyncio.sleep(0.1)
            return low_quality_knowledge
        
        fallback_model.eb_mm_model.extract_knowledge = low_quality_extract
        
        start_time = time.time()
        result = await fallback_model.extract_knowledge(text, user_id, session_id)
        end_time = time.time()
        
        flow_time = end_time - start_time
        
        # 預期包含質量檢查的流程時間 < 2秒
        assert flow_time < 2.0, f"包含質量檢查的流程時間過長: {flow_time:.2f}秒"
        assert result is not None, "應返回知識資產"
        
        print(f"\n包含質量檢查的降級流程時間: {flow_time:.2f}秒")

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_fallback_requests(self, fallback_model):
        """測試並發降級請求的性能"""
        texts = ["測試文本1", "測試文本2", "測試文本3"]
        user_id = "test_user"
        
        async def extract_knowledge(text: str, index: int) -> tuple[int, float]:
            """提取知識並記錄時間"""
            session_id = f"test_session_{index}"
            start_time = time.time()
            result = await fallback_model.extract_knowledge(text, user_id, session_id)
            end_time = time.time()
            return index, end_time - start_time
        
        # 並發執行多個請求
        start_time = time.time()
        tasks = [extract_knowledge(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 驗證結果
        assert len(results) == len(texts), "應返回所有結果"
        
        # 計算平均響應時間
        avg_response_time = sum(r[1] for r in results) / len(results)
        
        print(f"\n並發請求數: {len(texts)}")
        print(f"總耗時: {total_time:.2f}秒")
        print(f"平均響應時間: {avg_response_time:.2f}秒")
        
        # 預期並發處理時間不應超過單個請求時間的2倍
        assert total_time < 2.0, f"並發處理時間過長: {total_time:.2f}秒"

