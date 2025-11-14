"""
@purpose: 认证依赖注入
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.infrastructure.database import get_db
from src.models.database import User


async def get_current_user(
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前认证用户（依赖注入）

    Returns:
        User: 当前用户对象
    """
    # 这里需要从请求中提取 token，实际使用时应该通过中间件
    # 暂时返回 None，由路由处理
    pass


def get_auth_service():
    """
    获取认证服务实例（依赖注入）

    Returns:
        AuthService: 认证服务实例
    """
    return auth_middleware.auth_service
