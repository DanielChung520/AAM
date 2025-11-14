"""
@purpose: 定義記憶服務的抽象接口，實現依賴倒置原則
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from abc import ABC, abstractmethod

from src.models.api.mcp import EnrichedMCP, PartialMCP
from src.models.domain.dialogue import DialogueArchiveMessage


class IMemoryService(ABC):
    """記憶服務抽象接口"""

    @abstractmethod
    async def enrich(self, mcp: PartialMCP) -> EnrichedMCP:
        """
        豐富化 MCP（同步 API 調用）
        
        Args:
            mcp: 部分 MCP（請求體）
            
        Returns:
            豐富化後的 MCP（響應體）
        """
        pass

    @abstractmethod
    async def archive(self, message: DialogueArchiveMessage) -> None:
        """
        歸檔對話消息（異步處理）
        
        Args:
            message: 對話歸檔消息
        """
        pass

