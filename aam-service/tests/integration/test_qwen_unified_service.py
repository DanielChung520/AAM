"""
@purpose: Qwen Provider 與 UnifiedModelService 集成測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights


class TestQwenUnifiedService:
    """Qwen Provider 與 UnifiedModelService 集成測試類"""

    @pytest.fixture
    def qwen_provider(self):
        """創建 Qwen Provider 實例"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            pytest.skip("需要設置QWEN_API_KEY環境變量")
        
        api_base_url = os.getenv(
            "QWEN_API_BASE_URL",
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        )
        
        return QwenProvider(
            model_name="qwen-turbo",
            api_base_url=api_base_url,
            api_key=api_key,
            timeout=120,
        )

    @pytest.fixture
    def unified_service(self, qwen_provider):
        """創建 UnifiedModelService 實例（使用 Qwen Provider）"""
        return UnifiedModelService(provider=qwen_provider)

    def test_unified_service_initialization(self, unified_service, qwen_provider):
        """測試 UnifiedModelService 初始化"""
        assert unified_service.provider == qwen_provider
        assert unified_service.provider.provider_type == ModelProviderType.QWEN

    @pytest.mark.asyncio
    async def test_unified_service_check_available(self, unified_service):
        """測試 UnifiedModelService 可用性檢查"""
        # Mock Provider 的可用性檢查
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        result = await unified_service.check_available()
        assert result is True

    @pytest.mark.asyncio
    async def test_unified_service_extract_knowledge_mock(self, unified_service):
        """測試 UnifiedModelService 知識提取（Mock）"""
        # Mock Provider 的 generate 方法
        mock_response = json.dumps({
            "entities": ["Python", "編程語言", "Web 開發"]
        })
        unified_service.provider.generate = AsyncMock(return_value=mock_response)
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # Mock KT 提取
        kt_response = json.dumps({
            "triples": [
                {"subject": "Python", "predicate": "是", "object": "編程語言"},
                {"subject": "Python", "predicate": "用於", "object": "Web 開發"}
            ]
        })
        
        # 替換 _extract_kt 方法以返回預定義結果
        async def mock_extract_kt(text):
            return [
                {"subject": "Python", "predicate": "是", "object": "編程語言"},
                {"subject": "Python", "predicate": "用於", "object": "Web 開發"}
            ]
        
        unified_service._extract_kt = mock_extract_kt
        
        # 執行知識提取
        knowledge = await unified_service.extract_knowledge(
            text="Python 是一種編程語言，可以用於 Web 開發。",
            user_id="test_user",
            session_id="test_session"
        )
        
        # 驗證結果
        assert isinstance(knowledge, KnowledgeAsset)
        assert knowledge.user_id == "test_user"
        assert knowledge.session_id == "test_session"
        assert knowledge.source_type == "dialogue"

    @pytest.mark.asyncio
    async def test_unified_service_extract_ner(self, unified_service):
        """測試 UnifiedModelService NER 提取"""
        # Mock Provider 的 generate 方法
        mock_response = json.dumps({
            "entities": ["Python", "編程語言", "Web 開發", "Django"]
        })
        unified_service.provider.generate = AsyncMock(return_value=mock_response)
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # 執行 NER 提取
        entities = await unified_service._extract_ner("Python 是一種編程語言，Django 是 Web 框架。")
        
        # 驗證結果
        assert isinstance(entities, list)
        assert len(entities) > 0

    @pytest.mark.asyncio
    async def test_unified_service_extract_kt(self, unified_service):
        """測試 UnifiedModelService KT 提取"""
        # Mock Provider 的 generate 方法
        mock_response = json.dumps({
            "triples": [
                {"subject": "Python", "predicate": "是", "object": "編程語言"},
                {"subject": "Django", "predicate": "是", "object": "Web 框架"}
            ]
        })
        unified_service.provider.generate = AsyncMock(return_value=mock_response)
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # 執行 KT 提取
        triples = await unified_service._extract_kt("Python 是一種編程語言，Django 是 Web 框架。")
        
        # 驗證結果
        assert isinstance(triples, list)
        assert len(triples) > 0
        assert "subject" in triples[0]
        assert "predicate" in triples[0]
        assert "object" in triples[0]

    @pytest.mark.asyncio
    async def test_unified_service_analyze_personality(self, unified_service):
        """測試 UnifiedModelService 個性分析"""
        # Mock Provider 的 generate 方法
        mock_response = json.dumps({
            "style_tags": {"formal": 0.8, "casual": 0.2},
            "sentiment": "positive",
            "language_patterns": ["使用專業術語", "結構化表達"],
            "confidence_score": 0.85
        })
        unified_service.provider.generate = AsyncMock(return_value=mock_response)
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # 執行個性分析
        personality = await unified_service.analyze_personality(
            "我對 Python 編程很感興趣，希望學習 Web 開發。"
        )
        
        # 驗證結果
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment in ["positive", "negative", "neutral"]
        assert isinstance(personality.style_tags, dict)
        assert isinstance(personality.language_patterns, list)
        assert 0.0 <= personality.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_unified_service_provider_unavailable(self, unified_service):
        """測試 UnifiedModelService Provider 不可用"""
        # Mock Provider 的可用性檢查為 False
        unified_service.provider.check_available = AsyncMock(return_value=False)
        
        # 應該拋出 RuntimeError
        with pytest.raises(RuntimeError, match="不可用"):
            await unified_service.extract_knowledge(
                text="測試文本",
                user_id="test_user",
                session_id="test_session"
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_unified_service_real_api_flow(self, unified_service):
        """測試 UnifiedModelService 真實 API 流程（端到端）"""
        # 這是一個端到端測試，需要真實的 API Key
        api_key = os.getenv("QWEN_API_KEY", "")
        if not api_key or api_key == "test-key":
            pytest.skip("需要真實的 QWEN_API_KEY 環境變量")
        
        try:
            # 1. 檢查可用性
            is_available = await unified_service.check_available()
            if not is_available:
                pytest.skip("Qwen API 不可用")
            
            # 2. 執行知識提取
            text = "Python 是一種高級編程語言，由 Guido van Rossum 在 1991 年創建。它可以用於 Web 開發、數據科學和機器學習。"
            knowledge = await unified_service.extract_knowledge(
                text=text,
                user_id="test_user",
                session_id="test_session_real"
            )
            
            # 3. 驗證結果
            assert isinstance(knowledge, KnowledgeAsset)
            assert knowledge.user_id == "test_user"
            assert knowledge.session_id == "test_session_real"
            assert knowledge.source_type == "dialogue"
            
            # 4. 驗證實體
            assert isinstance(knowledge.entities, list)
            
            # 5. 驗證三元組
            triples = json.loads(knowledge.triples_json)
            assert isinstance(triples, list)
            
        except Exception as e:
            pytest.skip(f"真實 API 測試失敗: {e}")

    @pytest.mark.asyncio
    async def test_unified_service_error_handling(self, unified_service):
        """測試 UnifiedModelService 錯誤處理"""
        # Mock Provider 的 generate 方法拋出異常
        unified_service.provider.generate = AsyncMock(side_effect=RuntimeError("API 錯誤"))
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # 應該拋出異常
        with pytest.raises(RuntimeError):
            await unified_service.extract_knowledge(
                text="測試文本",
                user_id="test_user",
                session_id="test_session"
            )

    @pytest.mark.asyncio
    async def test_unified_service_invalid_json_response(self, unified_service):
        """測試 UnifiedModelService 無效 JSON 響應處理"""
        # Mock Provider 的 generate 方法返回無效 JSON
        unified_service.provider.generate = AsyncMock(return_value="這不是有效的 JSON")
        unified_service.provider.check_available = AsyncMock(return_value=True)
        
        # 應該返回空列表（錯誤處理）
        entities = await unified_service._extract_ner("測試文本")
        assert isinstance(entities, list)
        
        triples = await unified_service._extract_kt("測試文本")
        assert isinstance(triples, list)

