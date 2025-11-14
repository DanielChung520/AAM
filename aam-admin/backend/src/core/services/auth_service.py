"""
@purpose: 认证服务，负责 JWT Token 的发行、验证和用户认证
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self):
        """初始化认证服务"""
        self.settings = get_settings()
        self.secret_key = self.settings.auth.secret_key
        self.algorithm = self.settings.auth.algorithm
        self.access_token_expire_minutes = self.settings.auth.access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.auth.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码

        Returns:
            bool: 密码是否正确
        """
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        if isinstance(plain_password, str):
            plain_password = plain_password.encode("utf-8")
        return bcrypt.checkpw(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        生成密码哈希

        Args:
            password: 明文密码

        Returns:
            str: 哈希密码
        """
        # 确保密码是字节类型且不超过 72 字节（bcrypt 限制）
        if isinstance(password, str):
            password_bytes = password.encode("utf-8")
        else:
            password_bytes = password

        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # 生成 salt 并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def create_access_token(self, user_id: int, username: str, role: str) -> str:
        """
        创建访问令牌

        Args:
            user_id: 用户 ID
            username: 用户名
            role: 用户角色

        Returns:
            str: JWT 访问令牌
        """
        now = datetime.utcnow()
        expire_time = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": str(user_id),  # subject (用户 ID)
            "username": username,
            "role": role,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire_time.timestamp()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Access token created for user_id={user_id}, username={username}")
        return token

    def create_refresh_token(self, user_id: int) -> str:
        """
        创建刷新令牌

        Args:
            user_id: 用户 ID

        Returns:
            str: JWT 刷新令牌
        """
        now = datetime.utcnow()
        expire_time = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire_time.timestamp()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Refresh token created for user_id={user_id}")
        return token

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """
        验证令牌

        Args:
            token: JWT 令牌
            token_type: 令牌类型 ("access" 或 "refresh")

        Returns:
            Optional[dict]: 解码后的 payload，如果验证失败返回 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 验证令牌类型
            if payload.get("type") != token_type:
                logger.warning(
                    f"Token type mismatch: expected {token_type}, got {payload.get('type')}"
                )
                return None

            return payload
        except ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except InvalidSignatureError:
            logger.warning("Invalid token signature")
            return None
        except DecodeError:
            logger.warning("Token decode error")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def generate_enterprise_signature(self, user_id: str, token: Optional[str] = None) -> str:
        """
        生成企业级签名（HMAC-SHA256）

        Args:
            user_id: 用户 ID
            token: JWT token（可选）

        Returns:
            str: HMAC-SHA256 签名
        """
        # 使用 secret_key 作为企业密钥
        secret = self.secret_key.encode("utf-8")
        message = user_id
        if token:
            message += token

        signature = hmac.new(secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        return signature

    def verify_enterprise_signature(
        self, signature: str, user_id: str, token: Optional[str] = None
    ) -> bool:
        """
        验证企业级签名

        Args:
            signature: 提供的签名
            user_id: 用户 ID
            token: JWT token（可选）

        Returns:
            bool: 签名是否有效
        """
        expected_signature = self.generate_enterprise_signature(user_id, token)
        return hmac.compare_digest(expected_signature, signature)
