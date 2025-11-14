"""
@purpose: 日志管理路由，提供日志搜索、导出等 API
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
from src.core.services.docker_service import DockerService
from src.core.services.log_service import LogService
from src.infrastructure.database import get_db
from src.models.database import User
from src.models.schemas.logs import LogEntry, LogExportRequest, LogSearchRequest, LogSearchResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/logs", tags=["日志管理"])


def get_log_service() -> LogService:
    """
    获取日志服务实例（依赖注入）

    Returns:
        LogService: 日志服务实例
    """
    docker_service = DockerService()
    return LogService(docker_service=docker_service)


@router.post("/search", response_model=LogSearchResponse, status_code=status.HTTP_200_OK)
async def search_logs(
    request: LogSearchRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    log_service: LogService = Depends(get_log_service),
):
    """
    搜索日志

    Args:
        request: 搜索请求
        current_user: 当前认证用户
        log_service: 日志服务

    Returns:
        LogSearchResponse: 搜索结果
    """
    try:
        logs, total = log_service.search_logs(
            service=request.service,
            level=request.level,
            start_time=request.start_time,
            end_time=request.end_time,
            keyword=request.keyword,
            page=request.page,
            page_size=request.page_size,
        )

        total_pages = (total + request.page_size - 1) // request.page_size

        return LogSearchResponse(
            items=[LogEntry(**log) for log in logs],
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error searching logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索日志失败",
        )


@router.post("/export", status_code=status.HTTP_200_OK)
async def export_logs(
    request: LogExportRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    log_service: LogService = Depends(get_log_service),
):
    """
    导出日志

    Args:
        request: 导出请求
        current_user: 当前认证用户
        log_service: 日志服务

    Returns:
        Response: 导出的日志文件
    """
    try:
        log_data = log_service.export_logs(
            service=request.service,
            level=request.level,
            start_time=request.start_time,
            end_time=request.end_time,
            keyword=request.keyword,
            format=request.format,
        )

        content_type = "application/json" if request.format.lower() == "json" else "text/csv"
        filename = f"logs_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{request.format.lower()}"

        return Response(
            content=log_data,
            media_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.error(f"Error exporting logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导出日志失败",
        )


@router.get("/search", response_model=LogSearchResponse, status_code=status.HTTP_200_OK)
async def search_logs_get(
    service: Optional[str] = Query(None, description="服务名称"),
    level: Optional[str] = Query(None, description="日志级别"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    keyword: Optional[str] = Query(None, description="关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=1000, description="每页数量"),
    current_user: User = Depends(auth_middleware.get_current_user),
    log_service: LogService = Depends(get_log_service),
):
    """
    搜索日志（GET 方法，方便浏览器直接访问）

    Args:
        service: 服务名称
        level: 日志级别
        start_time: 开始时间
        end_time: 结束时间
        keyword: 关键词
        page: 页码
        page_size: 每页数量
        current_user: 当前认证用户
        log_service: 日志服务

    Returns:
        LogSearchResponse: 搜索结果
    """
    try:
        logs, total = log_service.search_logs(
            service=service,
            level=level,
            start_time=start_time,
            end_time=end_time,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )

        total_pages = (total + page_size - 1) // page_size

        return LogSearchResponse(
            items=[LogEntry(**log) for log in logs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error searching logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索日志失败",
        )

