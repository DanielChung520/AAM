"""
@purpose: 定義對話歸檔消息的數據模型，用於 RabbitMQ 消息隊列
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer, field_validator


class DialogueArchiveMessage(BaseModel):
    """對話歸檔消息模型 - RabbitMQ Queue: aam.dialogue.archive"""
    dialog_id: str = Field(..., description="對話 ID")
    user_id: str = Field(..., description="用戶 ID")
    timestamp: datetime = Field(..., description="時間戳（ISO 8601 格式）")
    turn: int = Field(..., ge=1, description="對話輪次")
    user_query: str = Field(..., description="用戶查詢")
    ai_response: str = Field(..., description="AI 回應")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v):
        """解析時間戳，支持 ISO 8601 字符串或 datetime 對象"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """序列化時間戳為 ISO 8601 字符串"""
        return value.isoformat()

