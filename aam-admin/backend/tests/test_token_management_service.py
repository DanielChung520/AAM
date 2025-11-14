"""
@purpose: Token 管理服务单元测试
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.core.services.token_management_service import TokenManagementService
from src.models.database import TokenRecord, TokenStatus, User, UserRole


class TestTokenManagementService:
    """Token 管理服务测试类"""

    def test_issue_token_with_user(self, db_session: Session, test_user: User):
        """测试发行绑定用户的 Token"""
        service = TokenManagementService(db_session)
        
        token_str, token_record = service.issue_token(
            user_id=test_user.id,
            name="Test Token",
            expires_hours=24,
        )
        
        assert token_str is not None
        assert token_record is not None
        assert token_record.user_id == test_user.id
        assert token_record.name == "Test Token"
        assert token_record.status == TokenStatus.ACTIVE
        assert token_record.expires_at is not None

    def test_issue_token_without_user(self, db_session: Session):
        """测试发行通用 Token（无用户绑定）"""
        service = TokenManagementService(db_session)
        
        token_str, token_record = service.issue_token(
            name="Generic Token",
            expires_hours=48,
        )
        
        assert token_str is not None
        assert token_record is not None
        assert token_record.user_id is None
        assert token_record.name == "Generic Token"
        assert token_record.status == TokenStatus.ACTIVE

    def test_issue_token_invalid_user(self, db_session: Session):
        """测试发行 Token 时用户不存在的情况"""
        service = TokenManagementService(db_session)
        
        with pytest.raises(ValueError, match="用户 ID.*不存在"):
            service.issue_token(user_id=99999, name="Invalid User Token")

    def test_revoke_token(self, db_session: Session, test_user: User):
        """测试撤销 Token"""
        service = TokenManagementService(db_session)
        
        # 先发行一个 Token
        _, token_record = service.issue_token(
            user_id=test_user.id,
            name="Token to Revoke",
        )
        
        # 撤销 Token
        revoked_token = service.revoke_token(
            token_record.id,
            reason="Test revocation",
        )
        
        assert revoked_token.status == TokenStatus.REVOKED
        assert revoked_token.revoked_at is not None
        assert revoked_token.extra_data["revoke_reason"] == "Test revocation"

    def test_revoke_token_already_revoked(self, db_session: Session, test_user: User):
        """测试撤销已撤销的 Token"""
        service = TokenManagementService(db_session)
        
        # 先发行并撤销一个 Token
        _, token_record = service.issue_token(
            user_id=test_user.id,
            name="Token to Revoke",
        )
        service.revoke_token(token_record.id)
        
        # 再次撤销应该失败
        with pytest.raises(ValueError, match="已被撤销"):
            service.revoke_token(token_record.id)

    def test_revoke_token_not_found(self, db_session: Session):
        """测试撤销不存在的 Token"""
        service = TokenManagementService(db_session)
        
        with pytest.raises(ValueError, match="不存在"):
            service.revoke_token(99999)

    def test_get_token(self, db_session: Session, test_user: User):
        """测试获取 Token 详情"""
        service = TokenManagementService(db_session)
        
        # 先发行一个 Token
        _, token_record = service.issue_token(
            user_id=test_user.id,
            name="Test Token",
        )
        
        # 获取 Token
        retrieved_token = service.get_token(token_record.id)
        
        assert retrieved_token is not None
        assert retrieved_token.id == token_record.id
        assert retrieved_token.user_id == test_user.id

    def test_get_token_not_found(self, db_session: Session):
        """测试获取不存在的 Token"""
        service = TokenManagementService(db_session)
        
        token = service.get_token(99999)
        assert token is None

    def test_list_tokens(self, db_session: Session, test_user: User):
        """测试列出 Token"""
        service = TokenManagementService(db_session)
        
        # 发行多个 Token
        service.issue_token(user_id=test_user.id, name="Token 1")
        service.issue_token(user_id=test_user.id, name="Token 2")
        service.issue_token(name="Generic Token")
        
        # 列出所有 Token
        tokens, total = service.list_tokens()
        
        assert len(tokens) == 3
        assert total == 3

    def test_list_tokens_with_filter(self, db_session: Session, test_user: User):
        """测试使用过滤条件列出 Token"""
        service = TokenManagementService(db_session)
        
        # 发行多个 Token
        service.issue_token(user_id=test_user.id, name="User Token")
        service.issue_token(name="Generic Token")
        
        # 按用户 ID 过滤
        tokens, total = service.list_tokens(user_id=test_user.id)
        
        assert len(tokens) == 1
        assert total == 1
        assert tokens[0].user_id == test_user.id

    def test_list_tokens_with_status_filter(self, db_session: Session, test_user: User):
        """测试按状态过滤 Token"""
        service = TokenManagementService(db_session)
        
        # 发行并撤销一个 Token
        _, token_record = service.issue_token(
            user_id=test_user.id,
            name="Token to Revoke",
        )
        service.revoke_token(token_record.id)
        
        # 发行另一个活跃的 Token
        service.issue_token(user_id=test_user.id, name="Active Token")
        
        # 列出活跃的 Token
        active_tokens, active_total = service.list_tokens(status=TokenStatus.ACTIVE)
        assert active_total == 1
        
        # 列出已撤销的 Token
        revoked_tokens, revoked_total = service.list_tokens(status=TokenStatus.REVOKED)
        assert revoked_total == 1

    def test_update_token_last_used(self, db_session: Session, test_user: User):
        """测试更新 Token 最后使用时间"""
        service = TokenManagementService(db_session)
        
        # 发行一个 Token
        _, token_record = service.issue_token(
            user_id=test_user.id,
            name="Test Token",
        )
        
        import hashlib
        token_hash = hashlib.sha256("test_token".encode()).hexdigest()
        
        # 更新 Token 记录哈希（用于测试）
        token_record.token_hash = token_hash
        db_session.commit()
        
        # 更新最后使用时间
        service.update_token_last_used(token_hash)
        
        db_session.refresh(token_record)
        assert token_record.last_used_at is not None

