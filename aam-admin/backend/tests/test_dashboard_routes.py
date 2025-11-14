"""
@purpose: 仪表盘路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from fastapi.testclient import TestClient


class TestDashboardRoutes:
    """仪表盘路由测试类"""

    def test_get_dashboard_stats_unauthorized(self, client: TestClient):
        """测试未授权访问仪表盘统计"""
        response = client.get("/api/v1/admin/dashboard/stats")
        assert response.status_code == 401

    def test_get_dashboard_stats(self, authenticated_client: TestClient):
        """测试获取仪表盘统计"""
        response = authenticated_client.get("/api/v1/admin/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_services" in data
        assert "running_services" in data
        assert "llm_providers" in data
        assert "current_version" in data

    def test_get_dashboard_services(self, authenticated_client: TestClient):
        """测试获取服务状态列表"""
        response = authenticated_client.get("/api/v1/admin/dashboard/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_dashboard_metrics(self, authenticated_client: TestClient):
        """测试获取系统资源指标"""
        response = authenticated_client.get("/api/v1/admin/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data

    def test_get_recent_operations(self, authenticated_client: TestClient):
        """测试获取最近操作记录"""
        response = authenticated_client.get("/api/v1/admin/dashboard/recent-operations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

