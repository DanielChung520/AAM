"""
@purpose: 管理数据库 SQLAlchemy 模型定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from enum import Enum
from typing import Optional

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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserRole(str, Enum):
    """用户角色枚举"""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class TokenStatus(str, Enum):
    """Token 状态枚举"""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class DeploymentStatus(str, Enum):
    """部署状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class AuditAction(str, Enum):
    """审计操作类型枚举"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    START_SERVICE = "start_service"
    STOP_SERVICE = "stop_service"
    RESTART_SERVICE = "restart_service"


class User(Base):
    """管理员用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # 关系
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    deployments = relationship("DeploymentRecord", back_populates="operator_user")

    __table_args__ = (Index("idx_user_username", "username"), Index("idx_user_email", "email"))


class TokenRecord(Base):
    """Token 记录表"""

    __tablename__ = "token_records"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=True)  # Token 名称/描述
    status = Column(SQLEnum(TokenStatus), default=TokenStatus.ACTIVE, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSON, nullable=True)  # 存储额外信息

    __table_args__ = (
        Index("idx_token_hash", "token_hash"),
        Index("idx_token_user", "user_id"),
        Index("idx_token_status", "status"),
    )


class AuditLog(Base):
    """操作审计日志表"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(
        String(100), nullable=False
    )  # 资源类型，如 "llm_provider", "service", "deployment"
    resource_id = Column(String(255), nullable=True)  # 资源 ID
    description = Column(Text, nullable=True)  # 操作描述
    ip_address = Column(String(45), nullable=True)  # IPv4 或 IPv6
    user_agent = Column(String(500), nullable=True)
    request_data = Column(JSON, nullable=True)  # 请求数据
    response_data = Column(JSON, nullable=True)  # 响应数据
    status = Column(String(50), nullable=True)  # 操作状态：success, failed
    error_message = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 关系
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_created", "created_at"),
    )


class DeploymentRecord(Base):
    """部署记录表"""

    __tablename__ = "deployment_records"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(100), nullable=False)  # 版本号
    status = Column(SQLEnum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deployment_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_time = Column(DateTime(timezone=True), nullable=True)
    rollback_version = Column(String(100), nullable=True)  # 回滚版本
    deployment_strategy = Column(String(50), nullable=True)  # 部署策略：blue_green, rolling, canary
    config_snapshot = Column(JSON, nullable=True)  # 配置快照
    logs = Column(Text, nullable=True)  # 部署日志
    error_message = Column(Text, nullable=True)  # 错误信息
    extra_data = Column(JSON, nullable=True)  # 额外信息

    # 关系
    operator_user = relationship("User", back_populates="deployments")
    # 注意：version 是字符串字段，不是外键，需要通过查询关联 Version 模型

    __table_args__ = (
        Index("idx_deployment_version", "version"),
        Index("idx_deployment_status", "status"),
        Index("idx_deployment_operator", "operator_id"),
        Index("idx_deployment_time", "deployment_time"),
    )


class ServiceConfig(Base):
    """服务配置表"""

    __tablename__ = "service_configs"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), unique=True, index=True, nullable=False)  # 服务名称
    config_key = Column(String(255), nullable=False)  # 配置键
    config_value = Column(Text, nullable=True)  # 配置值
    config_type = Column(String(50), nullable=True)  # 配置类型：string, int, bool, json
    description = Column(Text, nullable=True)  # 配置描述
    is_encrypted = Column(Boolean, default=False, nullable=False)  # 是否加密
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_service_config_name", "service_name"),
        Index("idx_service_config_key", "config_key"),
    )
