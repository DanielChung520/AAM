"""
@purpose: 审计系统路由，提供审计日志查询、统计、导出等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.audit_service import AuditService
from src.infrastructure.database import get_db
from src.models.database import User, AuditAction
from src.models.schemas.audit import (
    AuditLogResponse,
    AuditLogListResponse,
    AuditLogQueryRequest,
    AuditLogStatsResponse,
    AuditLogTrendResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audit-logs", tags=["审计日志"])


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """
    获取审计服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        AuditService: 审计服务实例
    """
    return AuditService(db=db)


@router.get("", response_model=AuditLogListResponse, status_code=status.HTTP_200_OK)
async def list_audit_logs(
    user_id: Optional[int] = Query(None, description="用户 ID（可选）"),
    action: Optional[str] = Query(None, description="操作类型（可选）"),
    resource_type: Optional[str] = Query(None, description="资源类型（可选）"),
    resource_id: Optional[str] = Query(None, description="资源 ID（可选）"),
    status: Optional[str] = Query(None, description="操作状态（success/failed）"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序（asc/desc）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    获取审计日志列表

    Args:
        user_id: 用户 ID（可选）
        action: 操作类型（可选）
        resource_type: 资源类型（可选）
        resource_id: 资源 ID（可选）
        status: 操作状态（可选）
        start_time: 开始时间（ISO 格式，可选）
        end_time: 结束时间（ISO 格式，可选）
        keyword: 关键词搜索（可选）
        page: 页码
        page_size: 每页数量
        sort_by: 排序字段
        sort_order: 排序顺序
        current_user: 当前认证用户
        audit_service: 审计服务

    Returns:
        AuditLogListResponse: 审计日志列表响应
    """
    try:
        # 解析操作类型
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的操作类型: {action}",
                )

        # 解析时间
        start_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的开始时间格式: {start_time}",
                )

        end_dt = None
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的结束时间格式: {end_time}",
                )

        # 查询日志
        logs, total = audit_service.query_logs(
            user_id=user_id,
            action=action_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            start_time=start_dt,
            end_time=end_dt,
            keyword=keyword,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # 转换为响应格式
        log_responses = []
        for log in logs:
            # 获取用户名
            username = None
            if log.user_id:
                user = audit_service.db.query(User).filter(User.id == log.user_id).first()
                if user:
                    username = user.username

            # 提取操作前后状态（从 request_data 中）
            before_state = None
            after_state = None
            if log.request_data and isinstance(log.request_data, dict):
                before_state = log.request_data.get("before_state")
                after_state = log.request_data.get("after_state")

            log_responses.append(
                AuditLogResponse(
                    id=log.id,
                    user_id=log.user_id,
                    username=username,
                    action=log.action.value,
                    resource_type=log.resource_type,
                    resource_id=log.resource_id,
                    description=log.description,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    request_data=log.request_data,
                    response_data=log.response_data,
                    before_state=before_state,
                    after_state=after_state,
                    status=log.status,
                    error_message=log.error_message,
                    created_at=log.created_at,
                )
            )

        return AuditLogListResponse(
            items=log_responses,
            total=total,
            page=page,
            page_size=page_size,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing audit logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志列表失败",
        )


@router.get("/{log_id}", response_model=AuditLogResponse, status_code=status.HTTP_200_OK)
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(auth_middleware.get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    获取审计日志详情

    Args:
        log_id: 审计日志 ID
        current_user: 当前认证用户
        audit_service: 审计服务

    Returns:
        AuditLogResponse: 审计日志详情
    """
    try:
        log = audit_service.get_log(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"审计日志 ID {log_id} 不存在",
            )

        # 获取用户名
        username = None
        if log.user_id:
            user = audit_service.db.query(User).filter(User.id == log.user_id).first()
            if user:
                username = user.username

        # 提取操作前后状态
        before_state = None
        after_state = None
        if log.request_data and isinstance(log.request_data, dict):
            before_state = log.request_data.get("before_state")
            after_state = log.request_data.get("after_state")

        return AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=username,
            action=log.action.value,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            request_data=log.request_data,
            response_data=log.response_data,
            before_state=before_state,
            after_state=after_state,
            status=log.status,
            error_message=log.error_message,
            created_at=log.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志详情失败",
        )


@router.get("/export", status_code=status.HTTP_200_OK)
async def export_audit_logs(
    format: str = Query("csv", description="导出格式（csv/json）"),
    user_id: Optional[int] = Query(None, description="用户 ID（可选）"),
    action: Optional[str] = Query(None, description="操作类型（可选）"),
    resource_type: Optional[str] = Query(None, description="资源类型（可选）"),
    status: Optional[str] = Query(None, description="操作状态（可选）"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    导出审计日志

    Args:
        format: 导出格式（csv/json）
        user_id: 用户 ID（可选）
        action: 操作类型（可选）
        resource_type: 资源类型（可选）
        status: 操作状态（可选）
        start_time: 开始时间（ISO 格式，可选）
        end_time: 结束时间（ISO 格式，可选）
        current_user: 当前认证用户
        audit_service: 审计服务

    Returns:
        Response: 导出的文件（CSV 或 JSON）
    """
    try:
        # 解析操作类型
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的操作类型: {action}",
                )

        # 解析时间
        start_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的开始时间格式: {start_time}",
                )

        end_dt = None
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的结束时间格式: {end_time}",
                )

        # 导出日志
        exported_data = audit_service.export_logs(
            format=format,
            user_id=user_id,
            action=action_enum,
            resource_type=resource_type,
            status=status,
            start_time=start_dt,
            end_time=end_dt,
        )

        # 设置响应头
        content_type = "text/csv" if format.lower() == "csv" else "application/json"
        filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"

        return Response(
            content=exported_data,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导出审计日志失败",
        )


