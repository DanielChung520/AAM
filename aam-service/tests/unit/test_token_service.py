"""
@purpose: Token 服務單元測試，驗證 token 發行、驗證和 user_id 提取功能
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import time
from unittest.mock import patch

import pytest
import jwt

from src.core.services.token_service import TokenService
from src.config.settings import SecuritySettings


@pytest.fixture
def mock_security_settings():
    """創建模擬的安全配置"""
    with patch("src.core.services.token_service.get_settings") as mock_get_settings:
        mock_settings = type("Settings", (), {})()
        mock_settings.security = type("SecuritySettings", (), {})()
        mock_settings.security.secret_key = "test-secret-key-12345"
        mock_settings.security.algorithm = "HS256"
        mock_settings.security.token_expire_hours = 24
        mock_settings.security.token_issuer = "aam-agent"
        mock_settings.security.enable_user_id_validation = True
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def token_service(mock_security_settings):
    """創建 Token 服務實例"""
    return TokenService()


class TestTokenService:
    """Token 服務測試類"""

    def test_issue_token_success(self, token_service):
        """測試 token 發行成功"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 驗證 token 不為空
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # 驗證 token 可以解碼
        payload = jwt.decode(
            token,
            token_service.secret_key,
            algorithms=[token_service.algorithm],
        )

        # 驗證 payload 內容
        assert payload["user_id"] == user_id
        assert payload["iss"] == "aam-agent"
        assert "iat" in payload
        assert "exp" in payload

    def test_issue_token_empty_user_id(self, token_service):
        """測試發行 token 時 user_id 為空"""
        with pytest.raises(ValueError, match="user_id 不能為空"):
            token_service.issue_token("")

    def test_verify_token_success(self, token_service):
        """測試 token 驗證成功"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 驗證 token
        is_valid = token_service.verify_token(token, user_id)
        assert is_valid is True

    def test_verify_token_expired(self, token_service):
        """測試過期 token 驗證"""
        user_id = "user_123"

        # 創建一個已過期的 token
        payload = {
            "user_id": user_id,
            "iss": "aam-agent",
            "iat": int(time.time()) - 100000,  # 很久以前
            "exp": int(time.time()) - 50000,  # 已過期
        }
        expired_token = jwt.encode(
            payload,
            token_service.secret_key,
            algorithm=token_service.algorithm,
        )

        # 驗證過期 token
        is_valid = token_service.verify_token(expired_token, user_id)
        assert is_valid is False

    def test_verify_token_invalid_signature(self, token_service):
        """測試無效簽名的 token 驗證"""
        user_id = "user_123"

        # 使用錯誤的密鑰創建 token
        invalid_token = jwt.encode(
            {"user_id": user_id, "iss": "aam-agent"},
            "wrong-secret-key",
            algorithm="HS256",
        )

        # 驗證無效簽名的 token
        is_valid = token_service.verify_token(invalid_token, user_id)
        assert is_valid is False

    def test_verify_token_user_id_mismatch(self, token_service):
        """測試 user_id 不匹配的 token 驗證"""
        user_id_a = "user_123"
        user_id_b = "user_456"

        # 為 user_id_a 發行 token
        token = token_service.issue_token(user_id_a)

        # 使用 user_id_b 驗證 token（應該失敗）
        is_valid = token_service.verify_token(token, user_id_b)
        assert is_valid is False

    def test_verify_token_empty_token(self, token_service):
        """測試空 token 驗證"""
        with pytest.raises(ValueError, match="token 不能為空"):
            token_service.verify_token("", "user_123")

    def test_verify_token_empty_user_id(self, token_service):
        """測試空 user_id 驗證"""
        token = token_service.issue_token("user_123")
        with pytest.raises(ValueError, match="user_id 不能為空"):
            token_service.verify_token(token, "")

    def test_extract_user_id_success(self, token_service):
        """測試從 token 中提取 user_id"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 提取 user_id
        extracted_user_id = token_service.extract_user_id(token)
        assert extracted_user_id == user_id

    def test_extract_user_id_invalid_token(self, token_service):
        """測試從無效 token 中提取 user_id"""
        invalid_token = "invalid.token.string"

        # 提取 user_id（應該返回 None）
        extracted_user_id = token_service.extract_user_id(invalid_token)
        assert extracted_user_id is None

    def test_extract_user_id_empty_token(self, token_service):
        """測試從空 token 中提取 user_id"""
        extracted_user_id = token_service.extract_user_id("")
        assert extracted_user_id is None

    def test_token_issuer_validation(self, token_service):
        """測試 token 發行者驗證"""
        user_id = "user_123"

        # 創建一個發行者錯誤的 token
        payload = {
            "user_id": user_id,
            "iss": "wrong-issuer",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        wrong_issuer_token = jwt.encode(
            payload,
            token_service.secret_key,
            algorithm=token_service.algorithm,
        )

        # 驗證發行者錯誤的 token（應該失敗）
        is_valid = token_service.verify_token(wrong_issuer_token, user_id)
        assert is_valid is False

    def test_token_expire_hours_config(self, token_service):
        """測試 token 有效期配置"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 解碼 token 獲取過期時間
        payload = jwt.decode(
            token,
            token_service.secret_key,
            algorithms=[token_service.algorithm],
        )

        # 驗證過期時間大約是 24 小時後（允許 1 分鐘誤差）
        expected_exp = int(time.time()) + (token_service.token_expire_hours * 3600)
        actual_exp = payload["exp"]
        assert abs(actual_exp - expected_exp) < 60  # 允許 1 分鐘誤差

