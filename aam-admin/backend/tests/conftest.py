"""
@purpose: pytest 配置文件，提供测试用的 fixtures
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import pytest
from datetime import datetime
from typing import Generator
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from src.main import app
from src.infrastructure.database import get_db, Base
from src.models.database import User, UserRole, TokenRecord, TokenStatus, AuditLog, AuditAction


# 测试数据库 URL（使用内存数据库）
TEST_DATABASE_URL = "sqlite:///:memory:"

# 创建测试数据库引擎
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    创建测试数据库会话

    Yields:
        Session: 数据库会话
    """
    # 创建表
    Base.metadata.create_all(bind=test_engine)
    
    # 创建会话
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    创建测试客户端

    Args:
        db_session: 数据库会话

    Yields:
        TestClient: FastAPI 测试客户端
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    创建测试用户

    Args:
        db_session: 数据库会话

    Returns:
        User: 测试用户对象
    """
    from src.core.services.auth_service import AuthService
    
    auth_service = AuthService()
    hashed_password = auth_service.get_password_hash("test_password")
    
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_token(db_session: Session, test_user: User) -> str:
    """
    创建测试 Token

    Args:
        db_session: 数据库会话
        test_user: 测试用户

    Returns:
        str: JWT Token 字符串
    """
    from src.core.services.auth_service import AuthService
    
    auth_service = AuthService()
    token = auth_service.create_access_token(
        user_id=test_user.id,
        username=test_user.username,
        role=test_user.role.value,
    )
    
    # 保存 Token 记录
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    token_record = TokenRecord(
        token_hash=token_hash,
        user_id=test_user.id,
        name="Test Token",
        status=TokenStatus.ACTIVE,
        issued_at=datetime.utcnow(),
    )
    db_session.add(token_record)
    db_session.commit()
    
    return token


@pytest.fixture
def authenticated_client(client: TestClient, test_token: str, test_user: User, db_session: Session) -> TestClient:
    """
    创建已认证的测试客户端

    Args:
        client: 测试客户端
        test_token: 测试 Token
        test_user: 测试用户
        db_session: 数据库会话

    Returns:
        TestClient: 已认证的测试客户端
    """
    from src.api.middleware.auth_middleware import auth_middleware
    from unittest.mock import AsyncMock
    
    # Mock get_current_user 方法
    async def mock_get_current_user(
        credentials=None,
        db=None,
    ) -> User:
        return test_user
    
    # 覆盖依赖注入
    app.dependency_overrides[auth_middleware.get_current_user] = mock_get_current_user
    
    client.headers.update({"Authorization": f"Bearer {test_token}"})
    
    yield client
    
    # 清理依赖覆盖
    if auth_middleware.get_current_user in app.dependency_overrides:
        del app.dependency_overrides[auth_middleware.get_current_user]


@pytest.fixture
def mock_docker_client():
    """
    创建模拟的 Docker 客户端

    Returns:
        Mock: 模拟的 Docker 客户端
    """
    mock_client = Mock()
    
    # 模拟容器列表
    mock_container = Mock()
    mock_container.id = "test_container_id"
    mock_container.name = "test_container"
    mock_container.status = "running"
    mock_container.image = Mock()
    mock_container.image.tags = ["test_image:latest"]
    mock_container.attrs = {
        "State": {"Status": "running"},
        "Config": {"Image": "test_image:latest"},
    }
    
    mock_client.containers.list.return_value = [mock_container]
    mock_client.containers.get.return_value = mock_container
    
    # 模拟容器统计
    mock_stats = {
        "cpu_stats": {"cpu_usage": {"total_usage": 1000000000}},
        "memory_stats": {"usage": 512 * 1024 * 1024, "limit": 1024 * 1024 * 1024},
    }
    mock_container.stats.return_value = mock_stats
    
    return mock_client

