"""
@purpose: 仪表盘路由，提供统计概览、服务状态、系统指标等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.docker_service import DockerService
from src.core.services.metrics_service import MetricsService
from src.infrastructure.database import get_db
from src.models.database import User
from src.models.schemas.dashboard import (
    DashboardStats,
    ServiceStatus,
    SystemMetrics,
    RecentOperation,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


def get_metrics_service(
    db: Session = Depends(get_db),
) -> MetricsService:
    """
    获取指标服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        MetricsService: 指标服务实例
    """
    docker_service = DockerService()
    return MetricsService(docker_service=docker_service, db=db)


@router.get("/stats", response_model=DashboardStats, status_code=status.HTTP_200_OK)
async def get_dashboard_stats(
    current_user: User = Depends(auth_middleware.get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """
    获取仪表盘统计概览

    Args:
        current_user: 当前认证用户
        metrics_service: 指标服务

    Returns:
        DashboardStats: 统计概览
    """
    try:
        stats = metrics_service.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计概览失败",
        )


@router.get("/services", response_model=List[ServiceStatus], status_code=status.HTTP_200_OK)
async def get_service_statuses(
    current_user: User = Depends(auth_middleware.get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """
    获取服务状态列表

    Args:
        current_user: 当前认证用户
        metrics_service: 指标服务

    Returns:
        List[ServiceStatus]: 服务状态列表
    """
    try:
        services = metrics_service.get_service_statuses()
        return services
    except Exception as e:
        logger.error(f"Error getting service statuses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务状态失败",
        )


@router.get("/metrics", response_model=SystemMetrics, status_code=status.HTTP_200_OK)
async def get_system_metrics(
    current_user: User = Depends(auth_middleware.get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """
    获取系统资源指标

    Args:
        current_user: 当前认证用户
        metrics_service: 指标服务

    Returns:
        SystemMetrics: 系统资源指标
    """
    try:
        metrics = metrics_service.get_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统指标失败",
        )


@router.get(
    "/recent-operations",
    response_model=List[RecentOperation],
    status_code=status.HTTP_200_OK,
)
async def get_recent_operations(
    limit: int = 10,
    hours: int = 24,
    current_user: User = Depends(auth_middleware.get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """
    获取最近操作记录

    Args:
        limit: 返回记录数限制（默认 10）
        hours: 查询时间范围（小时，默认 24）
        current_user: 当前认证用户
        metrics_service: 指标服务

    Returns:
        List[RecentOperation]: 最近操作记录列表
    """
    try:
        operations = metrics_service.get_recent_operations(limit=limit, hours=hours)
        return operations
    except Exception as e:
        logger.error(f"Error getting recent operations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取最近操作记录失败",
        )

