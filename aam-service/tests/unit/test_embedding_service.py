"""
@purpose: 測試向量化服務的功能和性能
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock sentence_transformers 模塊以避免依賴問題
mock_sentence_transformers = MagicMock()
sys.modules['sentence_transformers'] = mock_sentence_transformers

from src.config.settings import AISettings
from src.infrastructure.ai.embedding_service import EmbeddingService


class TestEmbeddingService:
    """測試 EmbeddingService 類"""

    def test_init_with_settings(self):
        """測試使用提供的設置初始化"""
        settings = AISettings(
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            model_cache_dir="./test_cache",
        )
        service = EmbeddingService(settings=settings)
        assert service.settings == settings

    def test_init_without_settings(self):
        """測試從全局配置初始化"""
        service = EmbeddingService()
        assert service.settings is not None

    @patch("src.infrastructure.ai.embedding_service.SentenceTransformer")
    def test_embed_text(self, mock_transformer_class):
        """測試單文本向量化"""
        # 模擬 SentenceTransformer
        mock_model = Mock()
        # 創建模擬向量（使用 list 而不是 numpy array 以避免依賴）
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = [0.1] * 384
        mock_model.encode.return_value = mock_embedding
        mock_transformer_class.return_value = mock_model
        
        service = EmbeddingService()
        service._model = mock_model  # 設置模擬模型
        
        text = "This is a test sentence."
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
        mock_model.encode.assert_called_once_with(text, convert_to_numpy=True)

    @patch("src.infrastructure.ai.embedding_service.SentenceTransformer")
    def test_embed_batch(self, mock_transformer_class):
        """測試批量文本向量化"""
        # 模擬 SentenceTransformer
        mock_model = Mock()
        # 創建模擬向量列表
        mock_embeddings = [
            Mock(tolist=lambda: [0.1] * 384),
            Mock(tolist=lambda: [0.2] * 384),
            Mock(tolist=lambda: [0.3] * 384),
        ]
        mock_model.encode.return_value = mock_embeddings
        mock_transformer_class.return_value = mock_model
        
        service = EmbeddingService()
        service._model = mock_model  # 設置模擬模型
        
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
        ]
        embeddings = service.embed_batch(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)
        mock_model.encode.assert_called_once_with(
            texts, convert_to_numpy=True, batch_size=32
        )

    def test_embed_batch_empty(self):
        """測試空批量向量化"""
        service = EmbeddingService()
        service._model = Mock()  # 設置模擬模型以避免實際加載
        embeddings = service.embed_batch([])
        assert embeddings == []

    @patch("src.infrastructure.ai.embedding_service.SentenceTransformer")
    def test_model_lazy_loading(self, mock_transformer_class):
        """測試模型懶加載"""
        mock_model = Mock()
        mock_transformer_class.return_value = mock_model
        
        service = EmbeddingService()
        # 第一次訪問應該加載模型
        model1 = service.model
        # 第二次訪問應該返回同一個實例
        model2 = service.model
        assert model1 is model2
        assert model1 is mock_model
        # 驗證 SentenceTransformer 只被調用一次
        assert mock_transformer_class.call_count == 1

