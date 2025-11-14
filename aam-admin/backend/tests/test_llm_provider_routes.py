"""
@purpose: LLM Provider 管理路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from fastapi.testclient import TestClient


class TestLLMProviderRoutes:
    """LLM Provider 管理路由测试类"""

    def test_get_providers_unauthorized(self, client: TestClient):
        """测试未授权访问 Provider 列表"""
        response = client.get("/api/v1/admin/llm-providers")
        assert response.status_code == 401

    def test_get_providers(self, authenticated_client: TestClient):
        """测试获取 Provider 列表"""
        response = authenticated_client.get("/api/v1/admin/llm-providers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_provider_detail(self, authenticated_client: TestClient):
        """测试获取 Provider 详情"""
        # 先获取 Provider 列表
        list_response = authenticated_client.get("/api/v1/admin/llm-providers")
        providers = list_response.json()
        
        if providers:
            provider_type = providers[0]["type"]
            response = authenticated_client.get(f"/api/v1/admin/llm-providers/{provider_type}")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == provider_type
        else:
            # 测试不存在的 Provider
            response = authenticated_client.get("/api/v1/admin/llm-providers/invalid")
            assert response.status_code == 404

    def test_get_provider_models(self, authenticated_client: TestClient):
        """测试获取模型列表"""
        # 先获取 Provider 列表
        list_response = authenticated_client.get("/api/v1/admin/llm-providers")
        providers = list_response.json()
        
        if providers:
            provider_type = providers[0]["type"]
            response = authenticated_client.get(f"/api/v1/admin/llm-providers/{provider_type}/models")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_update_model_config(self, authenticated_client: TestClient):
        """测试更新模型配置"""
        # 先获取 Provider 和模型列表
        list_response = authenticated_client.get("/api/v1/admin/llm-providers")
        providers = list_response.json()
        
        if providers:
            provider_type = providers[0]["type"]
            models_response = authenticated_client.get(
                f"/api/v1/admin/llm-providers/{provider_type}/models"
            )
            models = models_response.json()
            
            if models:
                model_name = models[0]["name"]
                response = authenticated_client.put(
                    f"/api/v1/admin/llm-providers/{provider_type}/models/{model_name}",
                    json={
                        "max_tokens": 2000,
                        "temperature": 0.7,
                    },
                )
                assert response.status_code == 200

    def test_toggle_model(self, authenticated_client: TestClient):
        """测试启用/禁用模型"""
        # 先获取 Provider 和模型列表
        list_response = authenticated_client.get("/api/v1/admin/llm-providers")
        providers = list_response.json()
        
        if providers:
            provider_type = providers[0]["type"]
            models_response = authenticated_client.get(
                f"/api/v1/admin/llm-providers/{provider_type}/models"
            )
            models = models_response.json()
            
            if models:
                model_name = models[0]["name"]
                response = authenticated_client.post(
                    f"/api/v1/admin/llm-providers/{provider_type}/models/{model_name}/toggle",
                    json={"enabled": False},
                )
                assert response.status_code == 200

    def test_test_provider(self, authenticated_client: TestClient):
        """测试 Provider 连接"""
        # 先获取 Provider 列表
        list_response = authenticated_client.get("/api/v1/admin/llm-providers")
        providers = list_response.json()
        
        if providers:
            provider_type = providers[0]["type"]
            response = authenticated_client.post(
                f"/api/v1/admin/llm-providers/{provider_type}/test"
            )
            assert response.status_code == 200

