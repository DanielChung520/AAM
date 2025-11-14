"""
@purpose: 系统设置服务，提供配置管理、环境变量管理、健康检查、备份恢复功能
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.config import get_settings, Settings
from src.infrastructure.database import get_db
from src.core.services.docker_service import DockerService

logger = logging.getLogger(__name__)


class SettingsService:
    """系统设置服务类"""

    # 敏感环境变量列表（用于隐藏值）
    SENSITIVE_ENV_VARS = [
        "SECRET_KEY",
        "PASSWORD",
        "PASSWD",
        "TOKEN",
        "API_KEY",
        "API_SECRET",
        "SECRET",
        "AUTH_SECRET_KEY",
        "DB_PASSWORD",
        "DATABASE_PASSWORD",
    ]

    def __init__(self, db: Session):
        """
        初始化系统设置服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.settings = get_settings()
        self.docker_service = DockerService()
        self.env_file_path = Path(".env")

    # ==================== 系统配置管理 ====================

    def get_system_settings(self) -> Dict[str, Any]:
        """
        获取系统配置

        Returns:
            Dict: 系统配置信息
        """
        return {
            "app_name": self.settings.app.app_name,
            "app_version": self.settings.app.app_version,
            "debug": self.settings.app.debug,
            "log_level": self.settings.app.log_level,
            "api_host": self.settings.api.api_host,
            "api_port": self.settings.api.api_port,
            "api_prefix": self.settings.api.api_prefix,
            "cors_origins": self.settings.api.cors_origins,
            "database_url": self._mask_sensitive_info(self.settings.database.database_url),
            "docker_host": self.settings.docker.docker_host,
            "docker_base_url": self.settings.docker.docker_base_url,
        }

    def update_system_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新系统配置（注意：此实现仅返回更新后的配置，实际配置需要重启应用）

        Args:
            updates: 更新的配置项

        Returns:
            Dict: 更新后的系统配置
        """
        # 注意：由于配置是通过环境变量和 Pydantic Settings 管理的，
        # 实际更新需要修改环境变量或配置文件，然后重启应用
        # 这里仅返回更新后的配置预览

        current_settings = self.get_system_settings()
        updated_settings = {**current_settings, **updates}

        logger.warning(
            "系统配置更新需要修改环境变量或配置文件，然后重启应用才能生效"
        )

        return updated_settings

    def _mask_sensitive_info(self, value: str) -> str:
        """隐藏敏感信息"""
        if not value:
            return value
        if "@" in value or "://" in value:
            # 处理 URL 格式（如数据库 URL）
            try:
                parts = value.split("@")
                if len(parts) == 2:
                    return f"***@{parts[1]}"
            except:
                pass
        return value

    # ==================== 环境变量管理 ====================

    def get_environment_variables(self) -> List[Dict[str, Any]]:
        """
        获取环境变量列表

        Returns:
            List[Dict]: 环境变量列表
        """
        env_vars = []

        # 从 .env 文件读取
        if self.env_file_path.exists():
            with open(self.env_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        is_sensitive = any(
                            sensitive in key.upper() for sensitive in self.SENSITIVE_ENV_VARS
                        )
                        env_vars.append(
                            {
                                "key": key,
                                "value": value if not is_sensitive else "***FILTERED***",
                                "is_sensitive": is_sensitive,
                                "description": None,
                            }
                        )

        # 从系统环境变量读取（补充 .env 中没有的）
        for key, value in os.environ.items():
            if not any(ev["key"] == key for ev in env_vars):
                is_sensitive = any(
                    sensitive in key.upper() for sensitive in self.SENSITIVE_ENV_VARS
                )
                env_vars.append(
                    {
                        "key": key,
                        "value": value if not is_sensitive else "***FILTERED***",
                        "is_sensitive": is_sensitive,
                        "description": None,
                    }
                )

        return env_vars

    def update_environment_variable(
        self, key: str, value: str, description: Optional[str] = None
    ) -> bool:
        """
        更新环境变量（写入 .env 文件）

        Args:
            key: 环境变量键
            value: 环境变量值
            description: 描述（可选）

        Returns:
            bool: 是否更新成功
        """
        try:
            # 读取现有 .env 文件
            env_lines = []
            key_found = False

            if self.env_file_path.exists():
                with open(self.env_file_path, "r", encoding="utf-8") as f:
                    env_lines = f.readlines()

            # 更新或添加环境变量
            new_lines = []
            for line in env_lines:
                if line.strip().startswith(f"{key}="):
                    # 更新现有变量
                    comment = ""
                    if "#" in line:
                        comment = " # " + line.split("#", 1)[1].strip()
                    new_lines.append(f'{key}="{value}"{comment}\n')
                    key_found = True
                else:
                    new_lines.append(line)

            # 如果没找到，添加新变量
            if not key_found:
                if description:
                    new_lines.append(f'# {description}\n')
                new_lines.append(f'{key}="{value}"\n')

            # 写入 .env 文件
            with open(self.env_file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            logger.info(f"环境变量已更新: {key}")
            return True
        except Exception as e:
            logger.error(f"更新环境变量失败: {e}", exc_info=True)
            return False

    # ==================== 系统健康检查 ====================

    def get_system_health(self) -> Dict[str, Any]:
        """
        获取系统健康状态

        Returns:
            Dict: 系统健康状态
        """
        checks = {}
        overall_status = "healthy"

        # 检查数据库连接
        db_status = self._check_database()
        checks["database"] = db_status
        if db_status["status"] != "healthy":
            overall_status = "unhealthy"

        # 检查 Docker 连接
        docker_status = self._check_docker()
        checks["docker"] = docker_status
        if docker_status["status"] != "healthy":
            overall_status = "warning" if overall_status == "healthy" else overall_status

        # 检查 AAM 服务连接
        aam_status = self._check_aam_service()
        checks["aam_service"] = aam_status
        if aam_status["status"] != "healthy":
            overall_status = "warning" if overall_status == "healthy" else overall_status

        # 检查磁盘空间
        disk_status = self._check_disk_space()
        checks["disk"] = disk_status
        if disk_status["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif disk_status["status"] == "warning" and overall_status == "healthy":
            overall_status = "warning"

        # 检查内存使用
        memory_status = self._check_memory()
        checks["memory"] = memory_status
        if memory_status["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif memory_status["status"] == "warning" and overall_status == "healthy":
            overall_status = "warning"

        return {
            "overall_status": overall_status,
            "checks": checks,
            "timestamp": datetime.utcnow(),
        }

    def _check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            # 尝试执行简单查询
            self.db.execute(text("SELECT 1"))
            self.db.commit()
            return {
                "status": "healthy",
                "message": "数据库连接正常",
                "details": {"connected": True},
            }
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            self.db.rollback()
            return {
                "status": "unhealthy",
                "message": f"数据库连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _check_docker(self) -> Dict[str, Any]:
        """检查 Docker 连接"""
        try:
            self.docker_service.client.ping()
            return {
                "status": "healthy",
                "message": "Docker 连接正常",
                "details": {"connected": True},
            }
        except Exception as e:
            logger.error(f"Docker 连接检查失败: {e}")
            return {
                "status": "unhealthy",
                "message": f"Docker 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _check_aam_service(self) -> Dict[str, Any]:
        """检查 AAM 服务连接"""
        try:
            import httpx

            aam_url = self.settings.auth.aam_service_url
            health_url = f"{aam_url}/health" if aam_url else None

            if not health_url:
                return {
                    "status": "unknown",
                    "message": "AAM 服务 URL 未配置",
                    "details": {},
                }

            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": "AAM 服务连接正常",
                        "details": {"url": aam_url, "status_code": response.status_code},
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"AAM 服务返回非200状态码: {response.status_code}",
                        "details": {"url": aam_url, "status_code": response.status_code},
                    }
        except Exception as e:
            logger.error(f"AAM 服务连接检查失败: {e}")
            return {
                "status": "unhealthy",
                "message": f"AAM 服务连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage("/")
            total = disk.total
            used = disk.used
            free = disk.free
            percent = (used / total) * 100

            if percent >= 90:
                status = "unhealthy"
                message = f"磁盘空间严重不足 ({percent:.1f}% 已使用)"
            elif percent >= 80:
                status = "warning"
                message = f"磁盘空间不足 ({percent:.1f}% 已使用)"
            else:
                status = "healthy"
                message = f"磁盘空间充足 ({percent:.1f}% 已使用)"

            return {
                "status": status,
                "message": message,
                "details": {
                    "total": total,
                    "used": used,
                    "free": free,
                    "percent": percent,
                },
            }
        except Exception as e:
            logger.error(f"磁盘空间检查失败: {e}")
            return {
                "status": "unknown",
                "message": f"磁盘空间检查失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _check_memory(self) -> Dict[str, Any]:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            total = memory.total
            used = memory.used
            free = memory.available
            percent = memory.percent

            if percent >= 90:
                status = "unhealthy"
                message = f"内存使用率过高 ({percent:.1f}%)"
            elif percent >= 80:
                status = "warning"
                message = f"内存使用率较高 ({percent:.1f}%)"
            else:
                status = "healthy"
                message = f"内存使用正常 ({percent:.1f}%)"

            return {
                "status": status,
                "message": message,
                "details": {
                    "total": total,
                    "used": used,
                    "free": free,
                    "percent": percent,
                },
            }
        except Exception as e:
            logger.error(f"内存检查失败: {e}")
            return {
                "status": "unknown",
                "message": f"内存检查失败: {str(e)}",
                "details": {"error": str(e)},
            }

    # ==================== 备份功能 ====================

    def create_backup(
        self,
        name: Optional[str] = None,
        include_database: bool = True,
        include_config: bool = True,
        include_versions: bool = True,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建系统备份

        Args:
            name: 备份名称（可选）
            include_database: 是否包含数据库
            include_config: 是否包含配置文件
            include_versions: 是否包含版本配置
            description: 描述

        Returns:
            Dict: 备份记录信息
        """
        try:
            # 创建备份目录
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            # 生成备份名称
            if not name:
                name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            backup_path = backup_dir / name
            backup_path.mkdir(exist_ok=True)

            # 备份数据库
            if include_database:
                self._backup_database(backup_path)

            # 备份配置文件
            if include_config:
                self._backup_config(backup_path)

            # 备份版本配置
            if include_versions:
                self._backup_versions(backup_path)

            # 创建备份元数据
            metadata = {
                "name": name,
                "created_at": datetime.utcnow().isoformat(),
                "includes": {
                    "database": include_database,
                    "config": include_config,
                    "versions": include_versions,
                },
                "description": description,
            }

            metadata_path = backup_path / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # 创建压缩包
            archive_path = backup_dir / f"{name}.tar.gz"
            shutil.make_archive(
                str(backup_path), "gztar", str(backup_path.parent), name
            )

            # 计算备份大小
            backup_size = archive_path.stat().st_size if archive_path.exists() else 0

            # 清理临时目录
            shutil.rmtree(backup_path)

            logger.info(f"备份创建成功: {name}")

            return {
                "id": name,
                "name": name,
                "created_at": datetime.utcnow(),
                "size": backup_size,
                "status": "completed",
                "includes": {
                    "database": include_database,
                    "config": include_config,
                    "versions": include_versions,
                },
                "description": description,
            }
        except Exception as e:
            logger.error(f"创建备份失败: {e}", exc_info=True)
            raise

    def _backup_database(self, backup_path: Path):
        """备份数据库"""
        try:
            # 这里应该使用数据库备份工具（如 pg_dump）
            # 简化实现，仅记录
            logger.info("数据库备份功能需要根据实际数据库类型实现")
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")

    def _backup_config(self, backup_path: Path):
        """备份配置文件"""
        try:
            config_dir = backup_path / "config"
            config_dir.mkdir(exist_ok=True)

            # 备份 .env 文件
            if self.env_file_path.exists():
                shutil.copy(self.env_file_path, config_dir / ".env")

            # 备份其他配置文件
            config_files = ["config.json", "settings.json"]
            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    shutil.copy(config_path, config_dir / config_file)
        except Exception as e:
            logger.error(f"配置文件备份失败: {e}")

    def _backup_versions(self, backup_path: Path):
        """备份版本配置"""
        try:
            versions_dir = backup_path / "versions"
            versions_dir.mkdir(exist_ok=True)

            # 备份版本配置文件（如果存在）
            versions_config = Path("../aam-service/config/models.json")
            if versions_config.exists():
                shutil.copy(versions_config, versions_dir / "models.json")
        except Exception as e:
            logger.error(f"版本配置备份失败: {e}")

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        获取备份列表

        Returns:
            List[Dict]: 备份列表
        """
        backups = []
        backup_dir = Path("backups")

        if not backup_dir.exists():
            return backups

        for archive_path in backup_dir.glob("*.tar.gz"):
            try:
                stat = archive_path.stat()
                backup_name = archive_path.stem.replace(".tar", "")

                backups.append(
                    {
                        "id": backup_name,
                        "name": backup_name,
                        "created_at": datetime.fromtimestamp(stat.st_mtime),
                        "size": stat.st_size,
                        "status": "completed",
                        "includes": {
                            "database": True,
                            "config": True,
                            "versions": True,
                        },
                        "description": None,
                    }
                )
            except Exception as e:
                logger.error(f"读取备份信息失败: {archive_path}: {e}")

        # 按创建时间倒序排序
        backups.sort(key=lambda x: x["created_at"], reverse=True)

        return backups

    def restore_backup(
        self,
        backup_id: str,
        restore_database: bool = True,
        restore_config: bool = True,
        restore_versions: bool = True,
    ) -> bool:
        """
        恢复系统备份

        Args:
            backup_id: 备份 ID
            restore_database: 是否恢复数据库
            restore_config: 是否恢复配置文件
            restore_versions: 是否恢复版本配置

        Returns:
            bool: 是否恢复成功
        """
        try:
            backup_dir = Path("backups")
            archive_path = backup_dir / f"{backup_id}.tar.gz"

            if not archive_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_id}")

            # 解压备份
            extract_path = backup_dir / backup_id
            shutil.unpack_archive(str(archive_path), str(extract_path), "gztar")

            # 恢复数据库
            if restore_database:
                self._restore_database(extract_path)

            # 恢复配置文件
            if restore_config:
                self._restore_config(extract_path)

            # 恢复版本配置
            if restore_versions:
                self._restore_versions(extract_path)

            # 清理临时目录
            shutil.rmtree(extract_path)

            logger.info(f"备份恢复成功: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"恢复备份失败: {e}", exc_info=True)
            return False

    def _restore_database(self, backup_path: Path):
        """恢复数据库"""
        try:
            logger.info("数据库恢复功能需要根据实际数据库类型实现")
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")

    def _restore_config(self, backup_path: Path):
        """恢复配置文件"""
        try:
            config_dir = backup_path / "config"
            if config_dir.exists():
                # 恢复 .env 文件
                env_backup = config_dir / ".env"
                if env_backup.exists():
                    shutil.copy(env_backup, self.env_file_path)
        except Exception as e:
            logger.error(f"配置文件恢复失败: {e}")

    def _restore_versions(self, backup_path: Path):
        """恢复版本配置"""
        try:
            versions_dir = backup_path / "versions"
            if versions_dir.exists():
                models_backup = versions_dir / "models.json"
                if models_backup.exists():
                    target_path = Path("../aam-service/config/models.json")
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(models_backup, target_path)
        except Exception as e:
            logger.error(f"版本配置恢复失败: {e}")

