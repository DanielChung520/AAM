"""
@purpose: 測試 ChromaDB 知識庫的保存和搜索功能
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# 在導入前 Mock chromadb 以避免依賴問題
import sys
from unittest.mock import Mock

mock_chromadb = Mock()
mock_chromadb.HttpClient = Mock()
sys.modules['chromadb'] = mock_chromadb
sys.modules['chromadb.config'] = Mock()
sys.modules['chromadb.config'].Settings = Mock

from src.config.settings import ChromaDBSettings
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.ai.embedding_service import EmbeddingService
from src.models.domain.database import KnowledgeAsset


class TestChromaKnowledgeStore:
    """測試 ChromaKnowledgeStore 類"""

    @pytest.fixture
    def mock_chromadb_client(self):
        """創建模擬 ChromaDB 客戶端"""
        client = Mock()
        collection = Mock()
        client.get_or_create_collection.return_value = collection
        return client, collection

    @pytest.fixture
    def mock_embedding_service(self):
        """創建模擬向量化服務"""
        service = Mock(spec=EmbeddingService)
        service.embed_text.return_value = [0.1] * 384  # 模擬向量
        return service

    @pytest.fixture
    def knowledge_asset(self):
        """創建測試用的知識資產"""
        return KnowledgeAsset(
            user_id="user123",
            session_id="session123",
            timestamp=1706342400,
            source_type="dialogue",
            entities=["Python", "AI"],
            triples_json='[{"subject": "AI", "predicate": "is", "object": "technology"}]',
        )

    @patch("src.infrastructure.database.chroma_knowledge_store.chromadb.HttpClient")
    def test_init(self, mock_client_class, mock_chromadb_client, mock_embedding_service):
        """測試初始化"""
        mock_client, mock_collection = mock_chromadb_client
        mock_client_class.return_value = mock_client
        
        settings = ChromaDBSettings(
            chromadb_host="localhost",
            chromadb_port=8001,
            chromadb_collection_name="test_collection",
        )
        
        store = ChromaKnowledgeStore(
            chromadb_settings=settings,
            embedding_service=mock_embedding_service,
        )
        
        assert store.settings == settings
        assert store.embedding_service == mock_embedding_service
        mock_client.get_or_create_collection.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.infrastructure.database.chroma_knowledge_store.chromadb.HttpClient")
    async def test_save(
        self, mock_client_class, mock_chromadb_client, mock_embedding_service, knowledge_asset
    ):
        """測試保存知識資產"""
        mock_client, mock_collection = mock_chromadb_client
        mock_client_class.return_value = mock_client
        
        store = ChromaKnowledgeStore(embedding_service=mock_embedding_service)
        store.collection = mock_collection
        
        text_content = "User query: What is AI? AI response: AI is artificial intelligence."
        
        await store.save(knowledge_asset, text_content)
        
        # 驗證向量化服務被調用
        mock_embedding_service.embed_text.assert_called_once_with(text_content)
        
        # 驗證 ChromaDB collection.add 被調用
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert "ids" in call_args.kwargs
        assert "embeddings" in call_args.kwargs
        assert "metadatas" in call_args.kwargs
        assert "documents" in call_args.kwargs

    @pytest.mark.asyncio
    @patch("src.infrastructure.database.chroma_knowledge_store.chromadb.HttpClient")
    async def test_search(
        self, mock_client_class, mock_chromadb_client, mock_embedding_service
    ):
        """測試搜索知識"""
        mock_client, mock_collection = mock_chromadb_client
        mock_client_class.return_value = mock_client
        
        store = ChromaKnowledgeStore(embedding_service=mock_embedding_service)
        store.collection = mock_collection
        
        # 模擬搜索結果
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["Content 1", "Content 2"]],
            "distances": [[0.1, 0.2]],
        }
        
        results = await store.search("test query", "user123", limit=10)
        
        # 驗證向量化服務被調用
        mock_embedding_service.embed_text.assert_called_once_with("test query")
        
        # 驗證 ChromaDB collection.query 被調用
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert "query_embeddings" in call_args.kwargs
        assert call_args.kwargs["n_results"] == 10
        assert call_args.kwargs["where"] == {"user_id": "user123"}
        
        # 驗證返回結果
        assert len(results) == 2
        assert results[0].source == "chromadb:doc1"
        assert results[0].content == "Content 1"
        assert 0.0 <= results[0].score <= 1.0

    @pytest.mark.asyncio
    @patch("src.infrastructure.database.chroma_knowledge_store.chromadb.HttpClient")
    async def test_search_empty_results(
        self, mock_client_class, mock_chromadb_client, mock_embedding_service
    ):
        """測試搜索無結果的情況"""
        mock_client, mock_collection = mock_chromadb_client
        mock_client_class.return_value = mock_client
        
        store = ChromaKnowledgeStore(embedding_service=mock_embedding_service)
        store.collection = mock_collection
        
        # 模擬空搜索結果
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "distances": [[]],
        }
        
        results = await store.search("test query", "user123")
        assert len(results) == 0

