"""
@purpose: 定義用戶畫像存儲的抽象接口，實現 Repository Pattern
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.models.domain.database import UserProfileDB


class IPersonaStore(ABC):
    """用戶畫像存儲抽象接口"""

    @abstractmethod
    async def save_or_update(self, profile: UserProfileDB) -> None:
        """
        保存或更新用戶畫像
        
        Args:
            profile: 用戶畫像數據庫模型
        """
        pass

    @abstractmethod
    async def get(self, user_id: str) -> Optional[UserProfileDB]:
        """
        獲取用戶畫像
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶畫像對象，如果不存在則返回 None
        """
        pass

