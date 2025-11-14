"""
@purpose: 安全管理相关的 Schema 类型定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==================== Token 管理相关 Schema ====================


class TokenCreateRequest(BaseModel):
    """Token 发行请求"""

    user_id: Optional[int] = Field(None, description="用户 ID（可选，不提供则创建通用 Token）")
    name: Optional[str] = Field(None, description="Token 名称/描述")
    expires_hours: Optional[int] = Field(24, description="Token 有效期（小时），默认 24 小时")
    extra_data: Optional[dict] = Field(None, description="额外数据")


class TokenResponse(BaseModel):
    """Token 响应"""

    id: int
    token_hash: str = Field(..., description="Token 哈希（仅显示前 8 位）")
    user_id: Optional[int] = None
    name: Optional[str] = None
    status: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    extra_data: Optional[dict] = None

    class Config:
        from_attributes = True


class TokenIssueResponse(BaseModel):
    """Token 发行响应"""

    token: str = Field(..., description="JWT Token（仅在发行时返回一次）")
    token_record: TokenResponse


class TokenRevokeRequest(BaseModel):
    """Token 撤销请求"""

    reason: Optional[str] = Field(None, description="撤销原因")


# ==================== 企业认证配置相关 Schema ====================


class EnterpriseAuthConfig(BaseModel):
    """企业认证配置"""

    enabled: bool = Field(False, description="是否启用企业级认证")
    secret_key: Optional[str] = Field(None, description="企业 Secret Key（仅显示前 8 位）")
    secret_key_set: bool = Field(False, description="是否已设置 Secret Key")


class EnterpriseAuthConfigUpdate(BaseModel):
    """企业认证配置更新请求"""

    enabled: bool = Field(..., description="是否启用企业级认证")
    secret_key: Optional[str] = Field(None, description="企业 Secret Key（如果提供，将更新）")


class EnterpriseAuthTestRequest(BaseModel):
    """企业认证测试请求"""

    user_id: str = Field(..., description="用户 ID")
    token: Optional[str] = Field(None, description="JWT Token（可选）")


class EnterpriseAuthTestResponse(BaseModel):
    """企业认证测试响应"""

    success: bool
    signature: Optional[str] = Field(None, description="生成的签名（用于测试）")
    message: str


# ==================== 审计日志相关 Schema ====================


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogFilter(BaseModel):
    """审计日志过滤条件"""

    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

