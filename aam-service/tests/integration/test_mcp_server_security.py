"""
@purpose: MCP Server 安全集成測試，驗證 token 驗證中間件和越權訪問防護
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.core.services.token_service import TokenService
from src.core.services.memory_service import MemoryServiceImpl
from src.mcp_server.auth_middleware import AuthMiddleware
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel


@pytest.fixture
def mock_security_settings():
    """創建模擬的安全配置"""
    with patch("src.core.services.token_service.get_settings"), \
         patch("src.mcp_server.auth_middleware.get_settings") as mock_get_settings:
        mock_settings = type("Settings", (), {})()
        mock_settings.security = type("SecuritySettings", (), {})()
        mock_settings.security.secret_key = "test-secret-key-12345"
        mock_settings.security.algorithm = "HS256"
        mock_settings.security.token_expire_hours = 24
        mock_settings.security.token_issuer = "aam-agent"
        mock_settings.security.enable_user_id_validation = True
        mock_settings.security.enterprise_secret_key = "test-enterprise-secret-key-12345"
        mock_settings.security.enable_enterprise_auth = False  # 默認關閉，測試時可啟用
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


@pytest.fixture
def mock_memory_service():
    """創建模擬的記憶服務"""
    mock_knowledge_store = Mock()
    mock_persona_store = Mock()
    analysis_model = MockAnalysisModel()
    return MemoryServiceImpl(
        knowledge_store=mock_knowledge_store,
        persona_store=mock_persona_store,
        analysis_model=analysis_model,
    )


class TestAuthMiddleware:
    """安全中間件測試類"""

    def test_verify_request_success(self, auth_middleware, token_service):
        """測試請求驗證成功"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 驗證請求
        is_valid, error_message = auth_middleware.verify_request(token, user_id)

        assert is_valid is True
        assert error_message is None

    def test_verify_request_missing_token(self, auth_middleware):
        """測試缺少 token 的請求驗證"""
        user_id = "user_123"

        # 驗證請求（沒有 token）
        is_valid, error_message = auth_middleware.verify_request(None, user_id)

        assert is_valid is False
        assert "Token 缺失" in error_message

    def test_verify_request_invalid_token(self, auth_middleware):
        """測試無效 token 的請求驗證"""
        user_id = "user_123"
        invalid_token = "invalid.token.string"

        # 驗證請求（無效 token）
        is_valid, error_message = auth_middleware.verify_request(
            invalid_token, user_id
        )

        assert is_valid is False
        assert "Token 驗證失敗" in error_message

    def test_verify_request_user_id_mismatch(self, auth_middleware, token_service):
        """測試 user_id 不匹配的請求驗證（越權訪問防護）"""
        user_id_a = "user_123"
        user_id_b = "user_456"

        # 為 user_id_a 發行 token
        token = token_service.issue_token(user_id_a)

        # 使用 user_id_b 驗證請求（應該失敗）
        is_valid, error_message = auth_middleware.verify_request(token, user_id_b)

        assert is_valid is False
        assert "Token 驗證失敗" in error_message

    def test_extract_user_id_from_token(self, auth_middleware, token_service):
        """測試從 token 中提取 user_id"""
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 提取 user_id
        extracted_user_id = auth_middleware.extract_user_id_from_token(token)
        assert extracted_user_id == user_id

    def test_extract_user_id_from_invalid_token(self, auth_middleware):
        """測試從無效 token 中提取 user_id"""
        invalid_token = "invalid.token.string"

        # 提取 user_id（應該返回 None）
        extracted_user_id = auth_middleware.extract_user_id_from_token(invalid_token)
        assert extracted_user_id is None

    def test_extract_user_id_from_empty_token(self, auth_middleware):
        """測試從空 token 中提取 user_id"""
        extracted_user_id = auth_middleware.extract_user_id_from_token(None)
        assert extracted_user_id is None


