"""
@purpose: 測試 MCP 控制器的邏輯和 API Key 認證機制
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.api.controllers.mcp_controller import enrich_mcp, verify_api_key
from src.core.interfaces.i_memory_service import IMemoryService
from src.models.api.mcp import (
    EnrichedMCP,
    Metadata,
    PartialMCP,
    RetrievedKnowledge,
    RetrievedDoc,
    SessionContext,
    UserProfile,
    UserProfileEnriched,
)


class TestVerifyAPIKey:
    """測試 API Key 認證機制"""

    @pytest.fixture
    def mock_settings(self):
        """創建模擬的配置"""
        mock_settings = Mock()
        mock_settings.api.api_key = "test-api-key-123"
        return mock_settings

    @pytest.mark.asyncio
    async def test_verify_api_key_success(self, mock_settings):
        """測試 API Key 驗證成功"""
        with patch("src.api.controllers.mcp_controller.get_settings", return_value=mock_settings):
            result = await verify_api_key("test-api-key-123")
            assert result == "test-api-key-123"

    @pytest.mark.asyncio
    async def test_verify_api_key_failure(self, mock_settings):
        """測試 API Key 驗證失敗"""
        with patch("src.api.controllers.mcp_controller.get_settings", return_value=mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key("wrong-api-key")
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid or missing API Key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_api_key_missing(self, mock_settings):
        """測試缺少 API Key"""
        with patch("src.api.controllers.mcp_controller.get_settings", return_value=mock_settings):
            # FastAPI 會在缺少必需參數時自動拋出異常，這裡測試錯誤的 key
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key("")
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestEnrichMCP:
    """測試 enrich_mcp 端點"""

    @pytest.fixture
    def mock_memory_service(self):
        """創建模擬的記憶服務"""
        mock_service = Mock(spec=IMemoryService)
        return mock_service

    @pytest.fixture
    def partial_mcp(self):
        """創建測試用的 PartialMCP"""
        return PartialMCP(
            user_profile=UserProfile(user_id="user123"),
            session_context=SessionContext(
                session_id="session123",
                current_query="What is Python?",
                short_term_memory=[],
            ),
        )

    @pytest.fixture
    def enriched_mcp(self):
        """創建測試用的 EnrichedMCP"""
        return EnrichedMCP(
            metadata=Metadata(),
            user_profile=UserProfileEnriched(
                user_id="user123",
                long_term_style_tags=["formal"],
                current_sentiment="positive",
            ),
            session_context=SessionContext(
                session_id="session123",
                current_query="What is Python?",
                short_term_memory=[],
            ),
            retrieved_knowledge=RetrievedKnowledge(
                docs=[
                    RetrievedDoc(
                        source="chromadb:doc1",
                        content="Python is a programming language",
                        score=0.9,
                    )
                ],
                kg_triples=[],
            ),
        )

    @pytest.mark.asyncio
    async def test_enrich_mcp_success(
        self, mock_memory_service, partial_mcp, enriched_mcp
    ):
        """測試 enrich_mcp 端點成功流程"""
        # 設置 Mock 返回值
        mock_memory_service.enrich = AsyncMock(return_value=enriched_mcp)

        # 執行測試（跳過 API Key 驗證）
        with patch("src.api.controllers.mcp_controller.verify_api_key", return_value="test-key"):
            result = await enrich_mcp(
                mcp=partial_mcp,
                memory_service=mock_memory_service,
                api_key="test-key",
            )

        # 驗證結果
        assert isinstance(result, EnrichedMCP)
        assert result.user_profile.user_id == "user123"
        assert result.session_context.session_id == "session123"
        assert len(result.retrieved_knowledge.docs) == 1

        # 驗證方法被調用
        mock_memory_service.enrich.assert_called_once_with(partial_mcp)

    @pytest.mark.asyncio
    async def test_enrich_mcp_service_error(
        self, mock_memory_service, partial_mcp
    ):
        """測試 enrich_mcp 端點處理服務錯誤"""
        # 設置 Mock 拋出異常
        mock_memory_service.enrich = AsyncMock(
            side_effect=Exception("服務內部錯誤")
        )

        # 執行測試
        with patch("src.api.controllers.mcp_controller.verify_api_key", return_value="test-key"):
            with pytest.raises(HTTPException) as exc_info:
                await enrich_mcp(
                    mcp=partial_mcp,
                    memory_service=mock_memory_service,
                    api_key="test-key",
                )

        # 驗證異常
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "處理 MCP 豐富化請求時發生內部錯誤" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_enrich_mcp_http_exception_propagation(
        self, mock_memory_service, partial_mcp
    ):
        """測試 HTTPException 異常的傳播"""
        # 設置 Mock 拋出 HTTPException
        http_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="業務邏輯錯誤",
        )
        mock_memory_service.enrich = AsyncMock(side_effect=http_exception)

        # 執行測試
        with patch("src.api.controllers.mcp_controller.verify_api_key", return_value="test-key"):
            with pytest.raises(HTTPException) as exc_info:
                await enrich_mcp(
                    mcp=partial_mcp,
                    memory_service=mock_memory_service,
                    api_key="test-key",
                )

        # 驗證異常被正確傳播
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "業務邏輯錯誤"


class TestMCPControllerIntegration:
    """測試 MCP 控制器的整合場景（使用 TestClient）"""

    @pytest.fixture
    def mock_memory_service(self):
        """創建模擬的記憶服務"""
        mock_service = Mock(spec=IMemoryService)
        return mock_service

    @pytest.fixture
    def test_app(self, mock_memory_service):
        """創建測試用的 FastAPI 應用"""
        from fastapi import FastAPI
        from src.api.controllers.mcp_controller import router

        app = FastAPI()
        app.include_router(router, prefix="/v1/mcp", tags=["MCP"])
        
        # 將 mock_service 存儲到 app.state
        app.state.memory_service = mock_memory_service
        
        return app

    @pytest.fixture
    def client(self, test_app):
        """創建測試客戶端"""
        return TestClient(test_app)

    def test_enrich_endpoint_with_valid_api_key(
        self, client, mock_memory_service
    ):
        """測試使用有效 API Key 調用端點"""
        # 設置 Mock 返回值
        enriched_mcp = EnrichedMCP(
            metadata=Metadata(),
            user_profile=UserProfileEnriched(
                user_id="user123",
                long_term_style_tags=[],
                current_sentiment="neutral",
            ),
            session_context=SessionContext(
                session_id="session123",
                current_query="test query",
                short_term_memory=[],
            ),
            retrieved_knowledge=RetrievedKnowledge(),
        )
        mock_memory_service.enrich = AsyncMock(return_value=enriched_mcp)

        # Mock API Key 驗證
        with patch("src.api.controllers.mcp_controller.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = "test-api-key"
            mock_get_settings.return_value = mock_settings

            # 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json={
                    "user_profile": {"user_id": "user123"},
                    "session_context": {
                        "session_id": "session123",
                        "current_query": "test query",
                        "short_term_memory": [],
                    },
                },
                headers={"X-API-KEY": "test-api-key"},
            )

        # 驗證響應
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_profile"]["user_id"] == "user123"
        assert data["session_context"]["session_id"] == "session123"

    def test_enrich_endpoint_with_invalid_api_key(
        self, client, mock_memory_service
    ):
        """測試使用無效 API Key 調用端點"""
        # Mock API Key 驗證
        with patch("src.api.controllers.mcp_controller.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = "correct-api-key"
            mock_get_settings.return_value = mock_settings

            # 發送請求（使用錯誤的 API Key）
            response = client.post(
                "/v1/mcp/enrich",
                json={
                    "user_profile": {"user_id": "user123"},
                    "session_context": {
                        "session_id": "session123",
                        "current_query": "test query",
                        "short_term_memory": [],
                    },
                },
                headers={"X-API-KEY": "wrong-api-key"},
            )

        # 驗證響應
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or missing API Key" in response.json()["detail"]

    def test_enrich_endpoint_without_api_key(
        self, client, mock_memory_service
    ):
        """測試缺少 API Key 的請求"""
        # 發送請求（不包含 API Key header）
        response = client.post(
            "/v1/mcp/enrich",
            json={
                "user_profile": {"user_id": "user123"},
                "session_context": {
                    "session_id": "session123",
                    "current_query": "test query",
                    "short_term_memory": [],
                },
            },
        )

        # 驗證響應（FastAPI 會自動返回 422 當缺少必需參數時）
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

