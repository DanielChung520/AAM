"""
@purpose: 版本管理路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

from src.models.version import Version, VersionStatus, VersionConfig
from src.models.schemas.version import Version as VersionSchema


class TestVersionRoutes:
    """版本管理路由测试类"""

    def test_list_versions_unauthorized(self, client: TestClient):
        """测试未授权访问版本列表"""
        response = client.get("/api/v1/admin/versions")
        assert response.status_code == 401

    def test_list_versions_empty(self, authenticated_client: TestClient, db_session):
        """测试获取空版本列表"""
        response = authenticated_client.get("/api/v1/admin/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_versions_with_data(self, authenticated_client: TestClient, db_session, test_user):
        """测试获取版本列表（有数据）"""
        # 创建测试版本
        version1 = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            git_commit="abc123",
            image_tag="aam-service:v1.0.0",
            created_by=test_user.id,
        )
        version2 = Version(
            version="v1.1.0",
            status=VersionStatus.AVAILABLE,
            git_commit="def456",
            image_tag="aam-service:v1.1.0",
            created_by=test_user.id,
        )
        db_session.add_all([version1, version2])
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["version"] in ["v1.0.0", "v1.1.0"]

    def test_list_versions_with_pagination(self, authenticated_client: TestClient, db_session, test_user):
        """测试版本列表分页"""
        # 创建多个测试版本
        versions = []
        for i in range(25):
            version = Version(
                version=f"v1.{i}.0",
                status=VersionStatus.AVAILABLE,
                created_by=test_user.id,
            )
            versions.append(version)
        db_session.add_all(versions)
        db_session.commit()

        # 测试第一页
        response = authenticated_client.get("/api/v1/admin/versions?page=1&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 20
        assert data["page"] == 1
        assert data["total_pages"] == 2

        # 测试第二页
        response = authenticated_client.get("/api/v1/admin/versions?page=2&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_list_versions_with_status_filter(self, authenticated_client: TestClient, db_session, test_user):
        """测试版本列表状态过滤"""
        # 创建不同状态的版本
        version1 = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            created_by=test_user.id,
        )
        version2 = Version(
            version="v1.1.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add_all([version1, version2])
        db_session.commit()

        # 过滤 ACTIVE 状态
        response = authenticated_client.get("/api/v1/admin/versions?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "active"

    def test_list_versions_with_search(self, authenticated_client: TestClient, db_session, test_user):
        """测试版本列表搜索"""
        version1 = Version(
            version="v1.0.0",
            description="First release",
            created_by=test_user.id,
        )
        version2 = Version(
            version="v2.0.0",
            description="Second release",
            created_by=test_user.id,
        )
        db_session.add_all([version1, version2])
        db_session.commit()

        # 搜索包含 "First" 的版本
        response = authenticated_client.get("/api/v1/admin/versions?search=First")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["version"] == "v1.0.0"

    @patch("src.core.services.version_service.VersionService._get_current_git_info")
    @patch("src.core.services.version_service.VersionService._save_version_config")
    def test_create_version(
        self, mock_save_config, mock_git_info, authenticated_client: TestClient, db_session, test_user
    ):
        """测试创建版本"""
        mock_git_info.return_value = {"commit": "abc123", "branch": "main"}
        mock_save_config.return_value = None

        response = authenticated_client.post(
            "/api/v1/admin/versions",
            json={
                "version": "v1.0.0",
                "description": "Test version",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["status"] == "available"
        assert data["description"] == "Test version"

    def test_create_version_duplicate(self, authenticated_client: TestClient, db_session, test_user):
        """测试创建重复版本"""
        # 先创建一个版本
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        # 尝试创建相同版本
        response = authenticated_client.post(
            "/api/v1/admin/versions",
            json={"version": "v1.0.0"},
        )
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_create_version_invalid_format(self, authenticated_client: TestClient):
        """测试创建无效格式的版本号"""
        response = authenticated_client.post(
            "/api/v1/admin/versions",
            json={"version": "invalid-version"},
        )
        assert response.status_code == 422  # Validation error

    @patch("src.core.services.version_service.VersionService._get_git_info_from_tag")
    @patch("src.core.services.version_service.VersionService._save_version_config")
    def test_create_version_with_git_tag(
        self, mock_save_config, mock_git_info, authenticated_client: TestClient, db_session, test_user
    ):
        """测试基于 Git Tag 创建版本"""
        mock_git_info.return_value = {"commit": "def456", "branch": "release/v1.0.0"}
        mock_save_config.return_value = None

        response = authenticated_client.post(
            "/api/v1/admin/versions",
            json={
                "version": "v1.0.0",
                "git_tag": "v1.0.0",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["git_tag"] == "v1.0.0"

    def test_get_version_not_found(self, authenticated_client: TestClient):
        """测试获取不存在的版本"""
        response = authenticated_client.get("/api/v1/admin/versions/v999.0.0")
        assert response.status_code == 404

    def test_get_version_detail(self, authenticated_client: TestClient, db_session, test_user):
        """测试获取版本详情"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            git_commit="abc123",
            git_branch="main",
            image_tag="aam-service:v1.0.0",
            description="Test version",
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/versions/v1.0.0")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["status"] == "active"
        assert data["git_commit"] == "abc123"
        assert data["description"] == "Test version"

    def test_get_version_detail_with_config(self, authenticated_client: TestClient, db_session, test_user):
        """测试获取版本详情（包含配置）"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.flush()

        config = VersionConfig(
            version_id=version.id,
            docker_compose_config={"services": {"aam-service": {"image": "aam-service:v1.0.0"}}},
            environment_variables={"APP_VERSION": "v1.0.0"},
            config_snapshot={"version": "v1.0.0"},
        )
        db_session.add(config)
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/versions/v1.0.0")
        assert response.status_code == 200
        data = response.json()
        assert data["docker_compose_config"] is not None
        assert data["environment_variables"] is not None

    def test_compare_versions_not_found(self, authenticated_client: TestClient):
        """测试比较不存在的版本"""
        response = authenticated_client.get("/api/v1/admin/versions/v1.0.0/compare/v2.0.0")
        assert response.status_code == 404

    def test_compare_versions(self, authenticated_client: TestClient, db_session, test_user):
        """测试版本比较"""
        version1 = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        version2 = Version(
            version="v1.1.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add_all([version1, version2])
        db_session.flush()

        config1 = VersionConfig(
            version_id=version1.id,
            config_snapshot={"key1": "value1"},
        )
        config2 = VersionConfig(
            version_id=version2.id,
            config_snapshot={"key1": "value2"},
        )
        db_session.add_all([config1, config2])
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/versions/v1.0.0/compare/v1.1.0")
        assert response.status_code == 200
        data = response.json()
        assert "differences" in data
        assert data["v1"] == "v1.0.0"
        assert data["v2"] == "v1.1.0"

    def test_get_active_version_not_found(self, authenticated_client: TestClient):
        """测试获取活动版本（不存在）"""
        response = authenticated_client.get("/api/v1/admin/versions/active")
        assert response.status_code == 404

    def test_get_active_version(self, authenticated_client: TestClient, db_session, test_user):
        """测试获取活动版本"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/versions/active")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["status"] == "active"

    def test_delete_version_not_found(self, authenticated_client: TestClient):
        """测试删除不存在的版本"""
        response = authenticated_client.delete("/api/v1/admin/versions/v999.0.0")
        assert response.status_code == 404

    def test_delete_version_active(self, authenticated_client: TestClient, db_session, test_user):
        """测试删除活动版本（应该失败）"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        response = authenticated_client.delete("/api/v1/admin/versions/v1.0.0")
        assert response.status_code == 400
        assert "活动版本" in response.json()["detail"] or "不能删除" in response.json()["detail"]

    def test_delete_version_success(self, authenticated_client: TestClient, db_session, test_user):
        """测试删除版本（成功）"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        response = authenticated_client.delete("/api/v1/admin/versions/v1.0.0")
        assert response.status_code == 204

        # 验证版本已删除
        response = authenticated_client.get("/api/v1/admin/versions/v1.0.0")
        assert response.status_code == 404

