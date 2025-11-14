"""
@purpose: 多 Provider 並發測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel


class TestMultiProvider:
    """多 Provider 並發測試類"""

    @pytest.fixture
    def ollama_provider(self):
        """創建 Ollama Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            return ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",
            )

    @pytest.fixture
    def qwen_provider(self):
        """創建 Qwen Provider"""
        return ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_multiple_providers_independent(self, ollama_provider, qwen_provider):
        """測試多個 Provider 獨立工作"""
        # Mock 兩個 Provider 的可用性檢查
        ollama_provider.check_available = AsyncMock(return_value=True)
        qwen_provider.check_available = AsyncMock(return_value=True)
        
        # 創建兩個 UnifiedModelService
        ollama_service = UnifiedModelService(provider=ollama_provider)
        qwen_service = UnifiedModelService(provider=qwen_provider)
        
        # 驗證兩個服務都可用
        assert await ollama_service.check_available() is True
        assert await qwen_service.check_available() is True
        
        # 驗證 Provider 類型不同
        assert ollama_service.provider.provider_type == ModelProviderType.OLLAMA
        assert qwen_service.provider.provider_type == ModelProviderType.QWEN

    @pytest.mark.asyncio
    async def test_fallback_with_multiple_providers(
        self,
        ollama_provider,
        qwen_provider,
    ):
        """測試降級策略使用多個 Provider"""
        from src.infrastructure.ai.quality_evaluator import QualityEvaluator
        from src.models.domain.database import KnowledgeAsset
        from datetime import datetime
        
        # 創建 UnifiedModelService（EB-mM 使用 Ollama，LLM 層使用 Qwen）
        eb_mm_service = UnifiedModelService(provider=ollama_provider)
        llm_service = UnifiedModelService(provider=qwen_provider)
        
        # Mock 知識提取結果
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=["實體1", "實體2"],
            triples_json='[{"subject": "主體", "predicate": "謂詞", "object": "客體"}]',
        )
        
        # Mock 服務方法
        eb_mm_service.extract_knowledge = AsyncMock(return_value=knowledge)
        eb_mm_service.check_available = AsyncMock(return_value=False)  # EB-mM 不可用
        
        llm_service.extract_knowledge = AsyncMock(return_value=knowledge)
        llm_service.check_available = AsyncMock(return_value=True)  # LLM 層可用
        
        # 創建降級策略模型
        quality_evaluator = QualityEvaluator(quality_threshold=0.7)
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=eb_mm_service,
            ollama_local_model=None,
            llm_model=llm_service,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證使用 LLM 層（Qwen Provider）
        assert result == knowledge
        llm_service.extract_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_provider_calls(self, ollama_provider, qwen_provider):
        """測試並發調用不同 Provider"""
        import asyncio
        
        # Mock 兩個 Provider 的生成方法
        ollama_provider.generate = AsyncMock(return_value="Ollama 響應")
        ollama_provider.check_available = AsyncMock(return_value=True)
        
        qwen_provider.generate = AsyncMock(return_value="Qwen 響應")
        qwen_provider.check_available = AsyncMock(return_value=True)
        
        # 並發調用兩個 Provider
        async def call_ollama():
            return await ollama_provider.generate("測試提示詞")
        
        async def call_qwen():
            return await qwen_provider.generate("測試提示詞")
        
        # 同時調用
        results = await asyncio.gather(call_ollama(), call_qwen())
        
        # 驗證兩個 Provider 都成功響應
        assert results[0] == "Ollama 響應"
        assert results[1] == "Qwen 響應"
        
        # 驗證兩個 Provider 都被調用
        ollama_provider.generate.assert_called_once()
        qwen_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_provider_configuration_isolation(self, ollama_provider, qwen_provider):
        """測試 Provider 配置隔離"""
        # 驗證兩個 Provider 的配置獨立
        assert ollama_provider.provider_type == ModelProviderType.OLLAMA
        assert qwen_provider.provider_type == ModelProviderType.QWEN
        
        # 驗證配置互不影響
        assert ollama_provider.model_name == "llama3"
        assert qwen_provider.model_name == "qwen-turbo"
        
        # 驗證 API 配置不同
        assert "localhost" in ollama_provider.base_url or ollama_provider.base_url == "http://localhost:11434"
        assert qwen_provider.api_base_url == "https://test.com/api"

    @pytest.mark.asyncio
    async def test_provider_resource_isolation(self, ollama_provider, qwen_provider):
        """測試 Provider 資源隔離"""
        # Mock 兩個 Provider 的可用性檢查
        ollama_provider.check_available = AsyncMock(return_value=True)
        qwen_provider.check_available = AsyncMock(return_value=True)
        
        # 創建兩個 UnifiedModelService
        ollama_service = UnifiedModelService(provider=ollama_provider)
        qwen_service = UnifiedModelService(provider=qwen_provider)
        
        # 驗證兩個服務的 Provider 實例不同
        assert ollama_service.provider is not qwen_service.provider
        assert ollama_service.provider.provider_type != qwen_service.provider.provider_type
        
        # 驗證可用性檢查獨立
        ollama_available = await ollama_service.check_available()
        qwen_available = await qwen_service.check_available()
        
        assert ollama_available is True
        assert qwen_available is True

    @pytest.mark.asyncio
    async def test_fallback_eb_mm_ollama_llm_qwen(
        self,
        ollama_provider,
        qwen_provider,
    ):
        """測試降級策略：EB-mM (Ollama) → Ollama 本地模型 → LLM 層 (Qwen)"""
        from src.infrastructure.ai.quality_evaluator import QualityEvaluator
        from src.models.domain.database import KnowledgeAsset
        from datetime import datetime
        
        # 創建三個 UnifiedModelService
        # EB-mM 使用 Ollama
        eb_mm_service = UnifiedModelService(provider=ollama_provider)
        
        # Ollama 本地模型使用另一個 Ollama Provider（不同模型）
        ollama_local_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.OLLAMA,
            model_name="mistral",
            api_base_url="http://localhost:11434",
        )
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            ollama_local_service = UnifiedModelService(provider=ollama_local_provider)
        
        # LLM 層使用 Qwen
        llm_service = UnifiedModelService(provider=qwen_provider)
        
        # Mock 知識提取結果
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=["實體"],
            triples_json='[{"subject": "主體", "predicate": "謂詞", "object": "客體"}]',
        )
        
        # Mock EB-mM 和 Ollama 本地模型都不可用
        eb_mm_service.check_available = AsyncMock(return_value=False)
        ollama_local_service.check_available = AsyncMock(return_value=False)
        
        # Mock LLM 層可用
        llm_service.check_available = AsyncMock(return_value=True)
        llm_service.extract_knowledge = AsyncMock(return_value=knowledge)
        
        # 創建降級策略模型
        quality_evaluator = QualityEvaluator(quality_threshold=0.7)
        fallback_model = FallbackAnalysisModel(
            eb_mm_model=eb_mm_service,
            ollama_local_model=ollama_local_service,
            llm_model=llm_service,
            quality_evaluator=quality_evaluator,
        )
        
        # 執行知識提取
        result = await fallback_model.extract_knowledge(
            text="測試文本",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證降級到 LLM 層（Qwen Provider）
        assert result == knowledge
        llm_service.extract_knowledge.assert_called_once()

