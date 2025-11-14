"""
@purpose: 版本仓库服务，负责版本配置的存储和管理
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.models.version import Version, VersionConfig, VersionStatus

logger = logging.getLogger(__name__)


class VersionRepository:
    """版本仓库服务类"""

    def __init__(self, db: Session):
        """
        初始化版本仓库服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.settings = get_settings()
        self.config_base_path = self._get_config_base_path()

    def _get_config_base_path(self) -> Path:
        """
        获取配置基础路径

        Returns:
            Path: 配置基础路径
        """
        # 尝试多个可能的路径
        possible_paths = [
            Path("../aam-service"),  # 开发环境
            Path("/app"),  # Docker 环境
            Path("."),  # 当前目录
        ]

        for path in possible_paths:
            if (path / "config" / "models.json").exists() or (
                path / "docker-compose.yml"
            ).exists():
                logger.info(f"找到配置基础路径: {path}")
                return path

        # 如果都找不到，使用第一个作为默认路径
        default_path = possible_paths[0]
        logger.warning(f"配置基础路径不存在，将使用默认路径: {default_path}")
        return default_path

    def save_version_config(
        self,
        version: Version,
        docker_compose_config: Optional[Dict] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        service_config: Optional[Dict] = None,
        config_snapshot: Optional[Dict] = None,
    ) -> VersionConfig:
        """
        保存版本配置快照

        Args:
            version: 版本对象
            docker_compose_config: Docker Compose 配置
            environment_variables: 环境变量
            service_config: 服务配置
            config_snapshot: 完整配置快照

        Returns:
            VersionConfig: 版本配置对象
        """
        try:
            # 如果没有提供配置快照，尝试从文件系统读取
            if config_snapshot is None:
                config_snapshot = self._read_current_config_snapshot()

            if docker_compose_config is None:
                docker_compose_config = self._read_docker_compose_config()

            if environment_variables is None:
                environment_variables = self._read_environment_variables()

            if service_config is None:
                service_config = self._read_service_config()

            version_config = VersionConfig(
                version_id=version.id,
                docker_compose_config=docker_compose_config,
                environment_variables=environment_variables,
                service_config=service_config,
                config_snapshot=config_snapshot,
            )

            self.db.add(version_config)
            self.db.commit()
            self.db.refresh(version_config)

            logger.info(f"版本配置已保存: version={version.version}, config_id={version_config.id}")
            return version_config

        except Exception as e:
            self.db.rollback()
            logger.error(f"保存版本配置失败: {e}", exc_info=True)
            raise

    def get_version_config(self, version: Version) -> Optional[VersionConfig]:
        """
        获取版本配置

        Args:
            version: 版本对象

        Returns:
            Optional[VersionConfig]: 版本配置对象，如果不存在返回 None
        """
        return (
            self.db.query(VersionConfig)
            .filter(VersionConfig.version_id == version.id)
            .first()
        )

    def delete_version_config(self, version: Version) -> bool:
        """
        删除版本配置

        Args:
            version: 版本对象

        Returns:
            bool: 是否成功删除
        """
        try:
            version_config = self.get_version_config(version)
            if version_config:
                self.db.delete(version_config)
                self.db.commit()
                logger.info(f"版本配置已删除: version={version.version}")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除版本配置失败: {e}", exc_info=True)
            return False

    def _read_current_config_snapshot(self) -> Dict:
        """
        读取当前配置快照

        Returns:
            Dict: 配置快照
        """
        try:
            snapshot = {
                "models_config": self._read_models_config(),
                "docker_compose": self._read_docker_compose_config(),
                "environment": self._read_environment_variables(),
            }
            return snapshot
        except Exception as e:
            logger.warning(f"读取配置快照失败: {e}")
            return {}

    def _read_models_config(self) -> Dict:
        """
        读取 models.json 配置

        Returns:
            Dict: 模型配置
        """
        config_path = self.config_base_path / "config" / "models.json"
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"读取 models.json 失败: {e}")
            return {}

    def _read_docker_compose_config(self) -> Optional[Dict]:
        """
        读取 docker-compose.yml 配置

        Returns:
            Optional[Dict]: Docker Compose 配置
        """
        compose_path = self.config_base_path / "docker-compose.yml"
        try:
            if compose_path.exists():
                try:
                    import yaml

                    with open(compose_path, "r", encoding="utf-8") as f:
                        return yaml.safe_load(f)
                except ImportError:
                    logger.warning("PyYAML 未安装，无法读取 docker-compose.yml")
                    # 尝试作为 JSON 读取（如果格式兼容）
                    with open(compose_path, "r", encoding="utf-8") as f:
                        return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"读取 docker-compose.yml 失败: {e}")
            return None

    def _read_environment_variables(self) -> Dict[str, str]:
        """
        读取环境变量（从 .env 文件）

        Returns:
            Dict[str, str]: 环境变量字典
        """
        env_path = self.config_base_path / ".env"
        env_vars = {}
        try:
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
            return env_vars
        except Exception as e:
            logger.warning(f"读取 .env 文件失败: {e}")
            return {}

    def _read_service_config(self) -> Dict:
        """
        读取服务配置

        Returns:
            Dict: 服务配置
        """
        # 这里可以读取其他服务配置文件
        # 目前返回空字典
        return {}

    def check_version_dependencies(self, version: Version) -> bool:
        """
        检查版本依赖关系（是否有部署记录使用此版本）

        Args:
            version: 版本对象

        Returns:
            bool: 是否有依赖关系
        """
        from src.models.database import DeploymentRecord

        deployment_count = (
            self.db.query(DeploymentRecord)
            .filter(DeploymentRecord.version == version.version)
            .count()
        )
        return deployment_count > 0

