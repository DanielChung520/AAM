"""
@purpose: 安全管理路由，提供 Token 管理、企业认证配置、审计日志等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.auth_service import AuthService
from src.core.services.token_management_service import TokenManagementService
from src.infrastructure.database import get_db
from src.models.database import User, TokenRecord, TokenStatus, AuditLog, AuditAction
from src.models.schemas.security import (
    TokenCreateRequest,
    TokenResponse,
    TokenIssueResponse,
    TokenRevokeRequest,
    EnterpriseAuthConfig,
    EnterpriseAuthConfigUpdate,
    EnterpriseAuthTestRequest,
    EnterpriseAuthTestResponse,
    AuditLogResponse,
    AuditLogListResponse,
    AuditLogFilter,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/security", tags=["安全管理"])


def get_token_management_service(
    db: Session = Depends(get_db),
) -> TokenManagementService:
    """
    获取 Token 管理服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        TokenManagementService: Token 管理服务实例
    """
    return TokenManagementService(db=db)


def get_auth_service() -> AuthService:
    """
    获取认证服务实例（依赖注入）

    Returns:
        AuthService: 认证服务实例
    """
    return AuthService()


# ==================== Token 管理端点 ====================


@router.get("/tokens", response_model=list[TokenResponse], status_code=status.HTTP_200_OK)
async def list_tokens(
    user_id: Optional[int] = Query(None, description="用户 ID（可选）"),
    status: Optional[str] = Query(None, description="Token 状态（active/revoked/expired）"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(auth_middleware.get_current_user),
    token_service: TokenManagementService = Depends(get_token_management_service),
):
    """
    获取 Token 列表

    Args:
        user_id: 用户 ID（可选）
        status: Token 状态（可选）
        limit: 返回数量限制
        offset: 偏移量
        current_user: 当前认证用户
        token_service: Token 管理服务

    Returns:
        list[TokenResponse]: Token 列表
    """
    try:
        # 解析状态
        token_status = None
        if status:
            try:
                token_status = TokenStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的 Token 状态: {status}",
                )

        tokens, total = token_service.list_tokens(
            user_id=user_id, status=token_status, limit=limit, offset=offset
        )

        # 转换为响应格式（隐藏完整 token_hash，只显示前 8 位）
        token_responses = []
        for token in tokens:
            token_hash_display = token.token_hash[:8] + "***" if len(token.token_hash) > 8 else token.token_hash
            token_responses.append(
                TokenResponse(
                    id=token.id,
                    token_hash=token_hash_display,
                    user_id=token.user_id,
                    name=token.name,
                    status=token.status.value,
                    issued_at=token.issued_at,
                    expires_at=token.expires_at,
                    revoked_at=token.revoked_at,
                    last_used_at=token.last_used_at,
                    extra_data=token.extra_data,
                )
            )

        return token_responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tokens: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 Token 列表失败",
        )


@router.post("/tokens/issue", response_model=TokenIssueResponse, status_code=status.HTTP_201_CREATED)
async def issue_token(
    request: TokenCreateRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    token_service: TokenManagementService = Depends(get_token_management_service),
):
    """
    发行 Token

    Args:
        request: Token 发行请求
        current_user: 当前认证用户
        token_service: Token 管理服务

    Returns:
        TokenIssueResponse: Token 发行响应（包含 Token 字符串和记录）
    """
    try:
        token_str, token_record = token_service.issue_token(
            user_id=request.user_id,
            name=request.name,
            expires_hours=request.expires_hours,
            extra_data=request.extra_data,
        )

        # 转换为响应格式
        token_hash_display = (
            token_record.token_hash[:8] + "***"
            if len(token_record.token_hash) > 8
            else token_record.token_hash
        )

        token_response = TokenResponse(
            id=token_record.id,
            token_hash=token_hash_display,
            user_id=token_record.user_id,
            name=token_record.name,
            status=token_record.status.value,
            issued_at=token_record.issued_at,
            expires_at=token_record.expires_at,
            revoked_at=token_record.revoked_at,
            last_used_at=token_record.last_used_at,
            extra_data=token_record.extra_data,
        )

        return TokenIssueResponse(token=token_str, token_record=token_response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error issuing token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发行 Token 失败",
        )


@router.post("/tokens/{token_id}/revoke", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def revoke_token(
    token_id: int,
    request: TokenRevokeRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    token_service: TokenManagementService = Depends(get_token_management_service),
):
    """
    撤销 Token

    Args:
        token_id: Token ID
        request: Token 撤销请求
        current_user: 当前认证用户
        token_service: Token 管理服务

    Returns:
        TokenResponse: 更新后的 Token 记录
    """
    try:
        token_record = token_service.revoke_token(token_id, reason=request.reason)

        # 转换为响应格式
        token_hash_display = (
            token_record.token_hash[:8] + "***"
            if len(token_record.token_hash) > 8
            else token_record.token_hash
        )

        return TokenResponse(
            id=token_record.id,
            token_hash=token_hash_display,
            user_id=token_record.user_id,
            name=token_record.name,
            status=token_record.status.value,
            issued_at=token_record.issued_at,
            expires_at=token_record.expires_at,
            revoked_at=token_record.revoked_at,
            last_used_at=token_record.last_used_at,
            extra_data=token_record.extra_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error revoking token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤销 Token 失败",
        )


@router.get("/tokens/{token_id}", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def get_token(
    token_id: int,
    current_user: User = Depends(auth_middleware.get_current_user),
    token_service: TokenManagementService = Depends(get_token_management_service),
):
    """
    获取 Token 详情

    Args:
        token_id: Token ID
        current_user: 当前认证用户
        token_service: Token 管理服务

    Returns:
        TokenResponse: Token 详情
    """
    try:
        token_record = token_service.get_token(token_id)
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Token ID {token_id} 不存在",
            )

        # 转换为响应格式
        token_hash_display = (
            token_record.token_hash[:8] + "***"
            if len(token_record.token_hash) > 8
            else token_record.token_hash
        )

        return TokenResponse(
            id=token_record.id,
            token_hash=token_hash_display,
            user_id=token_record.user_id,
            name=token_record.name,
            status=token_record.status.value,
            issued_at=token_record.issued_at,
            expires_at=token_record.expires_at,
            revoked_at=token_record.revoked_at,
            last_used_at=token_record.last_used_at,
            extra_data=token_record.extra_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 Token 详情失败",
        )


# ==================== 企业认证配置端点 ====================


@router.get("/enterprise-auth", response_model=EnterpriseAuthConfig, status_code=status.HTTP_200_OK)
async def get_enterprise_auth_config(
    current_user: User = Depends(auth_middleware.get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    获取企业认证配置

    Args:
        current_user: 当前认证用户
        auth_service: 认证服务

    Returns:
        EnterpriseAuthConfig: 企业认证配置
    """
    try:
        settings = auth_service.settings
        secret_key = settings.auth.secret_key

        # 检查是否设置了企业 Secret Key（这里简化处理，实际应该从配置中读取）
        # 如果 secret_key 是默认值，则认为未设置
        secret_key_set = secret_key != "your-secret-key-change-in-production"

        # 只显示前 8 位
        secret_key_display = None
        if secret_key_set and secret_key:
            secret_key_display = secret_key[:8] + "***"

        return EnterpriseAuthConfig(
            enabled=False,  # 从配置中读取，这里简化处理
            secret_key=secret_key_display,
            secret_key_set=secret_key_set,
        )
    except Exception as e:
        logger.error(f"Error getting enterprise auth config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取企业认证配置失败",
        )


