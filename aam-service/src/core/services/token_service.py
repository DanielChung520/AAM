"""
@purpose: JWT Token 服務，負責 token 的發行、驗證和 user_id 提取
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError

from src.config.settings import get_settings

# 配置日誌
logger = logging.getLogger(__name__)


class TokenService:
    """JWT Token 服務類"""

    def __init__(self):
        """初始化 Token 服務"""
        self.settings = get_settings()
        self.secret_key = self.settings.security.secret_key
        self.algorithm = self.settings.security.algorithm
        self.token_expire_hours = self.settings.security.token_expire_hours
        self.token_issuer = self.settings.security.token_issuer
        self.enable_user_id_validation = (
            self.settings.security.enable_user_id_validation
        )

    def issue_token(self, user_id: str) -> str:
        """
        發行 JWT token
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            JWT token 字符串
            
        Raises:
            ValueError: 當 user_id 為空時
        """
        if not user_id:
            raise ValueError("user_id 不能為空")

        # 計算過期時間
        now = datetime.utcnow()
        expire_time = now + timedelta(hours=self.token_expire_hours)

        # 構建 payload
        payload = {
            "user_id": user_id,
            "iss": self.token_issuer,
            "iat": int(now.timestamp()),
            "exp": int(expire_time.timestamp()),
        }

        # 簽名並生成 token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        # 記錄 token 發行事件（只記錄前 8 位，不記錄完整 token）
        logger.info(
            f"Token issued for user_id={user_id}, "
            f"token_prefix={token[:8]}..., "
            f"expires_at={expire_time.isoformat()}"
        )

        return token

    def verify_token(self, token: str, user_id: str) -> bool:
        """
        驗證 JWT token
        
        驗證步驟：
        1. Token 格式有效
        2. Token 未過期
        3. Token 簽名正確（AAM 發行）
        4. Token 中的 user_id 與請求的 user_id 匹配
        
        Args:
            token: JWT token 字符串
            user_id: 請求的用戶 ID
            
        Returns:
            bool: 驗證是否通過
            
        Raises:
            ValueError: 當 token 或 user_id 為空時
        """
        if not token:
            raise ValueError("token 不能為空")
        if not user_id:
            raise ValueError("user_id 不能為空")

        try:
            # 解碼並驗證 token
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            # 驗證發行者
            if payload.get("iss") != self.token_issuer:
                logger.warning(
                    f"Token issuer mismatch: expected={self.token_issuer}, "
                    f"got={payload.get('iss')}, token_prefix={token[:8]}..."
                )
                return False

            # 驗證 user_id 匹配（如果啟用驗證）
            if self.enable_user_id_validation:
                token_user_id = payload.get("user_id")
                if token_user_id != user_id:
                    logger.warning(
                        f"User ID mismatch: expected={user_id}, "
                        f"got={token_user_id}, token_prefix={token[:8]}..."
                    )
                    return False

            # 驗證通過
            logger.debug(
                f"Token verified successfully for user_id={user_id}, "
                f"token_prefix={token[:8]}..."
            )
            return True

        except ExpiredSignatureError:
            logger.warning(
                f"Token expired for user_id={user_id}, "
                f"token_prefix={token[:8]}..."
            )
            return False

        except InvalidSignatureError:
            logger.warning(
                f"Invalid token signature for user_id={user_id}, "
                f"token_prefix={token[:8]}..."
            )
            return False

        except DecodeError as e:
            logger.warning(
                f"Token decode error for user_id={user_id}, "
                f"token_prefix={token[:8]}..., error={str(e)}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Unexpected error during token verification: {e}",
                exc_info=e,
                extra={"user_id": user_id, "token_prefix": token[:8] + "..."},
            )
            return False

    def extract_user_id(self, token: str) -> Optional[str]:
        """
        從 token 中提取 user_id（不驗證簽名，僅用於提取）
        
        注意：此方法不驗證 token 的有效性，僅用於提取信息。
        實際驗證應使用 verify_token 方法。
        
        Args:
            token: JWT token 字符串
            
        Returns:
            Optional[str]: user_id，如果提取失敗則返回 None
        """
        if not token:
            return None

        try:
            # 不解碼簽名，僅解碼 payload（用於提取信息）
            payload = jwt.decode(
                token, options={"verify_signature": False}
            )
            return payload.get("user_id")

        except Exception as e:
            logger.warning(
                f"Failed to extract user_id from token: {e}",
                exc_info=e,
                extra={"token_prefix": token[:8] + "..." if token else "N/A"},
            )
            return None

