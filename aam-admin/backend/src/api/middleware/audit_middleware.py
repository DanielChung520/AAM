"""
@purpose: 审计中间件，拦截所有管理操作请求并记录审计日志
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from src.core.services.audit_service import AuditService
from src.models.database import AuditAction, AuditLog
from src.infrastructure.database import get_db

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件类"""

    # 需要审计的路由前缀
    AUDIT_PREFIXES = ["/api/v1/admin"]

    # 操作类型映射（HTTP 方法 + 路径模式 -> 操作类型）
    ACTION_MAPPING: Dict[str, AuditAction] = {
        ("POST", "/services"): AuditAction.CREATE,
        ("PUT", "/services"): AuditAction.UPDATE,
        ("PATCH", "/services"): AuditAction.UPDATE,
        ("DELETE", "/services"): AuditAction.DELETE,
        ("POST", "/services/.*/start"): AuditAction.START_SERVICE,
        ("POST", "/services/.*/stop"): AuditAction.STOP_SERVICE,
        ("POST", "/services/.*/restart"): AuditAction.RESTART_SERVICE,
        ("POST", "/llm-providers"): AuditAction.CREATE,
        ("PUT", "/llm-providers"): AuditAction.UPDATE,
        ("DELETE", "/llm-providers"): AuditAction.DELETE,
        ("POST", "/versions"): AuditAction.CREATE,
        ("POST", "/versions/.*/deploy"): AuditAction.DEPLOY,
        ("POST", "/versions/.*/rollback"): AuditAction.ROLLBACK,
        ("POST", "/security/tokens/issue"): AuditAction.CREATE,
        ("POST", "/security/tokens/.*/revoke"): AuditAction.DELETE,
        ("PUT", "/security/enterprise-auth"): AuditAction.UPDATE,
        ("PUT", "/settings"): AuditAction.UPDATE,
        ("POST", "/settings/backup"): AuditAction.CREATE,
        ("POST", "/settings/restore"): AuditAction.UPDATE,
    }

    # 资源类型映射（路径模式 -> 资源类型）
    RESOURCE_TYPE_MAPPING: Dict[str, str] = {
        "/services": "service",
        "/llm-providers": "llm_provider",
        "/versions": "deployment",
        "/security/tokens": "token",
        "/security/enterprise-auth": "config",
        "/settings": "settings",
    }

    def __init__(self, app: ASGIApp):
        """
        初始化审计中间件

        Args:
            app: ASGI 应用
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录审计日志

        Args:
            request: FastAPI 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            Response: HTTP 响应
        """
        # 检查是否需要审计
        if not self._should_audit(request):
            return await call_next(request)

        # 获取数据库会话（从请求状态中获取，如果已注入）
        db: Optional[Session] = request.state.get("db")
        if not db:
            # 如果没有数据库会话，创建一个临时会话
            # 注意：这需要确保数据库连接可用
            try:
                db_gen = get_db()
                db = next(db_gen)
            except Exception as e:
                logger.error(f"Failed to get database session for audit: {e}")
                return await call_next(request)

        # 获取用户信息（从请求状态中获取，如果已注入）
        user = request.state.get("current_user")

        # 提取请求信息
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # 识别操作类型和资源类型
        action = self._identify_action(method, path)
        resource_type = self._identify_resource_type(path)
        resource_id = self._extract_resource_id(path)

        # 读取请求体（用于记录请求数据）
        request_data = None
        try:
            if method in ("POST", "PUT", "PATCH"):
                body = await request.body()
                if body:
                    import json
                    try:
                        request_data = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_data = {"raw": body.decode(errors="ignore")[:500]}
        except Exception as e:
            logger.warning(f"Failed to read request body for audit: {e}")

        # 记录操作前状态（对于更新操作，需要先获取当前状态）
        before_state = None
        if action in (AuditAction.UPDATE, AuditAction.DELETE) and resource_id:
            try:
                before_state = self._get_resource_state(db, resource_type, resource_id)
            except Exception as e:
                logger.warning(f"Failed to get before state for audit: {e}")

        # 执行请求
        response = await call_next(request)

        # 记录操作后状态（仅在成功时）
        after_state = None
        if action == AuditAction.UPDATE and resource_id and response.status_code < 400:
            try:
                after_state = self._get_resource_state(db, resource_type, resource_id)
            except Exception as e:
                logger.warning(f"Failed to get after state for audit: {e}")

        # 记录审计日志（异步执行，不阻塞响应）
        try:
            audit_service = AuditService(db)
            audit_service.log_operation(
                user_id=user.id if user else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=f"{method} {path}",
                ip_address=ip_address,
                user_agent=user_agent,
                request_data=request_data,
                response_data=None,  # 不记录响应数据，避免复杂性
                status="success" if response.status_code < 400 else "failed",
                error_message=None if response.status_code < 400 else f"HTTP {response.status_code}",
                before_state=before_state,
                after_state=after_state,
            )
        except Exception as e:
            logger.error(f"Failed to log audit: {e}", exc_info=True)

        return response

    def _should_audit(self, request: Request) -> bool:
        """
        判断是否需要审计

        Args:
            request: FastAPI 请求对象

        Returns:
            bool: 是否需要审计
        """
        path = request.url.path
        method = request.method

        # 只审计管理 API 的写操作
        if not any(path.startswith(prefix) for prefix in self.AUDIT_PREFIXES):
            return False

        # 只审计写操作（POST, PUT, PATCH, DELETE）
        if method not in ("POST", "PUT", "PATCH", "DELETE"):
            return False

        # 排除某些不需要审计的端点
        excluded_paths = [
            "/api/v1/admin/auth/login",
            "/api/v1/admin/audit-logs",  # 审计日志查询本身不需要审计
        ]
        if any(path.startswith(excluded) for excluded in excluded_paths):
            return False

        return True

    def _identify_action(self, method: str, path: str) -> AuditAction:
        """
        识别操作类型

        Args:
            method: HTTP 方法
            path: 请求路径

        Returns:
            AuditAction: 操作类型
        """
        import re

        # 移除 API 前缀
        for prefix in self.AUDIT_PREFIXES:
            if path.startswith(prefix):
                path = path[len(prefix) :]
                break

        # 查找匹配的操作类型
        for (m, pattern), action in self.ACTION_MAPPING.items():
            if m == method:
                if re.match(pattern, path):
                    return action

        # 默认映射
        if method == "POST":
            return AuditAction.CREATE
        elif method in ("PUT", "PATCH"):
            return AuditAction.UPDATE
        elif method == "DELETE":
            return AuditAction.DELETE
        else:
            return AuditAction.UPDATE  # 默认

    def _identify_resource_type(self, path: str) -> str:
        """
        识别资源类型

        Args:
            path: 请求路径

        Returns:
            str: 资源类型
        """
        # 移除 API 前缀
        for prefix in self.AUDIT_PREFIXES:
            if path.startswith(prefix):
                path = path[len(prefix) :]
                break

        # 查找匹配的资源类型
        for pattern, resource_type in self.RESOURCE_TYPE_MAPPING.items():
            if path.startswith(pattern):
                return resource_type

        return "unknown"

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """
        从路径中提取资源 ID

        Args:
            path: 请求路径

        Returns:
            Optional[str]: 资源 ID
        """
        import re

        # 移除 API 前缀
        for prefix in self.AUDIT_PREFIXES:
            if path.startswith(prefix):
                path = path[len(prefix) :]
                break

        # 尝试匹配常见的资源 ID 模式
        patterns = [
            r"/(\d+)",  # 数字 ID
            r"/([a-f0-9-]{36})",  # UUID
            r"/([^/]+)/",  # 任意字符串 ID
        ]

        for pattern in patterns:
            match = re.search(pattern, path)
            if match:
                return match.group(1)

        return None

    def _get_resource_state(
        self, db: Session, resource_type: str, resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取资源当前状态（用于记录操作前后对比）

        Args:
            db: 数据库会话
            resource_type: 资源类型
            resource_id: 资源 ID

        Returns:
            Optional[Dict[str, Any]]: 资源状态字典
        """
        # 这里简化处理，实际应该根据资源类型查询对应的数据库表
        # 目前只返回资源 ID 和类型
        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

