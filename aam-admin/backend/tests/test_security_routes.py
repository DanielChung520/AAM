"""
@purpose: 安全管理路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from fastapi.testclient import TestClient


class TestSecurityRoutes:
    """安全管理路由测试类"""

    def test_list_tokens_unauthorized(self, client: TestClient):
        """测试未授权访问 Token 列表"""
        response = client.get("/api/v1/admin/security/tokens")
        assert response.status_code == 401

    def test_list_tokens(self, authenticated_client: TestClient):
        """测试获取 Token 列表"""
        response = authenticated_client.get("/api/v1/admin/security/tokens")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_issue_token(self, authenticated_client: TestClient, test_user):
        """测试发行 Token"""
        response = authenticated_client.post(
            "/api/v1/admin/security/tokens/issue",
            json={
                "user_id": test_user.id,
                "name": "Test Token",
                "expires_hours": 24,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert "token_record" in data
        assert data["token_record"]["name"] == "Test Token"

    def test_issue_token_generic(self, authenticated_client: TestClient):
        """测试发行通用 Token（无用户绑定）"""
        response = authenticated_client.post(
            "/api/v1/admin/security/tokens/issue",
            json={
                "name": "Generic Token",
                "expires_hours": 48,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert data["token_record"]["user_id"] is None

    def test_issue_token_invalid_user(self, authenticated_client: TestClient):
        """测试发行 Token 时用户不存在"""
        response = authenticated_client.post(
            "/api/v1/admin/security/tokens/issue",
            json={
                "user_id": 99999,
                "name": "Invalid User Token",
            },
        )
        assert response.status_code == 400

    def test_revoke_token(self, authenticated_client: TestClient, test_user):
        """测试撤销 Token"""
        # 先发行一个 Token
        issue_response = authenticated_client.post(
            "/api/v1/admin/security/tokens/issue",
            json={
                "user_id": test_user.id,
                "name": "Token to Revoke",
            },
        )
        token_id = issue_response.json()["token_record"]["id"]
        
        # 撤销 Token
        response = authenticated_client.post(
            f"/api/v1/admin/security/tokens/{token_id}/revoke",
            json={"reason": "Test revocation"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "revoked"

    def test_revoke_token_not_found(self, authenticated_client: TestClient):
        """测试撤销不存在的 Token"""
        response = authenticated_client.post(
            "/api/v1/admin/security/tokens/99999/revoke",
            json={"reason": "Test"},
        )
        assert response.status_code == 400

    def test_get_token_detail(self, authenticated_client: TestClient, test_user):
        """测试获取 Token 详情"""
        # 先发行一个 Token
        issue_response = authenticated_client.post(
            "/api/v1/admin/security/tokens/issue",
            json={
                "user_id": test_user.id,
                "name": "Test Token",
            },
        )
        token_id = issue_response.json()["token_record"]["id"]
        
        # 获取 Token 详情
        response = authenticated_client.get(f"/api/v1/admin/security/tokens/{token_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == token_id
        assert data["name"] == "Test Token"

    def test_get_enterprise_auth_config(self, authenticated_client: TestClient):
        """测试获取企业认证配置"""
        response = authenticated_client.get("/api/v1/admin/security/enterprise-auth")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "secret_key_set" in data

    def test_update_enterprise_auth_config(self, authenticated_client: TestClient):
        """测试更新企业认证配置"""
        response = authenticated_client.put(
            "/api/v1/admin/security/enterprise-auth",
            json={
                "enabled": True,
                "secret_key": "test_secret_key_12345678",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["secret_key_set"] is True

    def test_test_enterprise_auth(self, authenticated_client: TestClient):
        """测试企业认证签名生成"""
        response = authenticated_client.post(
            "/api/v1/admin/security/enterprise-auth/test",
            json={
                "user_id": "test_user_123",
                "token": "test_token",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "signature" in data

    def test_list_audit_logs(self, authenticated_client: TestClient):
        """测试获取审计日志列表"""
        response = authenticated_client.get("/api/v1/admin/security/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)

    def test_list_audit_logs_with_filters(self, authenticated_client: TestClient):
        """测试使用过滤条件获取审计日志"""
        response = authenticated_client.get(
            "/api/v1/admin/security/audit-logs",
            params={
                "page": 1,
                "page_size": 10,
                "status": "success",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_get_audit_log_detail(self, authenticated_client: TestClient):
        """测试获取审计日志详情"""
        # 先获取日志列表
        list_response = authenticated_client.get("/api/v1/admin/security/audit-logs")
        logs = list_response.json()["items"]
        
        if logs:
            log_id = logs[0]["id"]
            response = authenticated_client.get(f"/api/v1/admin/security/audit-logs/{log_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == log_id
        else:
            # 如果没有日志，测试不存在的日志
            response = authenticated_client.get("/api/v1/admin/security/audit-logs/99999")
            assert response.status_code == 404

