"""
@purpose: MCP Server 安全中間件，負責 token 驗證、user_id 匹配驗證和企業級認證
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import hashlib
import hmac
import logging
from typing import Optional

from src.config.settings import get_settings
from src.core.services.token_service import TokenService

# 配置日誌
logger = logging.getLogger(__name__)


class AuthMiddleware:
    """MCP Server 安全中間件"""

    def __init__(self, token_service: TokenService):
        """
        初始化安全中間件
        
        Args:
            token_service: Token 服務實例
        """
        self.token_service = token_service
        self.settings = get_settings()
        self.enterprise_secret_key = self.settings.security.enterprise_secret_key
        self.enable_enterprise_auth = self.settings.security.enable_enterprise_auth

    def verify_request(
        self,
        token: Optional[str],
        user_id: str,
        enterprise_signature: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        驗證 MCP 請求（包含用戶級和企業級認證）
        
        驗證步驟：
        1. 企業級認證（如果啟用）：
           - 驗證企業 Secret Key 簽名
        2. 用戶級認證：
           - 檢查 token 是否存在
           - 驗證 token 有效性
           - 驗證 user_id 和 token 的綁定關係
        
        Args:
            token: JWT token（可選）
            user_id: 請求的用戶 ID
            enterprise_signature: 企業級簽名（HMAC-SHA256，可選）
            
        Returns:
            tuple[bool, Optional[str]]: (驗證是否通過, 錯誤消息)
        """
        # 步驟 1: 企業級認證（如果啟用）
        if self.enable_enterprise_auth:
            if not self.enterprise_secret_key:
                logger.error(
                    "企業級認證已啟用，但 ENTERPRISE_SECRET_KEY 未設置",
                    extra={"user_id": user_id},
                )
                return False, "企業級認證配置錯誤：ENTERPRISE_SECRET_KEY 未設置"

            if not enterprise_signature:
                logger.warning(
                    f"企業級認證已啟用，但缺少企業簽名 for user_id={user_id}",
                    extra={"user_id": user_id},
                )
                return False, "企業級認證失敗：缺少企業簽名"

            # 驗證企業簽名
            if not self._verify_enterprise_signature(
                enterprise_signature, user_id, token
            ):
                logger.warning(
                    f"企業級認證失敗 for user_id={user_id}, "
                    f"signature_prefix={enterprise_signature[:8] if enterprise_signature else 'N/A'}...",
                    extra={"user_id": user_id},
                )
                return False, "企業級認證失敗：簽名驗證失敗"

            logger.debug(
                f"企業級認證通過 for user_id={user_id}",
                extra={"user_id": user_id},
            )

        # 步驟 2: 用戶級認證
        # 檢查 token 是否存在
        if not token:
            logger.warning(
                f"Missing token for user_id={user_id}",
                extra={"user_id": user_id},
            )
            return False, "Token 缺失，請提供有效的 JWT token"

        # 驗證 token
        if not self.token_service.verify_token(token, user_id):
            logger.warning(
                f"Token verification failed for user_id={user_id}, "
                f"token_prefix={token[:8] if token else 'N/A'}...",
                extra={"user_id": user_id},
            )
            return False, "Token 驗證失敗，請檢查 token 是否有效且未過期"

        # 驗證通過
        logger.debug(
            f"Request verified successfully for user_id={user_id}",
            extra={"user_id": user_id},
        )
        return True, None

    def _verify_enterprise_signature(
        self, signature: str, user_id: str, token: Optional[str]
    ) -> bool:
        """
        驗證企業級簽名（HMAC-SHA256）
        
        簽名計算方式：
        HMAC-SHA256(ENTERPRISE_SECRET_KEY, user_id + token)
        
        Args:
            signature: 提供的簽名
            user_id: 用戶 ID
            token: JWT token（可選）
            
        Returns:
            bool: 簽名是否有效
        """
        if not self.enterprise_secret_key:
            return False

        # 構建簽名消息
        message = user_id
        if token:
            message += token

        # 計算期望的簽名
        expected_signature = hmac.new(
            self.enterprise_secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # 使用安全比較防止時間攻擊
        return hmac.compare_digest(expected_signature, signature)

    def generate_enterprise_signature(
        self, user_id: str, token: Optional[str] = None
    ) -> str:
        """
        生成企業級簽名（用於測試或客戶端實現參考）
        
        Args:
            user_id: 用戶 ID
            token: JWT token（可選）
            
        Returns:
            str: HMAC-SHA256 簽名
        """
        if not self.enterprise_secret_key:
            raise ValueError("ENTERPRISE_SECRET_KEY 未設置，無法生成簽名")

        message = user_id
        if token:
            message += token

        return hmac.new(
            self.enterprise_secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def extract_user_id_from_token(self, token: Optional[str]) -> Optional[str]:
        """
        從 token 中提取 user_id（用於驗證）
        
        Args:
            token: JWT token
            
        Returns:
            Optional[str]: user_id，如果提取失敗則返回 None
        """
        if not token:
            return None

        return self.token_service.extract_user_id(token)