@router.put("/enterprise-auth", response_model=EnterpriseAuthConfig, status_code=status.HTTP_200_OK)
async def update_enterprise_auth_config(
    request: EnterpriseAuthConfigUpdate,
    current_user: User = Depends(auth_middleware.get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    更新企业认证配置

    Args:
        request: 企业认证配置更新请求
        current_user: 当前认证用户
        auth_service: 认证服务

    Returns:
        EnterpriseAuthConfig: 更新后的企业认证配置

    Note:
        这里简化处理，实际应该将配置保存到数据库或配置文件
    """
    try:
        # 这里简化处理，实际应该保存配置到数据库或配置文件
        # 暂时只返回更新后的配置（不实际保存）

        secret_key_display = None
        if request.secret_key:
            secret_key_display = request.secret_key[:8] + "***"

        return EnterpriseAuthConfig(
            enabled=request.enabled,
            secret_key=secret_key_display,
            secret_key_set=bool(request.secret_key),
        )
    except Exception as e:
        logger.error(f"Error updating enterprise auth config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新企业认证配置失败",
        )


@router.post("/enterprise-auth/test", response_model=EnterpriseAuthTestResponse, status_code=status.HTTP_200_OK)
async def test_enterprise_auth(
    request: EnterpriseAuthTestRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    测试企业认证签名

    Args:
        request: 企业认证测试请求
        current_user: 当前认证用户
        auth_service: 认证服务

    Returns:
        EnterpriseAuthTestResponse: 测试响应（包含生成的签名）
    """
    try:
        signature = auth_service.generate_enterprise_signature(
            user_id=request.user_id, token=request.token
        )

        return EnterpriseAuthTestResponse(
            success=True,
            signature=signature,
            message="企业认证签名生成成功",
        )
    except Exception as e:
        logger.error(f"Error testing enterprise auth: {e}", exc_info=True)
        return EnterpriseAuthTestResponse(
            success=False,
            signature=None,
            message=f"企业认证签名生成失败: {str(e)}",
        )


# ==================== 审计日志端点 ====================


@router.get("/audit-logs", response_model=AuditLogListResponse, status_code=status.HTTP_200_OK)
async def list_audit_logs(
    user_id: Optional[int] = Query(None, description="用户 ID（可选）"),
    action: Optional[str] = Query(None, description="操作类型（可选）"),
    resource_type: Optional[str] = Query(None, description="资源类型（可选）"),
    status: Optional[str] = Query(None, description="操作状态（可选）"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(auth_middleware.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取审计日志列表

    Args:
        user_id: 用户 ID（可选）
        action: 操作类型（可选）
        resource_type: 资源类型（可选）
        status: 操作状态（可选）
        start_time: 开始时间（ISO 格式）
        end_time: 结束时间（ISO 格式）
        page: 页码
        page_size: 每页数量
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        AuditLogListResponse: 审计日志列表响应
    """
    try:
        from datetime import datetime

        # 构建查询
        query = db.query(AuditLog)

        # 应用过滤条件
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            try:
                action_enum = AuditAction(action)
                query = query.filter(AuditLog.action == action_enum)
            except ValueError:
                pass

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if status:
            query = query.filter(AuditLog.status == status)

        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                query = query.filter(AuditLog.created_at >= start_dt)
            except ValueError:
                pass

        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                query = query.filter(AuditLog.created_at <= end_dt)
            except ValueError:
                pass

        # 获取总数
        total = query.count()

        # 应用排序和分页
        offset = (page - 1) * page_size
        logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size).all()

        # 转换为响应格式
        log_responses = []
        for log in logs:
            # 获取用户名
            username = None
            if log.user_id:
                user = db.query(User).filter(User.id == log.user_id).first()
                if user:
                    username = user.username

            log_responses.append(
                AuditLogResponse(
                    id=log.id,
                    user_id=log.user_id,
                    username=username,
                    action=log.action.value,
                    resource_type=log.resource_type,
                    resource_id=log.resource_id,
                    description=log.description,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    status=log.status,
                    error_message=log.error_message,
                    created_at=log.created_at,
                )
            )

        return AuditLogListResponse(
            items=log_responses,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Error listing audit logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志列表失败",
        )


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse, status_code=status.HTTP_200_OK)
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(auth_middleware.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取审计日志详情

    Args:
        log_id: 审计日志 ID
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        AuditLogResponse: 审计日志详情
    """
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"审计日志 ID {log_id} 不存在",
            )

        # 获取用户名
        username = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                username = user.username

        return AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=username,
            action=log.action.value,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            status=log.status,
            error_message=log.error_message,
            created_at=log.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志详情失败",
        )

