#!/usr/bin/env python3
"""
@purpose: 初始化管理员用户脚本
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from src.infrastructure.database import SessionLocal
from src.models.database import User, UserRole
from src.core.services.auth_service import AuthService

auth_service = AuthService()


def create_admin_user(username: str = "admin", password: str = "admin", email: str = "admin@example.com"):
    """
    创建管理员用户

    Args:
        username: 用户名
        password: 密码
        email: 邮箱
    """
    db: Session = SessionLocal()
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"用户 {username} 已存在")
            return

        # 创建新用户
        hashed_password = auth_service.get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        print(f"管理员用户创建成功: {username}")
        print(f"  邮箱: {email}")
        print(f"  角色: {UserRole.ADMIN.value}")
        print(f"  密码: {password} (请登录后修改)")
    except Exception as e:
        db.rollback()
        print(f"创建用户失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="创建初始管理员用户")
    parser.add_argument("--username", default="admin", help="用户名")
    parser.add_argument("--password", default="admin", help="密码")
    parser.add_argument("--email", default="admin@example.com", help="邮箱")

    args = parser.parse_args()
    create_admin_user(args.username, args.password, args.email)

