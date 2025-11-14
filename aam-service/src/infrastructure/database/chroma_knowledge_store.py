"""
@purpose: 實現 ChromaDB 知識庫，封裝向量數據庫的存取邏輯
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config.settings import ChromaDBSettings, get_settings
from src.core.interfaces.i_knowledge_store import IKnowledgeStore
from src.infrastructure.ai.embedding_service import EmbeddingService
from src.models.api.mcp import RetrievedDoc
from src.models.domain.database import KnowledgeAsset


class ChromaKnowledgeStore(IKnowledgeStore):
    """ChromaDB 知識庫實現"""

    def __init__(
        self,
        chromadb_settings: ChromaDBSettings | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        """
        初始化 ChromaDB 知識庫
        
        Args:
            chromadb_settings: ChromaDB 配置設置，如果為 None 則從全局配置加載
            embedding_service: 向量化服務，如果為 None 則創建新實例
        """
        if chromadb_settings is None:
            chromadb_settings = get_settings().chromadb
        
        self.settings = chromadb_settings
        self.embedding_service = (
            embedding_service if embedding_service else EmbeddingService()
        )
        
        # 初始化 ChromaDB 客戶端
        self.client = chromadb.HttpClient(
            host=self.settings.chromadb_host,
            port=self.settings.chromadb_port,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        # 獲取或創建 collection
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chromadb_collection_name,
            metadata={"description": "知識資產向量存儲"},
        )

    async def save(
        self, knowledge: KnowledgeAsset, text_content: str, doc_id: str | None = None
    ) -> None:
        """
        保存知識資產到向量數據庫
        
        Args:
            knowledge: 知識資產對象
            text_content: 要向量化的文本內容（通常是對話的 user_query + ai_response）
            doc_id: 可選的文檔 ID，如果為 None 則自動生成
        """
        # 向量化文本內容
        embedding = self.embedding_service.embed_text(text_content)
        
        # 轉換元數據
        metadata = knowledge.to_chromadb_metadata()
        
        # 生成文檔 ID（使用 session_id + timestamp 確保唯一性，或使用提供的 doc_id）
        if doc_id is None:
            doc_id = f"{knowledge.session_id}_{knowledge.timestamp}"
        
        # 存儲到 ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text_content],
        )

    async def search(
        self, query: str, user_id: str, limit: int = 10
    ) -> List[RetrievedDoc]:
        """
        搜索相關知識
        
        Args:
            query: 查詢字符串
            user_id: 用戶 ID
            limit: 返回結果數量限制，默認為 10
            
        Returns:
            檢索到的文檔列表
        """
        # 向量化查詢字符串
        query_embedding = self.embedding_service.embed_text(query)
        
        # 執行混合搜索（向量相似度 + 元數據過濾）
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where={"user_id": user_id},  # 元數據過濾
        )
        
        # 轉換為 RetrievedDoc 列表
        retrieved_docs = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                content = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 1.0
                
                # 將距離轉換為相似度分數（1 - normalized_distance）
                # ChromaDB 返回的是 L2 距離，需要轉換為相似度
                score = max(0.0, 1.0 - distance)
                
                retrieved_docs.append(
                    RetrievedDoc(
                        source=f"chromadb:{doc_id}",
                        content=content,
                        score=score,
                    )
                )
        
        return retrieved_docs

