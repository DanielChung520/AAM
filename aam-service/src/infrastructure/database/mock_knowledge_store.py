"""
@purpose: Mock 知識庫實現，用於降級模式或測試
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import List

from src.core.interfaces.i_knowledge_store import IKnowledgeStore
from src.models.api.mcp import RetrievedDoc
from src.models.domain.database import KnowledgeAsset


class MockKnowledgeStore(IKnowledgeStore):
    """Mock 知識庫實現 - 用於降級模式或測試"""
    
    def __init__(self):
        """初始化 Mock 知識庫（不需要實際連接）"""
        self._storage: List[tuple] = []  # 簡單的內存存儲
    
    async def save(
        self, knowledge: KnowledgeAsset, text_content: str
    ) -> None:
        """
        保存知識資產（Mock 實現）
        
        Args:
            knowledge: 知識資產對象
            text_content: 文本內容
        """
        # 簡單的內存存儲（僅用於降級模式）
        self._storage.append((knowledge, text_content))
    
    async def search(
        self, query: str, user_id: str, limit: int = 10
    ) -> List[RetrievedDoc]:
        """
        搜索相關知識（Mock 實現）
        
        Args:
            query: 查詢字符串
            user_id: 用戶 ID
            limit: 返回結果數量限制
            
        Returns:
            檢索到的文檔列表（Mock 實現返回空列表）
        """
        # Mock 實現返回空列表
        return []

