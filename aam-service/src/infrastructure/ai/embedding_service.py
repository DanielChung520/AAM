"""
@purpose: 封裝 Sentence Transformer 模型，提供文本向量化服務
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import List

from sentence_transformers import SentenceTransformer

from src.config.settings import AISettings, get_settings


class EmbeddingService:
    """文本向量化服務"""

    def __init__(self, settings: AISettings | None = None):
        """
        初始化向量化服務
        
        Args:
            settings: AI 配置設置，如果為 None 則從全局配置加載
        """
        if settings is None:
            settings = get_settings().ai
        
        self.settings = settings
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """
        獲取 Sentence Transformer 模型（懶加載）
        
        Returns:
            SentenceTransformer 模型實例
        """
        if self._model is None:
            self._model = SentenceTransformer(
                self.settings.embedding_model,
                cache_folder=self.settings.model_cache_dir,
            )
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """
        對單個文本進行向量化
        
        Args:
            text: 要向量化的文本
            
        Returns:
            向量列表（浮點數列表）
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量對文本進行向量化
        
        Args:
            texts: 要向量化的文本列表
            
        Returns:
            向量列表的列表
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, batch_size=32
        )
        return [embedding.tolist() for embedding in embeddings]

