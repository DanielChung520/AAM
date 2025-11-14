"""
@purpose: LangChain Embedding 模型單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from src.infrastructure.ai.langchain_embedding_model import LangChainEmbeddingModel
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights


class TestLangChainEmbeddingModel:
    """LangChain Embedding 模型測試類"""

    @pytest.fixture
    def mock_settings(self):
        """創建 Mock 配置"""
        settings = Mock()
        settings.langchain_embedding_model = "gpt-3.5-turbo"
        settings.langchain_embedding_provider = "openai"
        settings.langchain_embedding_api_key = "test-api-key"
        settings.langchain_embedding_timeout = 120
        return settings

    @pytest.fixture
    def mock_llm(self):
        """創建 Mock LLM"""
        llm = AsyncMock()
        return llm

    @pytest.fixture
    def langchain_model(self, mock_settings):
        """創建 LangChain Embedding 模型實例（使用 Mock）"""
        with patch("src.infrastructure.ai.langchain_embedding_model.ChatOpenAI") as mock_chat:
            mock_chat_instance = AsyncMock()
            mock_chat.return_value = mock_chat_instance
            
            model = LangChainEmbeddingModel(
                model_name="gpt-3.5-turbo",
                api_key="test-api-key",
                timeout=120,
                settings=mock_settings,
            )
            model.llm = mock_chat_instance
            return model

    @pytest.mark.asyncio
    async def test_check_available_success(self, langchain_model):
        """測試服務可用性檢查成功"""
        # 模擬 LLM 返回成功響應
        mock_response = MagicMock()
        mock_response.content = "OK"
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        # 創建測試鏈
        with patch("src.infrastructure.ai.langchain_embedding_model.ChatPromptTemplate") as mock_prompt:
            mock_chain = AsyncMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)
            mock_prompt.from_messages.return_value = mock_chain
            
            result = await langchain_model.check_available()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_available_failure(self, langchain_model):
        """測試服務可用性檢查失敗"""
        # 模擬 LLM 拋出異常
        langchain_model.llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        
        result = await langchain_model.check_available()
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_ner_success(self, langchain_model):
        """測試 NER 提取成功"""
        # 模擬 LLM 返回 JSON 結果
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "entities": ["實體1", "實體2", "實體3"],
            "entity_types": {
                "實體1": "人名",
                "實體2": "地名",
                "實體3": "組織名"
            }
        })
        
        # 模擬鏈調用
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        # 模擬 JSON 解析器
        with patch.object(langchain_model.json_parser, "parse", return_value={
            "entities": ["實體1", "實體2", "實體3"],
            "entity_types": {}
        }):
            entities = await langchain_model._extract_ner("測試文本包含實體1和實體2")
            assert isinstance(entities, list)
            assert len(entities) == 3
            assert "實體1" in entities

    @pytest.mark.asyncio
    async def test_extract_ner_empty_result(self, langchain_model):
        """測試 NER 提取返回空結果"""
        # 模擬 LLM 返回空結果
        mock_response = MagicMock()
        mock_response.content = json.dumps({"entities": []})
        
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        with patch.object(langchain_model.json_parser, "parse", return_value={"entities": []}):
            entities = await langchain_model._extract_ner("測試文本")
            assert isinstance(entities, list)
            assert len(entities) == 0

    @pytest.mark.asyncio
    async def test_extract_ner_error_handling(self, langchain_model):
        """測試 NER 提取錯誤處理"""
        # 模擬 LLM 拋出異常
        langchain_model.llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        
        entities = await langchain_model._extract_ner("測試文本")
        assert isinstance(entities, list)
        assert len(entities) == 0

    @pytest.mark.asyncio
    async def test_extract_kt_success(self, langchain_model):
        """測試 KT 提取成功"""
        # 模擬 LLM 返回三元組結果
        triples_data = [
            {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
            {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"},
        ]
        
        mock_response = MagicMock()
        mock_response.content = json.dumps({"triples": triples_data})
        
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        with patch.object(langchain_model.json_parser, "parse", return_value={"triples": triples_data}):
            triples = await langchain_model._extract_kt("測試文本")
            assert isinstance(triples, list)
            assert len(triples) == 2
            assert all("subject" in t and "predicate" in t and "object" in t for t in triples)

    @pytest.mark.asyncio
    async def test_extract_kt_validation(self, langchain_model):
        """測試 KT 提取三元組驗證"""
        # 模擬 LLM 返回不完整的三元組
        incomplete_triples = [
            {"subject": "主體1", "predicate": "謂詞1"},  # 缺少 object
            {"subject": "主體2", "object": "客體2"},  # 缺少 predicate
            {"subject": "主體3", "predicate": "謂詞3", "object": "客體3"},  # 完整
        ]
        
        mock_response = MagicMock()
        mock_response.content = json.dumps({"triples": incomplete_triples})
        
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        with patch.object(langchain_model.json_parser, "parse", return_value={"triples": incomplete_triples}):
            triples = await langchain_model._extract_kt("測試文本")
            # 應該只返回完整的三元組
            assert len(triples) == 1
            assert triples[0]["subject"] == "主體3"

    @pytest.mark.asyncio
    async def test_extract_knowledge_success(self, langchain_model):
        """測試 extract_knowledge 方法成功"""
        # 模擬 NER 和 KT 提取
        langchain_model._extract_ner = AsyncMock(return_value=["實體1", "實體2"])
        langchain_model._extract_kt = AsyncMock(return_value=[
            {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"}
        ])
        
        result = await langchain_model.extract_knowledge(
            "測試文本", "test_user", "test_session"
        )
        
        assert isinstance(result, KnowledgeAsset)
        assert result.user_id == "test_user"
        assert result.session_id == "test_session"
        assert len(result.entities) == 2
        assert len(json.loads(result.triples_json)) == 1

    @pytest.mark.asyncio
    async def test_extract_knowledge_empty_text(self, langchain_model):
        """測試 extract_knowledge 處理空文本"""
        result = await langchain_model.extract_knowledge(
            "", "test_user", "test_session"
        )
        
        assert isinstance(result, KnowledgeAsset)
        assert result.entities == []
        assert result.triples_json == "[]"

    @pytest.mark.asyncio
    async def test_analyze_personality_success(self, langchain_model):
        """測試個性分析成功"""
        # 模擬 LLM 返回個性分析結果
        personality_data = {
            "style_tags": ["formal", "technical"],
            "emotion": "positive",
            "language_patterns": ["簡潔", "專業"],
            "tone": "專業",
            "confidence_score": 0.85
        }
        
        mock_response = MagicMock()
        mock_response.content = json.dumps(personality_data)
        
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        with patch.object(langchain_model.json_parser, "parse", return_value=personality_data):
            result = await langchain_model.analyze_personality("測試文本")
            
            assert isinstance(result, PersonalityInsights)
            assert result.sentiment == "positive"
            assert len(result.style_tags) == 2
            assert "formal" in result.style_tags
            assert result.confidence_score == 0.85

    @pytest.mark.asyncio
    async def test_analyze_personality_empty_text(self, langchain_model):
        """測試個性分析處理空文本"""
        result = await langchain_model.analyze_personality("")
        
        assert isinstance(result, PersonalityInsights)
        assert result.sentiment == "neutral"
        assert len(result.style_tags) == 0
        assert result.confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_analyze_personality_style_tags_list(self, langchain_model):
        """測試個性分析處理列表格式的 style_tags"""
        # 模擬返回列表格式的 style_tags
        personality_data = {
            "style_tags": ["formal", "technical", "casual"],
            "emotion": "neutral",
            "language_patterns": [],
            "confidence_score": 0.7
        }
        
        mock_response = MagicMock()
        mock_response.content = json.dumps(personality_data)
        
        langchain_model.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        with patch.object(langchain_model.json_parser, "parse", return_value=personality_data):
            result = await langchain_model.analyze_personality("測試文本")
            
            assert isinstance(result.style_tags, dict)
            assert len(result.style_tags) == 3
            assert all(result.style_tags[tag] == 1 for tag in ["formal", "technical", "casual"])

    @pytest.mark.asyncio
    async def test_analyze_personality_error_handling(self, langchain_model):
        """測試個性分析錯誤處理"""
        # 模擬 LLM 拋出異常
        langchain_model.llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception):
            await langchain_model.analyze_personality("測試文本")

