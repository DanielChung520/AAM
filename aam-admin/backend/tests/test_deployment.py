"""
@purpose: 部署管理路由单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

from src.models.database import DeploymentRecord, DeploymentStatus
from src.models.version import Version, VersionStatus


class TestDeploymentRoutes:
    """部署管理路由测试类"""

    def test_list_deployments_unauthorized(self, client: TestClient):
        """测试未授权访问部署列表"""
        response = client.get("/api/v1/admin/deployments")
        assert response.status_code == 401

    def test_list_deployments_empty(self, authenticated_client: TestClient, db_session):
        """测试获取空部署列表"""
        response = authenticated_client.get("/api/v1/admin/deployments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_list_deployments_with_data(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试获取部署列表（有数据）"""
        # 创建测试版本
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        # 创建部署记录
        deployment1 = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
            deployment_strategy="blue_green",
        )
        deployment2 = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.FAILED,
            operator_id=test_user.id,
            deployment_strategy="rolling",
        )
        db_session.add_all([deployment1, deployment2])
        db_session.commit()

        response = authenticated_client.get("/api/v1/admin/deployments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_deployments_with_status_filter(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试部署列表状态过滤"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        deployment1 = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
        )
        deployment2 = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.FAILED,
            operator_id=test_user.id,
        )
        db_session.add_all([deployment1, deployment2])
        db_session.commit()

        # 过滤 SUCCESS 状态
        response = authenticated_client.get("/api/v1/admin/deployments?status=success")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "success"

    def test_list_deployments_with_version_filter(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试部署列表版本过滤"""
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
        db_session.commit()

        deployment1 = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
        )
        deployment2 = DeploymentRecord(
            version="v1.1.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
        )
        db_session.add_all([deployment1, deployment2])
        db_session.commit()

        # 过滤 v1.0.0 版本
        response = authenticated_client.get("/api/v1/admin/deployments?version=v1.0.0")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["version"] == "v1.0.0"

    def test_get_deployment_not_found(self, authenticated_client: TestClient):
        """测试获取不存在的部署记录"""
        response = authenticated_client.get("/api/v1/admin/deployments/999")
        assert response.status_code == 404

    def test_get_deployment_detail(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试获取部署详情"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        deployment = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
            deployment_strategy="blue_green",
            config_snapshot={"key": "value"},
        )
        db_session.add(deployment)
        db_session.commit()

        response = authenticated_client.get(f"/api/v1/admin/deployments/{deployment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == deployment.id
        assert data["version"] == "v1.0.0"
        assert data["status"] == "success"
        assert data["deployment_strategy"] == "blue_green"

    @patch("src.core.services.deployment_service.DeploymentService.preview_deployment")
    def test_deploy_version_preview(
        self, mock_preview, authenticated_client: TestClient, db_session, test_user
    ):
        """测试部署预览"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        mock_preview.return_value = MagicMock(
            dict=lambda: {
                "version": "v1.0.0",
                "strategy": "blue_green",
                "config_valid": True,
                "dependencies_ok": True,
                "warnings": [],
                "errors": [],
            }
        )

        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/v1.0.0/deploy",
            json={
                "version": "v1.0.0",
                "strategy": "blue_green",
                "preview": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["config_valid"] is True
        assert data["dependencies_ok"] is True

    @patch("src.core.services.deployment_service.DeploymentService.deploy_version")
    def test_deploy_version(
        self, mock_deploy, authenticated_client: TestClient, db_session, test_user
    ):
        """测试部署版本"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        mock_deploy.return_value = 1

        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/v1.0.0/deploy",
            json={
                "version": "v1.0.0",
                "strategy": "blue_green",
                "config": {},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "deployment_id" in data
        assert data["deployment_id"] == 1

    def test_deploy_version_not_found(
        self, authenticated_client: TestClient, db_session
    ):
        """测试部署不存在的版本"""
        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/v999.0.0/deploy",
            json={
                "version": "v999.0.0",
                "strategy": "blue_green",
            },
        )
        assert response.status_code == 400

    @patch("src.core.services.deployment_service.DeploymentService.rollback_version")
    def test_rollback_version(
        self, mock_rollback, authenticated_client: TestClient, db_session, test_user
    ):
        """测试回滚版本"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.ACTIVE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        mock_rollback.return_value = 1

        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/v1.0.0/rollback",
            json={
                "target_version": "v0.9.0",
                "reason": "Test rollback",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "deployment_id" in data

    def test_rollback_version_not_found(
        self, authenticated_client: TestClient, db_session
    ):
        """测试回滚不存在的版本"""
        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/v999.0.0/rollback",
            json={
                "target_version": "v0.9.0",
            },
        )
        assert response.status_code == 400

    @patch("src.core.services.deployment_service.DeploymentService.switch_active_version")
    def test_switch_active_version(
        self, mock_switch, authenticated_client: TestClient, db_session, test_user
    ):
        """测试切换活动版本"""
        version = Version(
            version="v1.0.0",
            status=VersionStatus.AVAILABLE,
            created_by=test_user.id,
        )
        db_session.add(version)
        db_session.commit()

        mock_switch.return_value = None

        response = authenticated_client.post(
            "/api/v1/admin/deployments/versions/active/switch?version=v1.0.0"
        )
        assert response.status_code == 200

    def test_get_deployment_status_not_found(self, authenticated_client: TestClient):
        """测试获取不存在的部署状态"""
        response = authenticated_client.get("/api/v1/admin/deployments/999/status")
        assert response.status_code == 404

    @patch("src.core.services.deployment_service.DeploymentService.get_deployment_status")
    def test_get_deployment_status(
        self, mock_status, authenticated_client: TestClient, db_session, test_user
    ):
        """测试获取部署状态"""
        deployment = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.IN_PROGRESS,
            operator_id=test_user.id,
        )
        db_session.add(deployment)
        db_session.commit()

        mock_status.return_value = {
            "id": deployment.id,
            "status": "in_progress",
            "progress": 50.0,
            "current_step": "Deploying containers",
            "steps": [
                {"name": "Prepare", "status": "completed"},
                {"name": "Deploy", "status": "in_progress"},
            ],
        }

        response = authenticated_client.get(f"/api/v1/admin/deployments/{deployment.id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["progress"] == 50.0

    def test_get_deployment_logs_not_found(self, authenticated_client: TestClient):
        """测试获取不存在的部署日志"""
        response = authenticated_client.get("/api/v1/admin/deployments/999/logs")
        assert response.status_code == 404

    def test_get_deployment_logs(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试获取部署日志"""
        deployment = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
            logs="Deployment started\nDeployment completed successfully",
        )
        db_session.add(deployment)
        db_session.commit()

        response = authenticated_client.get(f"/api/v1/admin/deployments/{deployment.id}/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "Deployment started" in data["logs"]

    def test_get_deployment_logs_with_tail(
        self, authenticated_client: TestClient, db_session, test_user
    ):
        """测试获取部署日志（指定行数）"""
        deployment = DeploymentRecord(
            version="v1.0.0",
            status=DeploymentStatus.SUCCESS,
            operator_id=test_user.id,
            logs="\n".join([f"Log line {i}" for i in range(100)]),
        )
        db_session.add(deployment)
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1/admin/deployments/{deployment.id}/logs?tail=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data

