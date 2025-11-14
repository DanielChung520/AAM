"""
@purpose: 版本服务，负责版本管理的业务逻辑
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.core.services.version_repository import VersionRepository
from src.models.schemas.version import VersionFilter, VersionStatus
from src.models.version import Version, VersionConfig

logger = logging.getLogger(__name__)


class VersionService:
    """版本服务类"""

    def __init__(self, db: Session):
        """
        初始化版本服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.repository = VersionRepository(db)

    def create_version(
        self,
        version: str,
        git_tag: Optional[str] = None,
        description: Optional[str] = None,
        image_tag: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> Version:
        """
        创建新版本

        Args:
            version: 版本号
            git_tag: Git Tag（可选）
            description: 版本描述
            image_tag: Docker 镜像标签
            created_by: 创建者 ID

        Returns:
            Version: 版本对象

        Raises:
            ValueError: 如果版本已存在
        """
        # 检查版本是否已存在
        existing_version = (
            self.db.query(Version).filter(Version.version == version).first()
        )
        if existing_version:
            raise ValueError(f"版本 {version} 已存在")

        # 获取 Git 信息
        git_commit = None
        git_branch = None
        if git_tag:
            git_info = self._get_git_info_from_tag(git_tag)
            git_commit = git_info.get("commit")
            git_branch = git_info.get("branch")
        else:
            # 如果没有提供 git_tag，尝试获取当前 Git 信息
            git_info = self._get_current_git_info()
            git_commit = git_info.get("commit")
            git_branch = git_info.get("branch")

        # 如果没有提供 image_tag，根据版本号生成
        if not image_tag:
            image_tag = f"aam-service:{version}"

        # 创建版本对象
        version_obj = Version(
            version=version,
            status=VersionStatus.AVAILABLE,
            git_commit=git_commit,
            git_branch=git_branch,
            git_tag=git_tag,
            image_tag=image_tag,
            description=description,
            created_by=created_by,
        )

        self.db.add(version_obj)
        self.db.commit()
        self.db.refresh(version_obj)

        # 保存版本配置快照
        self.repository.save_version_config(version_obj)

        logger.info(f"版本已创建: {version}")
        return version_obj

    def get_version(self, version: str) -> Optional[Version]:
        """
        获取版本详情

        Args:
            version: 版本号

        Returns:
            Optional[Version]: 版本对象，如果不存在返回 None
        """
        return self.db.query(Version).filter(Version.version == version).first()

    def list_versions(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[VersionFilter] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Version], int]:
        """
        获取版本列表

        Args:
            page: 页码
            page_size: 每页数量
            filters: 过滤条件
            sort_by: 排序字段
            sort_order: 排序顺序（asc/desc）

        Returns:
            Tuple[List[Version], int]: 版本列表和总数量
        """
        query = self.db.query(Version)

        # 应用过滤条件
        if filters:
            if filters.status:
                query = query.filter(Version.status == filters.status)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Version.version.like(search_term),
                        Version.description.like(search_term),
                    )
                )
            if filters.created_after:
                query = query.filter(Version.created_at >= filters.created_after)
            if filters.created_before:
                query = query.filter(Version.created_at <= filters.created_before)

        # 排序
        sort_column = getattr(Version, sort_by, Version.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        versions = query.offset(offset).limit(page_size).all()

        return versions, total

    def get_active_version(self) -> Optional[Version]:
        """
        获取当前活动版本

        Returns:
            Optional[Version]: 活动版本对象，如果不存在返回 None
        """
        return (
            self.db.query(Version)
            .filter(Version.status == VersionStatus.ACTIVE)
            .first()
        )

    def set_active_version(self, version: str) -> Version:
        """
        设置活动版本

        Args:
            version: 版本号

        Returns:
            Version: 版本对象

        Raises:
            ValueError: 如果版本不存在
        """
        version_obj = self.get_version(version)
        if not version_obj:
            raise ValueError(f"版本 {version} 不存在")

        # 取消当前活动版本
        current_active = self.get_active_version()
        if current_active:
            current_active.status = VersionStatus.AVAILABLE
            self.db.add(current_active)

        # 设置新活动版本
        version_obj.status = VersionStatus.ACTIVE
        self.db.add(version_obj)
        self.db.commit()
        self.db.refresh(version_obj)

        logger.info(f"活动版本已更新: {version}")
        return version_obj

    def delete_version(self, version: str) -> bool:
        """
        删除版本（仅非活动版本）

        Args:
            version: 版本号

        Returns:
            bool: 是否成功删除

        Raises:
            ValueError: 如果版本是活动版本或有依赖关系
        """
        version_obj = self.get_version(version)
        if not version_obj:
            return False

        # 检查是否为活动版本
        if version_obj.status == VersionStatus.ACTIVE:
            raise ValueError("不能删除活动版本")

        # 检查依赖关系
        if self.repository.check_version_dependencies(version_obj):
            raise ValueError("版本存在部署记录，无法删除")

        # 删除版本配置
        self.repository.delete_version_config(version_obj)

        # 删除版本
        self.db.delete(version_obj)
        self.db.commit()

        logger.info(f"版本已删除: {version}")
        return True

    def compare_versions(self, version1: str, version2: str) -> Dict:
        """
        比较两个版本的配置差异

        Args:
            version1: 版本1
            version2: 版本2

        Returns:
            Dict: 配置差异
        """
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)

        if not v1 or not v2:
            raise ValueError("版本不存在")

        v1_config = self.repository.get_version_config(v1)
        v2_config = self.repository.get_version_config(v2)

        differences = {}
        summary = {"added": 0, "removed": 0, "modified": 0}

        # 比较各个配置项
        config_keys = [
            "docker_compose_config",
            "environment_variables",
            "service_config",
        ]

        for key in config_keys:
            v1_value = getattr(v1_config, key) if v1_config else None
            v2_value = getattr(v2_config, key) if v2_config else None

            diff = self._compare_config_values(v1_value, v2_value)
            if diff["added"] or diff["removed"] or diff["modified"]:
                differences[key] = diff
                summary["added"] += len(diff["added"])
                summary["removed"] += len(diff["removed"])
                summary["modified"] += len(diff["modified"])

        return {
            "version1": version1,
            "version2": version2,
            "differences": differences,
            "summary": summary,
        }

    def _compare_config_values(
        self, value1: Optional[Dict], value2: Optional[Dict]
    ) -> Dict:
        """
        比较两个配置值

        Args:
            value1: 配置值1
            value2: 配置值2

        Returns:
            Dict: 差异结果
        """
        if value1 is None and value2 is None:
            return {"added": [], "removed": [], "modified": []}

        if value1 is None:
            return {
                "added": list(value2.keys()) if isinstance(value2, dict) else [],
                "removed": [],
                "modified": [],
            }

        if value2 is None:
            return {
                "added": [],
                "removed": list(value1.keys()) if isinstance(value1, dict) else [],
                "modified": [],
            }

        if not isinstance(value1, dict) or not isinstance(value2, dict):
            if value1 != value2:
                return {"added": [], "removed": [], "modified": ["root"]}
            return {"added": [], "removed": [], "modified": []}

        added = []
        removed = []
        modified = []

        all_keys = set(value1.keys()) | set(value2.keys())

        for key in all_keys:
            if key not in value1:
                added.append(key)
            elif key not in value2:
                removed.append(key)
            elif value1[key] != value2[key]:
                modified.append(key)

        return {"added": added, "removed": removed, "modified": modified}

    def _get_git_info_from_tag(self, tag: str) -> Dict[str, Optional[str]]:
        """
        从 Git Tag 获取信息

        Args:
            tag: Git Tag

        Returns:
            Dict: Git 信息（commit, branch）
        """
        try:
            # 获取 Tag 对应的 Commit
            result = subprocess.run(
                ["git", "rev-parse", tag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commit = result.stdout.strip()
                # 尝试获取分支信息
                branch_result = subprocess.run(
                    ["git", "branch", "-r", "--contains", commit],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                branch = None
                if branch_result.returncode == 0 and branch_result.stdout:
                    branch = branch_result.stdout.split()[0] if branch_result.stdout.split() else None
                return {"commit": commit, "branch": branch}
        except Exception as e:
            logger.warning(f"获取 Git Tag 信息失败: {e}")

        return {"commit": None, "branch": None}

    def _get_current_git_info(self) -> Dict[str, Optional[str]]:
        """
        获取当前 Git 信息

        Returns:
            Dict: Git 信息（commit, branch）
        """
        try:
            # 获取当前 Commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None

            # 获取当前分支
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None

            return {"commit": commit, "branch": branch}
        except Exception as e:
            logger.warning(f"获取当前 Git 信息失败: {e}")

        return {"commit": None, "branch": None}

