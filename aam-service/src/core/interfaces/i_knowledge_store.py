"""
@purpose: 定義知識庫的抽象接口，實現 Repository Pattern
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from abc import ABC, abstractmethod
from typing import List

from src.models.api.mcp import RetrievedDoc
from src.models.domain.database import KnowledgeAsset


class IKnowledgeStore(ABC):
    """知識庫抽象接口"""

    @abstractmethod
    async def save(self, knowledge: KnowledgeAsset, text_content: str) -> None:
        """
        保存知識資產到向量數據庫
        
        Args:
            knowledge: 知識資產對象
            text_content: 要向量化的文本內容（通常是對話的 user_query + ai_response）
        """
        pass

    @abstractmethod
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
        pass