@router.get("/stats", response_model=AuditLogStatsResponse, status_code=status.HTTP_200_OK)
async def get_audit_stats(
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    获取审计统计信息

    Args:
        start_time: 开始时间（ISO 格式，可选）
        end_time: 结束时间（ISO 格式，可选）
        current_user: 当前认证用户
        audit_service: 审计服务

    Returns:
        AuditLogStatsResponse: 审计统计响应
    """
    try:
        # 解析时间
        start_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的开始时间格式: {start_time}",
                )

        end_dt = None
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的结束时间格式: {end_time}",
                )

        # 获取统计信息
        stats = audit_service.get_stats(start_time=start_dt, end_time=end_dt)

        return AuditLogStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计统计信息失败",
        )


@router.get("/trends", response_model=AuditLogTrendResponse, status_code=status.HTTP_200_OK)
async def get_audit_trends(
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    group_by: str = Query("day", description="分组方式（hour/day/week/month）"),
    action: Optional[str] = Query(None, description="操作类型（可选）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    获取操作趋势数据

    Args:
        start_time: 开始时间（ISO 格式，可选）
        end_time: 结束时间（ISO 格式，可选）
        group_by: 分组方式（hour/day/week/month）
        action: 操作类型（可选）
        current_user: 当前认证用户
        audit_service: 审计服务

    Returns:
        AuditLogTrendResponse: 审计趋势响应
    """
    try:
        # 验证分组方式
        if group_by not in ("hour", "day", "week", "month"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的分组方式: {group_by}，支持: hour/day/week/month",
            )

        # 解析操作类型
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的操作类型: {action}",
                )

        # 解析时间
        start_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的开始时间格式: {start_time}",
                )

        end_dt = None
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的结束时间格式: {end_time}",
                )

        # 获取趋势数据
        trends = audit_service.get_trends(
            start_time=start_dt,
            end_time=end_dt,
            group_by=group_by,
            action=action_enum,
        )

        return AuditLogTrendResponse(trends=trends, group_by=group_by)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取操作趋势数据失败",
        )

