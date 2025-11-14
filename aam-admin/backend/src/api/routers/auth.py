"""
@purpose: 认证路由，处理登录、登出、Token 刷新等
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import hashlib
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.core.services.auth_service import AuthService
from src.infrastructure.database import get_db
from src.models.database import TokenRecord, TokenStatus, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)


# 请求/响应模型
class LoginRequest(BaseModel):
    """登录请求"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应"""

    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    """用户信息响应"""

    id: int
    username: str
    email: str
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""

    message: str


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService()),
):
    """
    用户登录

    Args:
        request: 登录请求
        db: 数据库会话
        auth_service: 认证服务

    Returns:
        LoginResponse: 登录响应（包含 access_token 和 refresh_token）

    Raises:
        HTTPException: 当用户名或密码错误时
    """
    # 查询用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        logger.warning(f"Login attempt with non-existent username: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 验证密码
    if not auth_service.verify_password(request.password, user.hashed_password):
        logger.warning(f"Login attempt with wrong password for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 检查用户是否激活
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 创建令牌
    access_token = auth_service.create_access_token(
        user_id=user.id, username=user.username, role=user.role.value
    )
    refresh_token = auth_service.create_refresh_token(user_id=user.id)

    # 保存 Token 记录
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()
    token_record = TokenRecord(
        token_hash=token_hash,
        user_id=user.id,
        name="Login Token",
        status=TokenStatus.ACTIVE,
        issued_at=datetime.utcnow(),
    )
    db.add(token_record)
    db.commit()

    # 更新用户最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in successfully: {user.username}")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
        },
    )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService()),
):
    """
    刷新访问令牌

    Args:
        request: 刷新令牌请求
        db: 数据库会话
        auth_service: 认证服务

    Returns:
        RefreshTokenResponse: 新的访问令牌

    Raises:
        HTTPException: 当刷新令牌无效时
    """
    # 验证刷新令牌
    payload = auth_service.verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的刷新令牌",
        )

    # 获取用户 ID
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    # 创建新的访问令牌
    access_token = auth_service.create_access_token(
        user_id=user.id, username=user.username, role=user.role.value
    )

    logger.info(f"Access token refreshed for user: {user.username}")

    return RefreshTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """
    用户登出（撤销令牌）

    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话

    Returns:
        dict: 登出成功消息
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
        )

    token = credentials.credentials
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # 撤销令牌
    token_record = (
        db.query(TokenRecord)
        .filter(
            TokenRecord.token_hash == token_hash,
            TokenRecord.status == TokenStatus.ACTIVE,
        )
        .first()
    )

    if token_record:
        token_record.status = TokenStatus.REVOKED
        token_record.revoked_at = datetime.utcnow()
        db.commit()
        logger.info(f"Token revoked for user_id={token_record.user_id}")

    return {"message": "登出成功"}


@router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService()),
):
    """
    获取当前用户信息

    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话
        auth_service: 认证服务

    Returns:
        UserInfoResponse: 用户信息

    Raises:
        HTTPException: 当认证失败时
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
        )

    token = credentials.credentials
    payload = auth_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return UserInfoResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
    )


@router.post("/change-password", response_model=ChangePasswordResponse, status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(lambda: AuthService()),
):
    """
    修改当前用户密码

    Args:
        request: 修改密码请求
        credentials: HTTP Bearer 凭证
        db: 数据库会话
        auth_service: 认证服务

    Returns:
        ChangePasswordResponse: 修改密码响应

    Raises:
        HTTPException: 当认证失败或旧密码错误时
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
        )

    token = credentials.credentials
    payload = auth_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 验证旧密码
    if not auth_service.verify_password(request.old_password, user.hashed_password):
        logger.warning(f"Password change failed: wrong old password for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )

    # 验证新密码长度
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少为6个字符",
        )

    # 更新密码
    user.hashed_password = auth_service.get_password_hash(request.new_password)
    db.commit()

    logger.info(f"Password changed successfully for user: {user.username}")

    return ChangePasswordResponse(message="密码修改成功")
