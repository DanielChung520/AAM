"""
@purpose: 版本管理数据库模型定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models.database import Base


class VersionStatus(str, Enum):
    """版本状态枚举"""

    ACTIVE = "active"
    AVAILABLE = "available"
    DEPRECATED = "deprecated"


class Version(Base):
    """版本表"""

    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(100), unique=True, index=True, nullable=False)  # 版本号
    status = Column(SQLEnum(VersionStatus), default=VersionStatus.AVAILABLE, nullable=False)
    git_commit = Column(String(40), nullable=True)  # Git Commit Hash
    git_branch = Column(String(255), nullable=True)  # Git Branch
    git_tag = Column(String(255), nullable=True)  # Git Tag
    image_tag = Column(String(255), nullable=True)  # Docker 镜像标签
    description = Column(Text, nullable=True)  # 版本描述
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 创建者
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    deployments = relationship("DeploymentRecord", back_populates="version_record")
    configs = relationship("VersionConfig", back_populates="version", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_version_version", "version"),
        Index("idx_version_status", "status"),
        Index("idx_version_created_at", "created_at"),
    )


class VersionConfig(Base):
    """版本配置快照表"""

    __tablename__ = "version_configs"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    docker_compose_config = Column(JSON, nullable=True)  # Docker Compose 配置快照
    environment_variables = Column(JSON, nullable=True)  # 环境变量快照
    service_config = Column(JSON, nullable=True)  # 服务配置快照
    config_snapshot = Column(JSON, nullable=True)  # 完整配置快照
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 关系
    version = relationship("Version", back_populates="configs")

    __table_args__ = (Index("idx_version_config_version_id", "version_id"),)

