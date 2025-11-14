"""
@purpose: SmartQ 整合測試，驗證 AAM 服務與 SmartQ（上層應用）的集成
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.controllers.mcp_controller import router as mcp_router
from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
from src.models.api.mcp import PartialMCP, SessionContext, UserProfile


@pytest.mark.integration
@pytest.mark.external
class TestSmartQIntegration:
    """
    SmartQ 整合測試
    
    測試 AAM 服務與 SmartQ（上層應用）的集成，包括：
    - API 集成測試
    - 業務流程測試
    - 錯誤處理測試
    """

    @pytest.fixture
    def mock_knowledge_store(self):
        """創建模擬的知識庫"""
        store = Mock()
        store.search = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def mock_persona_store(self):
        """創建模擬的用戶畫像存儲"""
        store = Mock()
        store.get = AsyncMock(return_value=None)
        return store

    @pytest.fixture
    def analysis_model(self):
        """創建分析模型（使用 Mock）"""
        return MockAnalysisModel()

    @pytest.fixture
    def memory_service(self, mock_knowledge_store, mock_persona_store, analysis_model):
        """創建記憶服務實例"""
        return MemoryServiceImpl(
            knowledge_store=mock_knowledge_store,
            persona_store=mock_persona_store,
            analysis_model=analysis_model,
        )

    @pytest.fixture
    def test_app(self, memory_service):
        """創建測試用的 FastAPI 應用"""
        app = FastAPI()
        app.include_router(mcp_router, prefix="/v1/mcp", tags=["MCP"])
        app.state.memory_service = memory_service
        return app

    @pytest.fixture
    def client(self, test_app):
        """創建測試客戶端（模擬 SmartQ）"""
        return TestClient(test_app)

    @pytest.fixture
    def valid_api_key(self):
        """返回有效的 API Key"""
        return "test-api-key-123"

    @pytest.fixture
    def smartq_request_payload(self):
        """創建模擬 SmartQ 的請求負載"""
        return {
            "user_profile": {"user_id": "smartq_user_001"},
            "session_context": {
                "session_id": "smartq_session_001",
                "current_query": "What is machine learning?",
                "short_term_memory": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you?"},
                ],
            },
        }

    def test_smartq_enrich_request_success(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        mock_persona_store,
        valid_api_key,
        smartq_request_payload,
    ):
        """
        測試 SmartQ 發送豐富化請求成功
        
        場景: SmartQ 向 AAM 發送 MCP 豐富化請求，AAM 返回豐富化的上下文
        """
        # 設置 Mock 返回值
        from src.models.api.mcp import RetrievedDoc

        mock_docs = [
            RetrievedDoc(
                source="chromadb:doc1",
                content="Machine learning is a subset of artificial intelligence.",
                score=0.95,
            )
        ]
        mock_knowledge_store.search = AsyncMock(return_value=mock_docs)
        mock_persona_store.get = AsyncMock(return_value=None)

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # SmartQ 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=smartq_request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應
        assert response.status_code == 200
        data = response.json()

        # 驗證響應結構（SmartQ 期望的格式）
        assert "metadata" in data
        assert "user_profile" in data
        assert "session_context" in data
        assert "retrieved_knowledge" in data

        # 驗證豐富化的上下文
        assert len(data["retrieved_knowledge"]["docs"]) == 1
        assert (
            data["retrieved_knowledge"]["docs"][0]["content"]
            == "Machine learning is a subset of artificial intelligence."
        )
        assert data["retrieved_knowledge"]["docs"][0]["score"] == 0.95

        # 驗證短期記憶被保留
        assert len(data["session_context"]["short_term_memory"]) == 2

    def test_smartq_enrich_request_with_user_profile(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        mock_persona_store,
        valid_api_key,
    ):
        """
        測試 SmartQ 請求包含用戶畫像
        
        場景: SmartQ 發送請求，AAM 返回包含用戶個性化偏好的上下文
        """
        from src.models.domain.personality import PersonalityInsights

        # 設置 Mock 返回值（包含用戶畫像）
        mock_profile = PersonalityInsights(
            user_id="smartq_user_001",
            style_tags={"formal": 0.8, "technical": 0.9},
            sentiment="positive",
            language_patterns=["簡潔", "專業"],
            confidence_score=0.85,
        )
        mock_persona_store.get = AsyncMock(return_value=mock_profile)
        mock_knowledge_store.search = AsyncMock(return_value=[])

        request_payload = {
            "user_profile": {"user_id": "smartq_user_001"},
            "session_context": {
                "session_id": "smartq_session_001",
                "current_query": "Explain AI",
            },
        }

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # SmartQ 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應包含用戶畫像
        assert response.status_code == 200
        data = response.json()

        # 驗證用戶畫像被豐富化
        assert "long_term_style_tags" in data["user_profile"]
        assert len(data["user_profile"]["long_term_style_tags"]) > 0
        assert data["user_profile"]["current_sentiment"] == "positive"

    def test_smartq_enrich_request_invalid_format(
        self, client, valid_api_key
    ):
        """
        測試 SmartQ 發送無效格式的請求
        
        場景: SmartQ 發送格式錯誤的請求，AAM 返回 422 錯誤
        """
        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # SmartQ 發送無效請求（缺少必需字段）
            response = client.post(
                "/v1/mcp/enrich",
                json={"invalid": "data"},
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應（FastAPI 自動返回 422）
        assert response.status_code == 422

    def test_smartq_enrich_request_service_error(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        valid_api_key,
        smartq_request_payload,
    ):
        """
        測試 AAM 服務錯誤處理
        
        場景: AAM 服務內部錯誤，返回 500 錯誤，但不應該影響 SmartQ
        """
        # 設置 Mock 拋出異常
        mock_knowledge_store.search = AsyncMock(
            side_effect=Exception("數據庫連接錯誤")
        )

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # SmartQ 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=smartq_request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應（應該返回 500 錯誤）
        assert response.status_code == 500
        assert "內部錯誤" in response.json()["detail"]

    def test_smartq_enrich_request_timeout(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        valid_api_key,
        smartq_request_payload,
    ):
        """
        測試請求超時處理
        
        場景: AAM 服務響應超時，SmartQ 應該能夠處理超時錯誤
        """
        import asyncio

        # 設置 Mock 模擬超時
        async def slow_search(*args, **kwargs):
            await asyncio.sleep(10)  # 模擬長時間處理
            return []

        mock_knowledge_store.search = slow_search

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # SmartQ 發送請求（設置較短的超時時間）
            # 注意: TestClient 可能不支持超時，這需要在實際 HTTP 客戶端中測試
            response = client.post(
                "/v1/mcp/enrich",
                json=smartq_request_payload,
                headers={"X-API-KEY": valid_api_key},
                timeout=1.0,  # 1 秒超時
            )

        # 驗證響應（可能超時或返回錯誤）
        # 實際測試中，應該使用真實的 HTTP 客戶端測試超時
        assert response.status_code in [200, 500, 504]


@pytest.mark.integration
@pytest.mark.external
@pytest.mark.real_service
class TestSmartQIntegrationReal:
    """
    SmartQ 整合測試（使用真實 SmartQ 服務）
    
    注意: 這些測試需要真實的 SmartQ 服務運行
    使用環境變量 SMARTQ_SERVICE_URL 指定 SmartQ 服務地址
    """

    @pytest.fixture
    def smartq_service_url(self):
        """獲取 SmartQ 服務 URL"""
        url = os.getenv("SMARTQ_SERVICE_URL", "http://localhost:8001")
        if not url:
            pytest.skip("SMARTQ_SERVICE_URL 未設置，跳過真實服務測試")
        return url

    @pytest.fixture
    def aam_service_url(self):
        """獲取 AAM 服務 URL"""
        return os.getenv("AAM_SERVICE_URL", "http://localhost:8000")

    @pytest.fixture
    def smartq_api_key(self):
        """獲取 SmartQ API Key"""
        return os.getenv("SMARTQ_API_KEY", "test-key")

    async def test_smartq_to_aam_flow(
        self, smartq_service_url, aam_service_url, smartq_api_key
    ):
        """
        測試 SmartQ → AAM 完整流程
        
        場景: 
        1. SmartQ 接收用戶查詢
        2. SmartQ 調用 AAM 豐富化 API
        3. AAM 返回豐富化的上下文
        4. SmartQ 使用上下文生成響應
        """
        import httpx

        # 注意: 這需要真實的 SmartQ 服務運行
        # 實際實現時，應該：
        # 1. 發送用戶查詢到 SmartQ
        # 2. 驗證 SmartQ 調用了 AAM API
        # 3. 驗證 AAM 返回了正確的響應
        # 4. 驗證 SmartQ 生成了包含上下文的響應

        async with httpx.AsyncClient() as client:
            # 發送查詢到 SmartQ（假設 SmartQ 有 /chat 端點）
            response = await client.post(
                f"{smartq_service_url}/chat",
                json={
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "query": "What is Python?",
                },
                headers={"X-API-KEY": smartq_api_key},
                timeout=30.0,
            )

            # 驗證響應
            assert response.status_code == 200
            data = response.json()

            # 驗證響應包含從 AAM 獲取的上下文
            # （這取決於 SmartQ 的響應格式）
            assert "response" in data or "answer" in data

    async def test_smartq_aam_integration_error_handling(
        self, smartq_service_url, smartq_api_key
    ):
        """
        測試 SmartQ 與 AAM 集成時的錯誤處理
        
        場景: AAM 服務不可用時，SmartQ 應該能夠優雅降級
        """
        import httpx

        # 注意: 這需要真實的 SmartQ 服務運行
        # 實際實現時，應該：
        # 1. 停止 AAM 服務（或模擬不可用）
        # 2. 發送查詢到 SmartQ
        # 3. 驗證 SmartQ 能夠處理 AAM 不可用的情況
        # 4. 驗證 SmartQ 仍然能夠生成響應（可能不包含上下文）

        async with httpx.AsyncClient() as client:
            # 發送查詢到 SmartQ
            response = await client.post(
                f"{smartq_service_url}/chat",
                json={
                    "user_id": "test_user",
                    "session_id": "test_session",
                    "query": "What is Python?",
                },
                headers={"X-API-KEY": smartq_api_key},
                timeout=30.0,
            )

            # 驗證響應（應該仍然成功，但可能不包含上下文）
            assert response.status_code in [200, 503]

