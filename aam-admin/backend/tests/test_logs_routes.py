"""
@purpose: 日志管理路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from fastapi.testclient import TestClient


class TestLogsRoutes:
    """日志管理路由测试类"""

    def test_search_logs_unauthorized(self, client: TestClient):
        """测试未授权访问日志搜索"""
        response = client.post("/api/v1/admin/logs/search")
        assert response.status_code == 401

    def test_search_logs(self, authenticated_client: TestClient):
        """测试搜索日志"""
        response = authenticated_client.post(
            "/api/v1/admin/logs/search",
            json={
                "container_name": "aam-service",
                "level": "INFO",
                "limit": 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert isinstance(data["logs"], list)

    def test_search_logs_get(self, authenticated_client: TestClient):
        """测试使用 GET 方法搜索日志"""
        response = authenticated_client.get(
            "/api/v1/admin/logs/search",
            params={
                "container_name": "aam-service",
                "level": "INFO",
                "limit": 100,
            },
        )
        assert response.status_code == 200

    def test_export_logs(self, authenticated_client: TestClient):
        """测试导出日志"""
        response = authenticated_client.post(
            "/api/v1/admin/logs/export",
            json={
                "container_name": "aam-service",
                "format": "json",
                "start_time": "2025-01-14T00:00:00Z",
                "end_time": "2025-01-14T23:59:59Z",
            },
        )
        assert response.status_code == 200
        # 导出应该返回文件流
        assert response.headers.get("content-type") in [
            "application/json",
            "text/csv",
            "application/octet-stream",
        ]

