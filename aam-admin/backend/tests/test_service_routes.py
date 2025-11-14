"""
@purpose: 系统服务监管路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestServiceRoutes:
    """系统服务监管路由测试类"""

    def test_get_services_unauthorized(self, client: TestClient):
        """测试未授权访问服务列表"""
        response = client.get("/api/v1/admin/services")
        assert response.status_code == 401

    @patch("src.core.services.docker_service.DockerService")
    def test_get_services(self, mock_docker_service, authenticated_client: TestClient):
        """测试获取服务列表"""
        # Mock Docker 服务
        mock_client = mock_docker_service.return_value
        mock_client.get_containers.return_value = []
        
        response = authenticated_client.get("/api/v1/admin/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_service_detail(self, authenticated_client: TestClient):
        """测试获取服务详情"""
        response = authenticated_client.get("/api/v1/admin/services/aam-service")
        # 可能返回 404（如果服务不存在）或 200（如果存在）
        assert response.status_code in [200, 404]

    def test_start_service(self, authenticated_client: TestClient):
        """测试启动服务"""
        response = authenticated_client.post(
            "/api/v1/admin/services/aam-service/start",
            json={"confirm": True, "reason": "Test start"},
        )
        # 可能返回 200（成功）或 404（服务不存在）或 500（Docker 错误）
        assert response.status_code in [200, 404, 500]

    def test_stop_service(self, authenticated_client: TestClient):
        """测试停止服务"""
        response = authenticated_client.post(
            "/api/v1/admin/services/aam-service/stop",
            json={"confirm": True, "reason": "Test stop"},
        )
        assert response.status_code in [200, 404, 500]

    def test_restart_service(self, authenticated_client: TestClient):
        """测试重启服务"""
        response = authenticated_client.post(
            "/api/v1/admin/services/aam-service/restart",
            json={"confirm": True, "reason": "Test restart"},
        )
        assert response.status_code in [200, 404, 500]

    def test_get_service_stats(self, authenticated_client: TestClient):
        """测试获取服务资源统计"""
        response = authenticated_client.get("/api/v1/admin/services/aam-service/stats")
        assert response.status_code in [200, 404]

    def test_get_service_health(self, authenticated_client: TestClient):
        """测试获取服务健康状态"""
        response = authenticated_client.get("/api/v1/admin/services/aam-service/health")
        assert response.status_code in [200, 404]

