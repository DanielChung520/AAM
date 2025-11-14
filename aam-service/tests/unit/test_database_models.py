"""
@purpose: 測試數據庫 ORM 模型的轉換和驗證
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime

import pytest

# 測試 UserProfileTable 需要 SQLAlchemy，如果沒有安裝則跳過
try:
    from src.infrastructure.database.models import UserProfileTable
    from src.models.domain.database import UserProfileDB
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="SQLAlchemy not available")


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not available")
class TestUserProfileTable:
    """測試 UserProfileTable ORM 模型"""

    def test_to_domain_model(self):
        """測試轉換為領域模型"""
        table_record = UserProfileTable(
            user_id="user123",
            style_tags={"formal": 10, "casual": 5},
            sentiment_history={"positive": 20, "negative": 3},
            last_updated=datetime.utcnow(),
        )
        
        domain_model = table_record.to_domain_model()
        
        assert isinstance(domain_model, UserProfileDB)
        assert domain_model.user_id == "user123"
        assert domain_model.style_tags == {"formal": 10, "casual": 5}
        assert domain_model.sentiment_history == {"positive": 20, "negative": 3}

    def test_from_domain_model(self):
        """測試從領域模型創建"""
        domain_model = UserProfileDB(
            user_id="user123",
            style_tags={"formal": 10},
            sentiment_history={"positive": 20},
            last_updated=datetime.utcnow(),
        )
        
        table_record = UserProfileTable.from_domain_model(domain_model)
        
        assert isinstance(table_record, UserProfileTable)
        assert table_record.user_id == "user123"
        assert table_record.style_tags == {"formal": 10}
        assert table_record.sentiment_history == {"positive": 20}

    def test_table_metadata(self):
        """測試表元數據"""
        assert UserProfileTable.__tablename__ == "user_profiles"
        assert hasattr(UserProfileTable, "user_id")
        assert hasattr(UserProfileTable, "style_tags")
        assert hasattr(UserProfileTable, "sentiment_history")
        assert hasattr(UserProfileTable, "last_updated")
