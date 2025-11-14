"""
@purpose: 定義數據庫 Schema 的數據模型，包括 ChromaDB 和 PostgreSQL
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
from datetime import datetime
from typing import Dict, List, Literal

from pydantic import BaseModel, Field, field_serializer

from src.models.domain.triple_categories import get_category_summary


class KnowledgeAsset(BaseModel):
    """知識資產模型 - ChromaDB Collection: knowledge_assets"""
    user_id: str = Field(..., description="用戶 ID")
    session_id: str = Field(..., description="會話 ID")
    timestamp: int = Field(..., description="Unix 時間戳")
    source_type: Literal["dialogue", "document"] = Field(
        ..., description="來源類型"
    )
    entities: List[str] = Field(
        default_factory=list, description="命名實體列表"
    )
    triples_json: str = Field(
        default="[]", description="知識三元組 JSON 字符串"
    )

    def to_chromadb_metadata(self) -> dict:
        """轉換為 ChromaDB 元數據格式"""
        # 從三元組 JSON 中提取分類標籤摘要
        triple_categories = ""
        try:
            if self.triples_json and self.triples_json != "[]":
                triples = json.loads(self.triples_json)
                if isinstance(triples, list):
                    triple_categories = get_category_summary(triples)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失敗，使用空字符串
            triple_categories = ""
        
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "source_type": self.source_type,
            "entities": ",".join(self.entities) if self.entities else "",
            "triples_json": self.triples_json,
            "triple_categories": triple_categories,
        }

    @classmethod
    def from_chromadb_metadata(cls, metadata: dict) -> "KnowledgeAsset":
        """從 ChromaDB 元數據創建 KnowledgeAsset"""
        entities_str = metadata.get("entities", "")
        entities = entities_str.split(",") if entities_str else []
        return cls(
            user_id=metadata["user_id"],
            session_id=metadata["session_id"],
            timestamp=metadata["timestamp"],
            source_type=metadata["source_type"],
            entities=entities,
            triples_json=metadata.get("triples_json", "[]"),
        )


class UserProfileDB(BaseModel):
    """用戶畫像數據庫模型 - PostgreSQL Table: user_profiles"""
    user_id: str = Field(..., description="用戶 ID（主鍵）")
    style_tags: Dict[str, int] = Field(
        default_factory=dict, description="風格標籤字典，例如：{'formal': 10, 'casual': 5}"
    )
    sentiment_history: Dict[str, int] = Field(
        default_factory=dict, description="情感歷史字典，例如：{'positive': 20, 'negative': 3}"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="最後更新時間"
    )

    @field_serializer("last_updated")
    def serialize_last_updated(self, value: datetime) -> str:
        """序列化時間戳為 ISO 8601 字符串"""
        return value.isoformat()

