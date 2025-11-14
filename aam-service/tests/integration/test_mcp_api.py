"""
@purpose: 測試 MCP API 端點的整合測試，驗證完整的 API 請求/響應流程
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.controllers.mcp_controller import router as mcp_router
from src.core.interfaces.i_memory_service import IMemoryService
from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
from src.models.api.mcp import (
    EnrichedMCP,
    Metadata,
    PartialMCP,
    RetrievedDoc,
    RetrievedKnowledge,
    SessionContext,
    UserProfile,
    UserProfileEnriched,
)


@pytest.mark.integration
class TestMCPAPIIntegration:
    """測試 MCP API 端點的整合場景"""

    @pytest.fixture
    def mock_knowledge_store(self):
        """創建模擬的知識庫"""
        return Mock()

    @pytest.fixture
    def mock_persona_store(self):
        """創建模擬的用戶畫像存儲"""
        return Mock()

    @pytest.fixture
    def memory_service(self, mock_knowledge_store, mock_persona_store):
        """創建記憶服務實例"""
        analysis_model = MockAnalysisModel()
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
        
        # 將 memory_service 存儲到 app.state
        app.state.memory_service = memory_service
        
        return app

    @pytest.fixture
    def client(self, test_app):
        """創建測試客戶端"""
        return TestClient(test_app)

    @pytest.fixture
    def valid_api_key(self):
        """返回有效的 API Key"""
        return "test-api-key-123"

    @pytest.fixture
    def request_payload(self):
        """創建測試用的請求負載"""
        return {
            "user_profile": {"user_id": "user123"},
            "session_context": {
                "session_id": "session123",
                "current_query": "What is Python?",
                "short_term_memory": [],
            },
        }

    def test_enrich_endpoint_success(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        mock_persona_store,
        valid_api_key,
        request_payload,
    ):
        """測試 enrich 端點成功流程"""
        # 設置 Mock 返回值
        mock_docs = [
            RetrievedDoc(
                source="chromadb:doc1",
                content="Python is a programming language",
                score=0.9,
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

            # 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        
        # 驗證響應結構
        assert "metadata" in data
        assert "user_profile" in data
        assert "session_context" in data
        assert "retrieved_knowledge" in data
        
        # 驗證響應內容
        assert data["user_profile"]["user_id"] == "user123"
        assert data["session_context"]["session_id"] == "session123"
        assert data["session_context"]["current_query"] == "What is Python?"
        assert len(data["retrieved_knowledge"]["docs"]) == 1
        assert data["retrieved_knowledge"]["docs"][0]["source"] == "chromadb:doc1"
        assert data["retrieved_knowledge"]["docs"][0]["score"] == 0.9

        # 驗證服務方法被調用
        mock_knowledge_store.search.assert_called_once()
        mock_persona_store.get.assert_called_once()

    def test_enrich_endpoint_invalid_api_key(
        self, client, valid_api_key, request_payload
    ):
        """測試使用無效 API Key 的請求"""
        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # 發送請求（使用錯誤的 API Key）
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": "wrong-api-key"},
            )

        # 驗證響應
        assert response.status_code == 401
        assert "Invalid or missing API Key" in response.json()["detail"]

    def test_enrich_endpoint_missing_api_key(self, client, request_payload):
        """測試缺少 API Key 的請求"""
        # 發送請求（不包含 API Key header）
        response = client.post(
            "/v1/mcp/enrich",
            json=request_payload,
        )

        # 驗證響應（FastAPI 會自動返回 422 當缺少必需參數時）
        assert response.status_code == 422

    def test_enrich_endpoint_invalid_request_body(self, client, valid_api_key):
        """測試無效請求體的處理"""
        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # 發送無效請求（缺少必需字段）
            response = client.post(
                "/v1/mcp/enrich",
                json={"invalid": "data"},
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應（FastAPI 會自動返回 422 當請求體驗證失敗時）
        assert response.status_code == 422

    def test_enrich_endpoint_service_error(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        valid_api_key,
        request_payload,
    ):
        """測試服務錯誤的處理"""
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

            # 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應（應該返回 500 錯誤）
        assert response.status_code == 500
        assert "處理 MCP 豐富化請求時發生內部錯誤" in response.json()["detail"]

    def test_enrich_endpoint_with_short_term_memory(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        mock_persona_store,
        valid_api_key,
    ):
        """測試包含短期記憶的請求"""
        # 設置 Mock 返回值
        mock_knowledge_store.search = AsyncMock(return_value=[])
        mock_persona_store.get = AsyncMock(return_value=None)

        # 創建包含短期記憶的請求
        request_payload = {
            "user_profile": {"user_id": "user123"},
            "session_context": {
                "session_id": "session123",
                "current_query": "Tell me more",
                "short_term_memory": [
                    {"role": "user", "content": "What is Python?"},
                    {"role": "assistant", "content": "Python is a programming language."},
                ],
            },
        }

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert len(data["session_context"]["short_term_memory"]) == 2
        assert data["session_context"]["short_term_memory"][0]["role"] == "user"
        assert data["session_context"]["short_term_memory"][1]["role"] == "assistant"

    def test_enrich_endpoint_response_structure(
        self,
        client,
        memory_service,
        mock_knowledge_store,
        mock_persona_store,
        valid_api_key,
        request_payload,
    ):
        """測試響應結構的完整性"""
        # 設置 Mock 返回值
        mock_knowledge_store.search = AsyncMock(return_value=[])
        mock_persona_store.get = AsyncMock(return_value=None)

        # Mock API Key 驗證
        with patch(
            "src.api.controllers.mcp_controller.get_settings"
        ) as mock_get_settings:
            mock_settings = Mock()
            mock_settings.api.api_key = valid_api_key
            mock_get_settings.return_value = mock_settings

            # 發送請求
            response = client.post(
                "/v1/mcp/enrich",
                json=request_payload,
                headers={"X-API-KEY": valid_api_key},
            )

        # 驗證響應結構
        assert response.status_code == 200
        data = response.json()
        
        # 驗證 metadata 結構
        assert "request_id" in data["metadata"]
        assert "aam_version" in data["metadata"]
        assert data["metadata"]["aam_version"] == "1.0"
        
        # 驗證 user_profile 結構
        assert "user_id" in data["user_profile"]
        assert "long_term_style_tags" in data["user_profile"]
        assert "current_sentiment" in data["user_profile"]
        assert isinstance(data["user_profile"]["long_term_style_tags"], list)
        
        # 驗證 retrieved_knowledge 結構
        assert "docs" in data["retrieved_knowledge"]
        assert "kg_triples" in data["retrieved_knowledge"]
        assert isinstance(data["retrieved_knowledge"]["docs"], list)
        assert isinstance(data["retrieved_knowledge"]["kg_triples"], list)

