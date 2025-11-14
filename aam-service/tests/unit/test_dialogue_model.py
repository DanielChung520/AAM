"""
@purpose: 測試對話歸檔消息模型的數據驗證和序列化
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.domain.dialogue import DialogueArchiveMessage


class TestDialogueArchiveMessage:
    """測試 DialogueArchiveMessage 模型"""

    def test_valid_message(self):
        """測試有效的對話歸檔消息"""
        msg = DialogueArchiveMessage(
            dialog_id="dialog123",
            user_id="user123",
            timestamp=datetime.now(),
            turn=1,
            user_query="Hello",
            ai_response="Hi there!",
        )
        assert msg.dialog_id == "dialog123"
        assert msg.user_id == "user123"
        assert msg.turn == 1
        assert msg.user_query == "Hello"
        assert msg.ai_response == "Hi there!"

    def test_timestamp_from_iso_string(self):
        """測試從 ISO 8601 字符串解析時間戳"""
        msg = DialogueArchiveMessage(
            dialog_id="dialog123",
            user_id="user123",
            timestamp="2025-11-12T10:00:00Z",
            turn=1,
            user_query="Hello",
            ai_response="Hi there!",
        )
        assert isinstance(msg.timestamp, datetime)

    def test_invalid_turn(self):
        """測試無效的對話輪次"""
        with pytest.raises(ValidationError):
            DialogueArchiveMessage(
                dialog_id="dialog123",
                user_id="user123",
                timestamp=datetime.now(),
                turn=0,  # 必須 >= 1
                user_query="Hello",
                ai_response="Hi there!",
            )

    def test_json_serialization(self):
        """測試 JSON 序列化"""
        msg = DialogueArchiveMessage(
            dialog_id="dialog123",
            user_id="user123",
            timestamp=datetime(2025, 11, 12, 10, 0, 0),
            turn=1,
            user_query="Hello",
            ai_response="Hi there!",
        )
        json_str = msg.model_dump_json()
        assert "dialog123" in json_str
        assert "user123" in json_str