class TestMCPServerSecurity:
    """MCP Server 安全測試類"""

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_with_valid_token(
        self, token_service, mock_memory_service
    ):
        """測試使用有效 token 調用 enrich_context"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 發行 token
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 調用 enrich_context 工具
        arguments = {
            "user_id": user_id,
            "session_id": "session_123",
            "current_query": "What is Python?",
            "token": token,
        }

        result = await mcp_server._handle_tool_call("enrich_context", arguments)

        # 驗證結果（MCP 格式返回 list）
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].get("type") == "text"

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_without_token(
        self, token_service, mock_memory_service
    ):
        """測試不使用 token 調用 enrich_context（應該失敗）"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 調用 enrich_context 工具（沒有 token）
        arguments = {
            "user_id": "user_123",
            "session_id": "session_123",
            "current_query": "What is Python?",
            "token": None,
        }

        result = await mcp_server._handle_tool_call("enrich_context", arguments)

        # 驗證結果（應該失敗，返回錯誤文本）
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Token 缺失" in result[0].get("text", "")

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_with_invalid_token(
        self, token_service, mock_memory_service
    ):
        """測試使用無效 token 調用 enrich_context（應該失敗）"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 調用 enrich_context 工具（無效 token）
        arguments = {
            "user_id": "user_123",
            "session_id": "session_123",
            "current_query": "What is Python?",
            "token": "invalid.token.string",
        }

        result = await mcp_server._handle_tool_call("enrich_context", arguments)

        # 驗證結果（應該失敗，返回錯誤文本）
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Token 驗證失敗" in result[0].get("text", "")

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_unauthorized_access(
        self, token_service, mock_memory_service
    ):
        """測試越權訪問防護（用戶 A 的 token 訪問用戶 B 的數據）"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 為 user_id_a 發行 token
        user_id_a = "user_123"
        user_id_b = "user_456"
        token = token_service.issue_token(user_id_a)

        # 使用 user_id_b 調用 enrich_context（應該失敗）
        arguments = {
            "user_id": user_id_b,  # 不同的 user_id
            "session_id": "session_123",
            "current_query": "What is Python?",
            "token": token,  # user_id_a 的 token
        }

        result = await mcp_server._handle_tool_call("enrich_context", arguments)

        # 驗證結果（應該失敗，返回錯誤文本）
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Token 驗證失敗" in result[0].get("text", "")

    @pytest.mark.asyncio
    async def test_mcp_server_archive_dialogue_with_valid_token(
        self, token_service, mock_memory_service
    ):
        """測試使用有效 token 調用 archive_dialogue"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 發行 token
        user_id = "user_123"
        token = token_service.issue_token(user_id)

        # 調用 archive_dialogue 工具
        arguments = {
            "user_id": user_id,
            "dialog_id": "dialog_123",
            "user_query": "What is Python?",
            "ai_response": "Python is a programming language.",
            "turn": 1,
            "token": token,
        }

        result = await mcp_server._handle_tool_call("archive_dialogue", arguments)

        # 驗證結果（MCP 格式返回 list）
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].get("type") == "text"

    @pytest.mark.asyncio
    async def test_mcp_server_issue_token(self, token_service, mock_memory_service):
        """測試 issue_token 工具"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 調用 issue_token 工具
        arguments = {
            "user_id": "user_123",
        }

        result = await mcp_server._handle_tool_call("issue_token", arguments)

        # 驗證結果（MCP 格式返回 list）
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].get("type") == "text"
        assert "Token issued" in result[0].get("text", "")

    @pytest.mark.asyncio
    async def test_mcp_server_unknown_tool(self, token_service, mock_memory_service):
        """測試未知工具調用"""
        from src.mcp_server.server import MCPServer

        mcp_server = MCPServer(mock_memory_service, token_service)

        # 調用未知工具
        result = await mcp_server._handle_tool_call("unknown_tool", {})

        # 驗證結果（應該失敗，返回錯誤文本）
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Unknown tool" in result[0].get("text", "")

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_with_enterprise_auth(
        self, token_service, mock_memory_service
    ):
        """測試使用企業級認證調用 enrich_context"""
        from src.mcp_server.server import MCPServer
        from src.config.settings import get_settings

        # 啟用企業級認證
        with patch("src.mcp_server.auth_middleware.get_settings") as mock_get_settings:
            mock_settings = type("Settings", (), {})()
            mock_settings.security = type("SecuritySettings", (), {})()
            mock_settings.security.secret_key = "test-secret-key-12345"
            mock_settings.security.algorithm = "HS256"
            mock_settings.security.token_expire_hours = 24
            mock_settings.security.token_issuer = "aam-agent"
            mock_settings.security.enable_user_id_validation = True
            mock_settings.security.enterprise_secret_key = "test-enterprise-secret-key-12345"
            mock_settings.security.enable_enterprise_auth = True  # 啟用企業認證
            mock_get_settings.return_value = mock_settings

            mcp_server = MCPServer(mock_memory_service, token_service)

            # 發行 token
            user_id = "user_123"
            token = token_service.issue_token(user_id)

            # 生成企業簽名
            enterprise_signature = mcp_server.auth_middleware.generate_enterprise_signature(
                user_id, token
            )

            # 調用 enrich_context 工具（帶企業簽名）
            arguments = {
                "user_id": user_id,
                "session_id": "session_123",
                "current_query": "What is Python?",
                "token": token,
                "enterprise_signature": enterprise_signature,
            }

            result = await mcp_server._handle_tool_call("enrich_context", arguments)

            # 驗證結果（應該成功）
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].get("type") == "text"

    @pytest.mark.asyncio
    async def test_mcp_server_enrich_context_enterprise_auth_failure(
        self, token_service, mock_memory_service
    ):
        """測試企業級認證失敗的情況"""
        from src.mcp_server.server import MCPServer

        # 啟用企業級認證
        with patch("src.mcp_server.auth_middleware.get_settings") as mock_get_settings:
            mock_settings = type("Settings", (), {})()
            mock_settings.security = type("SecuritySettings", (), {})()
            mock_settings.security.secret_key = "test-secret-key-12345"
            mock_settings.security.algorithm = "HS256"
            mock_settings.security.token_expire_hours = 24
            mock_settings.security.token_issuer = "aam-agent"
            mock_settings.security.enable_user_id_validation = True
            mock_settings.security.enterprise_secret_key = "test-enterprise-secret-key-12345"
            mock_settings.security.enable_enterprise_auth = True  # 啟用企業認證
            mock_get_settings.return_value = mock_settings

            mcp_server = MCPServer(mock_memory_service, token_service)

            # 發行 token
            user_id = "user_123"
            token = token_service.issue_token(user_id)

            # 使用錯誤的企業簽名
            wrong_signature = "wrong_signature_12345"

            # 調用 enrich_context 工具（錯誤的企業簽名）
            arguments = {
                "user_id": user_id,
                "session_id": "session_123",
                "current_query": "What is Python?",
                "token": token,
                "enterprise_signature": wrong_signature,
            }

            result = await mcp_server._handle_tool_call("enrich_context", arguments)

            # 驗證結果（應該失敗）
            assert isinstance(result, list)
            assert len(result) > 0
            assert "企業級認證失敗" in result[0].get("text", "")

