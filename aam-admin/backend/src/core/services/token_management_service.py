"""
@purpose: Token 管理服务，负责 Token 的发行、撤销和查询
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.core.services.auth_service import AuthService
from src.models.database import TokenRecord, TokenStatus, User

logger = logging.getLogger(__name__)


class TokenManagementService:
    """Token 管理服务类"""

    def __init__(self, db: Session):
        """
        初始化 Token 管理服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.auth_service = AuthService()

    def issue_token(
        self,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        expires_hours: Optional[int] = 24,
        extra_data: Optional[dict] = None,
    ) -> tuple[str, TokenRecord]:
        """
        发行 Token

        Args:
            user_id: 用户 ID（可选）
            name: Token 名称/描述
            expires_hours: Token 有效期（小时）
            extra_data: 额外数据

        Returns:
            tuple[str, TokenRecord]: (Token 字符串, Token 记录)

        Raises:
            ValueError: 当用户不存在时
        """
        # 如果提供了 user_id，验证用户存在
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"用户 ID {user_id} 不存在")

        # 创建 Token
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            token_str = self.auth_service.create_access_token(
                user_id=user_id, username=user.username, role=user.role.value
            )
        else:
            # 创建通用 Token（使用系统用户 ID 0）
            token_str = self.auth_service.create_access_token(
                user_id=0, username="system", role="admin"
            )

        # 计算 Token 哈希
        token_hash = hashlib.sha256(token_str.encode()).hexdigest()

        # 计算过期时间
        expires_at = None
        if expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        # 创建 Token 记录
        token_record = TokenRecord(
            token_hash=token_hash,
            user_id=user_id,
            name=name or "Manual Token",
            status=TokenStatus.ACTIVE,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
            extra_data=extra_data,
        )

        self.db.add(token_record)
        self.db.commit()
        self.db.refresh(token_record)

        logger.info(f"Token issued: id={token_record.id}, user_id={user_id}, name={name}")

        return token_str, token_record

    def revoke_token(self, token_id: int, reason: Optional[str] = None) -> TokenRecord:
        """
        撤销 Token

        Args:
            token_id: Token ID
            reason: 撤销原因

        Returns:
            TokenRecord: 更新后的 Token 记录

        Raises:
            ValueError: 当 Token 不存在或已撤销时
        """
        token_record = self.db.query(TokenRecord).filter(TokenRecord.id == token_id).first()

        if not token_record:
            raise ValueError(f"Token ID {token_id} 不存在")

        if token_record.status == TokenStatus.REVOKED:
            raise ValueError(f"Token ID {token_id} 已被撤销")

        # 更新状态
        token_record.status = TokenStatus.REVOKED
        token_record.revoked_at = datetime.utcnow()

        # 更新额外数据（添加撤销原因）
        if reason:
            if token_record.extra_data is None:
                token_record.extra_data = {}
            token_record.extra_data["revoke_reason"] = reason

        self.db.commit()
        self.db.refresh(token_record)

        logger.info(f"Token revoked: id={token_id}, reason={reason}")

        return token_record

    def get_token(self, token_id: int) -> Optional[TokenRecord]:
        """
        获取 Token 记录

        Args:
            token_id: Token ID

        Returns:
            Optional[TokenRecord]: Token 记录，如果不存在返回 None
        """
        return self.db.query(TokenRecord).filter(TokenRecord.id == token_id).first()

    def list_tokens(
        self,
        user_id: Optional[int] = None,
        status: Optional[TokenStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[TokenRecord], int]:
        """
        列出 Token 记录

        Args:
            user_id: 用户 ID（可选，用于过滤）
            status: Token 状态（可选，用于过滤）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            tuple[list[TokenRecord], int]: (Token 记录列表, 总数)
        """
        query = self.db.query(TokenRecord)

        # 应用过滤条件
        if user_id is not None:
            query = query.filter(TokenRecord.user_id == user_id)

        if status:
            query = query.filter(TokenRecord.status == status)

        # 获取总数
        total = query.count()

        # 应用排序和分页
        tokens = query.order_by(desc(TokenRecord.issued_at)).offset(offset).limit(limit).all()

        return tokens, total

    def update_token_last_used(self, token_hash: str) -> None:
        """
        更新 Token 最后使用时间

        Args:
            token_hash: Token 哈希
        """
        token_record = (
            self.db.query(TokenRecord)
            .filter(TokenRecord.token_hash == token_hash)
            .first()
        )

        if token_record:
            token_record.last_used_at = datetime.utcnow()
            self.db.commit()

