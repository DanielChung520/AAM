"""
@purpose: 认证中间件，处理 JWT Token 验证和 API Key 认证
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.services.auth_service import AuthService
from src.infrastructure.database import get_db
from src.models.database import User, TokenRecord, TokenStatus

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    """认证中间件类"""

    def __init__(self):
        """初始化认证中间件"""
        self.auth_service = AuthService()
        self.settings = self.auth_service.settings

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db),
    ) -> User:
        """
        获取当前用户（依赖注入）

        Args:
            credentials: HTTP Bearer 凭证
            db: 数据库会话

        Returns:
            User: 当前用户对象

        Raises:
            HTTPException: 当认证失败时
        """
        token = credentials.credentials

        # 验证令牌
        payload = self.auth_service.verify_token(token, token_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或过期的令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户 ID
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少用户信息",
            )

        # 查询用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用",
            )

        # 检查 Token 记录（可选，用于撤销功能）
        token_hash = self._hash_token(token)
        token_record = (
            db.query(TokenRecord)
            .filter(
                TokenRecord.token_hash == token_hash,
                TokenRecord.status == TokenStatus.ACTIVE,
            )
            .first()
        )

        if not token_record:
            logger.warning(f"Token not found in records for user_id={user_id}")
            # 不强制要求 Token 记录存在，允许直接使用 JWT

        return user

    def verify_api_key(self, api_key: Optional[str] = None) -> bool:
        """
        验证 API Key（用于服务间认证）

        Args:
            api_key: API Key

        Returns:
            bool: API Key 是否有效
        """
        # TODO: 从数据库或配置中验证 API Key
        # 目前使用环境变量中的默认值
        expected_key = self.settings.auth.secret_key  # 临时使用 secret_key
        return api_key == expected_key if api_key else False

    def verify_enterprise_auth(
        self, signature: str, user_id: str, token: Optional[str] = None
    ) -> bool:
        """
        验证企业级认证签名

        Args:
            signature: 企业签名
            user_id: 用户 ID
            token: JWT token（可选）

        Returns:
            bool: 签名是否有效
        """
        return self.auth_service.verify_enterprise_signature(signature, user_id, token)

    def _hash_token(self, token: str) -> str:
        """
        对 Token 进行哈希（用于存储）

        Args:
            token: JWT token

        Returns:
            str: 哈希值
        """
        import hashlib

        return hashlib.sha256(token.encode()).hexdigest()


# 创建全局实例
auth_middleware = AuthMiddleware()
