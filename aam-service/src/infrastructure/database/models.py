"""
@purpose: 定義 PostgreSQL 數據庫的 SQLAlchemy ORM 模型
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from typing import Dict

from sqlalchemy import JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.models.domain.database import UserProfileDB


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類"""
    pass


class UserProfileTable(Base):
    """用戶畫像數據表模型 - 對應 PostgreSQL user_profiles 表"""
    
    __tablename__ = "user_profiles"
    
    user_id: Mapped[str] = mapped_column(
        String(255), primary_key=True, comment="用戶 ID（主鍵）"
    )
    style_tags: Mapped[Dict[str, int]] = mapped_column(
        JSONB, nullable=False, default=dict, comment="風格標籤字典"
    )
    sentiment_history: Mapped[Dict[str, int]] = mapped_column(
        JSONB, nullable=False, default=dict, comment="情感歷史字典"
    )
    last_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="最後更新時間",
    )

    def to_domain_model(self) -> UserProfileDB:
        """
        轉換為領域模型（UserProfileDB）
        
        Returns:
            UserProfileDB 對象
        """
        return UserProfileDB(
            user_id=self.user_id,
            style_tags=self.style_tags,
            sentiment_history=self.sentiment_history,
            last_updated=self.last_updated,
        )

    @classmethod
    def from_domain_model(cls, profile: UserProfileDB) -> "UserProfileTable":
        """
        從領域模型創建數據表模型
        
        Args:
            profile: UserProfileDB 對象
            
        Returns:
            UserProfileTable 對象
        """
        return cls(
            user_id=profile.user_id,
            style_tags=profile.style_tags,
            sentiment_history=profile.sentiment_history,
            last_updated=profile.last_updated,
        )

