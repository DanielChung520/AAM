"""
@purpose: EB-mM 分析模型單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime

from src.infrastructure.ai.eb_mm_analysis_model import EbMMAnalysisModel
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights


class TestEbMMAnalysisModel:
    """EB-mM 分析模型測試類"""

    @pytest.fixture
    def mock_provider(self):
        """創建 Mock Provider"""
        provider = AsyncMock()
        provider.provider_type = Mock()
        provider.provider_type.value = "ollama"
        provider.check_available = AsyncMock(return_value=True)
        provider.generate = AsyncMock()
        provider.get_config = Mock(return_value={})
        return provider

    @pytest.fixture
    def mock_unified_service(self, mock_provider):
        """創建 Mock UnifiedModelService"""
        service = UnifiedModelService(provider=mock_provider)
        return service

    @pytest.fixture
    def eb_mm_model(self, mock_unified_service):
        """創建 EB-mM 分析模型實例"""
        return EbMMAnalysisModel(unified_model_service=mock_unified_service)

    @pytest.mark.asyncio
    async def test_check_available_success(self, eb_mm_model, mock_provider):
        """測試服務可用性檢查成功"""
        mock_provider.check_available = AsyncMock(return_value=True)
        
        result = await eb_mm_model.check_available()
        assert result is True
        mock_provider.check_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_available_failure(self, eb_mm_model, mock_provider):
        """測試服務可用性檢查失敗"""
        mock_provider.check_available = AsyncMock(return_value=False)
        
        result = await eb_mm_model.check_available()
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_ner_success(self, eb_mm_model, mock_provider):
        """測試 NER 提取成功"""
        # 模擬 Provider 返回 JSON 結果
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "entities": ["實體1", "實體2", "實體3"],
            "entity_types": {
                "實體1": "人名",
                "實體2": "地名",
                "實體3": "組織名"
            },
            "confidence_scores": {
                "實體1": 0.95,
                "實體2": 0.87,
                "實體3": 0.92
            }
        }))
        
        entities = await eb_mm_model._extract_ner("測試文本包含實體1和實體2")
        
        assert isinstance(entities, list)
        assert len(entities) == 3
        assert "實體1" in entities
        assert "實體2" in entities
        assert "實體3" in entities
        mock_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_ner_empty_text(self, eb_mm_model, mock_provider):
        """測試 NER 提取空文本"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "entities": [],
            "entity_types": {},
            "confidence_scores": {}
        }))
        
        entities = await eb_mm_model._extract_ner("")
        
        assert isinstance(entities, list)
        assert len(entities) == 0

    @pytest.mark.asyncio
    async def test_extract_ner_invalid_json(self, eb_mm_model, mock_provider):
        """測試 NER 提取無效 JSON"""
        mock_provider.generate = AsyncMock(return_value="無效的 JSON 響應")
        
        entities = await eb_mm_model._extract_ner("測試文本")
        
        assert isinstance(entities, list)
        assert len(entities) == 0

    @pytest.mark.asyncio
    async def test_extract_ke_success(self, eb_mm_model, mock_provider):
        """測試 KE 提取成功"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "key_points": ["知識點1", "知識點2"],
            "concepts": ["概念1", "概念2"],
            "facts": ["事實1"]
        }))
        
        key_points = await eb_mm_model._extract_ke("測試文本包含重要知識")
        
        assert isinstance(key_points, list)
        assert len(key_points) == 5  # 合併所有知識點
        assert "知識點1" in key_points
        assert "概念1" in key_points
        assert "事實1" in key_points

    @pytest.mark.asyncio
    async def test_extract_ke_empty(self, eb_mm_model, mock_provider):
        """測試 KE 提取空結果"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "key_points": [],
            "concepts": [],
            "facts": []
        }))
        
        key_points = await eb_mm_model._extract_ke("測試文本")
        
        assert isinstance(key_points, list)
        assert len(key_points) == 0

    @pytest.mark.asyncio
    async def test_extract_kt_success(self, eb_mm_model, mock_provider):
        """測試 KT 提取成功"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "triples": [
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
                {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"}
            ]
        }))
        
        triples = await eb_mm_model._extract_kt("測試文本包含關係")
        
        assert isinstance(triples, list)
        assert len(triples) == 2
        assert triples[0]["subject"] == "主體1"
        assert triples[0]["predicate"] == "謂詞1"
        assert triples[0]["object"] == "客體1"

    @pytest.mark.asyncio
    async def test_extract_kt_incomplete_triple(self, eb_mm_model, mock_provider):
        """測試 KT 提取不完整三元組（應該被過濾）"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "triples": [
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
                {"subject": "主體2", "predicate": "謂詞2"},  # 缺少 object
                {"subject": "主體3"}  # 缺少 predicate 和 object
            ]
        }))
        
        triples = await eb_mm_model._extract_kt("測試文本")
        
        assert isinstance(triples, list)
        assert len(triples) == 1  # 只有完整的三元組被保留
        assert triples[0]["subject"] == "主體1"

    @pytest.mark.asyncio
    async def test_extract_knowledge_success(self, eb_mm_model, mock_provider):
        """測試 extract_knowledge 方法成功"""
        # 模擬各個提取方法
        mock_provider.generate = AsyncMock(side_effect=[
            json.dumps({"entities": ["實體1", "實體2"]}),  # NER
            json.dumps({"key_points": ["知識點1"]}),  # KE
            json.dumps({"triples": [{"subject": "主體", "predicate": "謂詞", "object": "客體"}]})  # KT
        ])
        
        knowledge = await eb_mm_model.extract_knowledge(
            text="測試文本",
            user_id="user123",
            session_id="session456"
        )
        
        assert isinstance(knowledge, KnowledgeAsset)
        assert knowledge.user_id == "user123"
        assert knowledge.session_id == "session456"
        assert len(knowledge.entities) == 2
        assert "實體1" in knowledge.entities
        
        # 驗證三元組
        triples = json.loads(knowledge.triples_json)
        assert len(triples) == 1
        assert triples[0]["subject"] == "主體"

    @pytest.mark.asyncio
    async def test_extract_knowledge_service_unavailable(self, eb_mm_model, mock_provider):
        """測試 extract_knowledge 服務不可用"""
        mock_provider.check_available = AsyncMock(return_value=False)
        
        with pytest.raises(RuntimeError, match="EB-mM 模型服務不可用"):
            await eb_mm_model.extract_knowledge(
                text="測試文本",
                user_id="user123",
                session_id="session456"
            )

    @pytest.mark.asyncio
    async def test_analyze_personality_success(self, eb_mm_model, mock_provider):
        """測試個性分析成功"""
        mock_provider.generate = AsyncMock(return_value=json.dumps({
            "style_tags": {"formal": 0.8, "technical": 0.9, "casual": 0.2},
            "sentiment": "positive",
            "language_patterns": ["簡潔", "專業"],
            "tone": "專業",
            "confidence_score": 0.85
        }))
        
        personality = await eb_mm_model.analyze_personality("測試文本")
        
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment == "positive"
        assert personality.confidence_score == 0.85
        assert "formal" in personality.style_tags
        assert personality.style_tags["formal"] == 80  # 轉換為整數
        assert len(personality.language_patterns) == 2

    @pytest.mark.asyncio
    async def test_analyze_personality_invalid_json(self, eb_mm_model, mock_provider):
        """測試個性分析無效 JSON（應該返回默認值）"""
        mock_provider.generate = AsyncMock(return_value="無效的 JSON")
        
        personality = await eb_mm_model.analyze_personality("測試文本")
        
        assert isinstance(personality, PersonalityInsights)
        assert personality.sentiment == "neutral"
        assert personality.confidence_score == 0.5
        assert len(personality.style_tags) == 0

    @pytest.mark.asyncio
    async def test_analyze_personality_service_unavailable(self, eb_mm_model, mock_provider):
        """測試個性分析服務不可用"""
        mock_provider.check_available = AsyncMock(return_value=False)
        
        with pytest.raises(RuntimeError, match="EB-mM 模型服務不可用"):
            await eb_mm_model.analyze_personality("測試文本")

