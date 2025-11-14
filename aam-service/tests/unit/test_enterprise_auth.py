"""
@purpose: 企業級認證單元測試，驗證企業 Secret Key 簽名生成和驗證
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import hashlib
import hmac
from unittest.mock import patch

import pytest

from src.mcp_server.auth_middleware import AuthMiddleware
from src.core.services.token_service import TokenService


@pytest.fixture
def mock_security_settings():
    """創建模擬的安全配置"""
    with patch("src.mcp_server.auth_middleware.get_settings") as mock_get_settings:
        mock_settings = type("Settings", (), {})()
        mock_settings.security = type("SecuritySettings", (), {})()
        mock_settings.security.secret_key = "test-secret-key-12345"
        mock_settings.security.algorithm = "HS256"
        mock_settings.security.token_expire_hours = 24
        mock_settings.security.token_issuer = "aam-agent"
        mock_settings.security.enable_user_id_validation = True
        mock_settings.security.enterprise_secret_key = "test-enterprise-secret-key-12345"
        mock_settings.security.enable_enterprise_auth = True
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def token_service(mock_security_settings):
    """創建 Token 服務實例"""
    return TokenService()


@pytest.fixture
def auth_middleware(token_service):
    """創建安全中間件實例"""
    return AuthMiddleware(token_service)


class TestEnterpriseAuth:
    """企業級認證測試類"""

    def test_generate_enterprise_signature(self, auth_middleware):
        """測試生成企業級簽名"""
        user_id = "user_123"
        token = "test_token_123"

        signature = auth_middleware.generate_enterprise_signature(user_id, token)

        # 驗證簽名格式（應該是 64 字符的十六進制字符串）
        assert signature is not None
        assert len(signature) == 64  # SHA256 十六進制長度
        assert all(c in "0123456789abcdef" for c in signature)

    def test_verify_enterprise_signature_success(self, auth_middleware):
        """測試驗證企業級簽名成功"""
        user_id = "user_123"
        token = "test_token_123"

        # 生成簽名
        signature = auth_middleware.generate_enterprise_signature(user_id, token)

        # 驗證簽名
        is_valid = auth_middleware._verify_enterprise_signature(
            signature, user_id, token
        )
        assert is_valid is True

    def test_verify_enterprise_signature_failure(self, auth_middleware):
        """測試驗證企業級簽名失敗（錯誤簽名）"""
        user_id = "user_123"
        token = "test_token_123"
        wrong_signature = "wrong_signature_12345"

        # 驗證錯誤簽名
        is_valid = auth_middleware._verify_enterprise_signature(
            wrong_signature, user_id, token
        )
        assert is_valid is False

    def test_verify_enterprise_signature_user_id_mismatch(
        self, auth_middleware
    ):
        """測試驗證企業級簽名失敗（user_id 不匹配）"""
        user_id_a = "user_123"
        user_id_b = "user_456"
        token = "test_token_123"

        # 為 user_id_a 生成簽名
        signature = auth_middleware.generate_enterprise_signature(user_id_a, token)

        # 使用 user_id_b 驗證簽名（應該失敗）
        is_valid = auth_middleware._verify_enterprise_signature(
            signature, user_id_b, token
        )
        assert is_valid is False

    def test_verify_enterprise_signature_token_mismatch(
        self, auth_middleware
    ):
        """測試驗證企業級簽名失敗（token 不匹配）"""
        user_id = "user_123"
        token_a = "test_token_123"
        token_b = "test_token_456"

        # 為 token_a 生成簽名
        signature = auth_middleware.generate_enterprise_signature(user_id, token_a)

        # 使用 token_b 驗證簽名（應該失敗）
        is_valid = auth_middleware._verify_enterprise_signature(
            signature, user_id, token_b
        )
        assert is_valid is False

    def test_verify_request_with_enterprise_auth_success(
        self, auth_middleware, token_service
    ):
        """測試帶企業級認證的請求驗證成功"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 生成企業簽名
        enterprise_signature = auth_middleware.generate_enterprise_signature(
            user_id, token
        )

        # 驗證請求
        is_valid, error_message = auth_middleware.verify_request(
            token, user_id, enterprise_signature
        )

        assert is_valid is True
        assert error_message is None

    def test_verify_request_with_enterprise_auth_missing_signature(
        self, auth_middleware, token_service
    ):
        """測試帶企業級認證的請求驗證失敗（缺少簽名）"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 驗證請求（沒有企業簽名）
        is_valid, error_message = auth_middleware.verify_request(
            token, user_id, None
        )

        assert is_valid is False
        assert "企業級認證失敗" in error_message
        assert "缺少企業簽名" in error_message

    def test_verify_request_with_enterprise_auth_invalid_signature(
        self, auth_middleware, token_service
    ):
        """測試帶企業級認證的請求驗證失敗（無效簽名）"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)
        wrong_signature = "wrong_signature_12345"

        # 驗證請求（無效簽名）
        is_valid, error_message = auth_middleware.verify_request(
            token, user_id, wrong_signature
        )

        assert is_valid is False
        assert "企業級認證失敗" in error_message
        assert "簽名驗證失敗" in error_message

    def test_verify_request_enterprise_auth_disabled(
        self, auth_middleware, token_service
    ):
        """測試企業級認證關閉時的請求驗證"""
        # 關閉企業級認證
        auth_middleware.enable_enterprise_auth = False

        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 驗證請求（沒有企業簽名，但企業認證已關閉）
        is_valid, error_message = auth_middleware.verify_request(
            token, user_id, None
        )

        # 應該通過（因為企業認證已關閉）
        assert is_valid is True
        assert error_message is None

    def test_enterprise_signature_algorithm(self, auth_middleware):
        """測試企業級簽名算法（HMAC-SHA256）"""
        user_id = "user_123"
        token = "test_token_123"

        # 生成簽名
        signature = auth_middleware.generate_enterprise_signature(user_id, token)

        # 手動計算簽名進行驗證
        message = user_id + token
        expected_signature = hmac.new(
            auth_middleware.enterprise_secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        assert signature == expected_signature

    def test_enterprise_signature_without_token(self, auth_middleware):
        """測試不帶 token 的企業級簽名生成"""
        user_id = "user_123"

        # 生成簽名（沒有 token）
        signature = auth_middleware.generate_enterprise_signature(user_id, None)

        # 驗證簽名
        is_valid = auth_middleware._verify_enterprise_signature(
            signature, user_id, None
        )
        assert is_valid is True

    def test_enterprise_auth_configuration_error(self, auth_middleware):
        """測試企業級認證配置錯誤（啟用但未設置 Secret Key）"""
        # 設置為啟用但沒有 Secret Key
        auth_middleware.enable_enterprise_auth = True
        auth_middleware.enterprise_secret_key = None

        user_id = "user_123"
        token = "test_token_123"
        signature = "test_signature"

        # 驗證請求（應該返回配置錯誤）
        is_valid, error_message = auth_middleware.verify_request(
            token, user_id, signature
        )

        assert is_valid is False
        assert "企業級認證配置錯誤" in error_message
        assert "ENTERPRISE_SECRET_KEY 未設置" in error_message

