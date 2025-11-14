"""
@purpose: 服务管理路由，提供服务列表、详情、操作等 API
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
from src.core.services.service_management_service import ServiceManagementService
from src.infrastructure.database import get_db
from src.models.database import User
from src.models.schemas.service import (
    ServiceDetail,
    ServiceHealth,
    ServiceOperationRequest,
    ServiceOperationResponse,
    ServiceStats,
    ServiceStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/services", tags=["服务管理"])


def get_service_management_service(
    db: Session = Depends(get_db),
) -> ServiceManagementService:
    """
    获取服务管理服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        ServiceManagementService: 服务管理服务实例
    """
    docker_service = DockerService()
    return ServiceManagementService(docker_service=docker_service, db=db)


@router.get("", response_model=List[ServiceStatus], status_code=status.HTTP_200_OK)
async def get_services(
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    获取服务列表

    Args:
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        List[ServiceStatus]: 服务状态列表
    """
    try:
        services = service_service.get_service_list()
        return [ServiceStatus(**service) for service in services]
    except Exception as e:
        logger.error(f"Error getting services: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务列表失败",
        )


@router.get("/{service_name}", response_model=ServiceDetail, status_code=status.HTTP_200_OK)
async def get_service_detail(
    service_name: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    获取服务详情

    Args:
        service_name: 服务名称
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceDetail: 服务详情
    """
    try:
        detail = service_service.get_service_detail(service_name)
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"服务 {service_name} 不存在",
            )
        return ServiceDetail(**detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务详情失败",
        )


@router.post(
    "/{service_name}/start",
    response_model=ServiceOperationResponse,
    status_code=status.HTTP_200_OK,
)
async def start_service(
    service_name: str,
    request: ServiceOperationRequest = ServiceOperationRequest(),
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    启动服务

    Args:
        service_name: 服务名称
        request: 操作请求
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceOperationResponse: 操作结果
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="需要确认操作",
            )
        result = service_service.operate_service(service_name, "start", request.reason)
        return ServiceOperationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting service: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启动服务失败",
        )


@router.post(
    "/{service_name}/stop",
    response_model=ServiceOperationResponse,
    status_code=status.HTTP_200_OK,
)
async def stop_service(
    service_name: str,
    request: ServiceOperationRequest = ServiceOperationRequest(),
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    停止服务

    Args:
        service_name: 服务名称
        request: 操作请求
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceOperationResponse: 操作结果
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="需要确认操作",
            )
        result = service_service.operate_service(service_name, "stop", request.reason)
        return ServiceOperationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping service: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="停止服务失败",
        )


@router.post(
    "/{service_name}/restart",
    response_model=ServiceOperationResponse,
    status_code=status.HTTP_200_OK,
)
async def restart_service(
    service_name: str,
    request: ServiceOperationRequest = ServiceOperationRequest(),
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    重启服务

    Args:
        service_name: 服务名称
        request: 操作请求
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceOperationResponse: 操作结果
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="需要确认操作",
            )
        result = service_service.operate_service(service_name, "restart", request.reason)
        return ServiceOperationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting service: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重启服务失败",
        )


@router.get(
    "/{service_name}/stats",
    response_model=ServiceStats,
    status_code=status.HTTP_200_OK,
)
async def get_service_stats(
    service_name: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    获取服务资源统计

    Args:
        service_name: 服务名称
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceStats: 服务资源统计
    """
    try:
        stats = service_service.get_service_stats(service_name)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"服务 {service_name} 不存在",
            )
        return ServiceStats(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务统计失败",
        )


@router.get(
    "/{service_name}/health",
    response_model=ServiceHealth,
    status_code=status.HTTP_200_OK,
)
async def get_service_health(
    service_name: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    service_service: ServiceManagementService = Depends(get_service_management_service),
):
    """
    获取服务健康状态

    Args:
        service_name: 服务名称
        current_user: 当前认证用户
        service_service: 服务管理服务

    Returns:
        ServiceHealth: 服务健康状态
    """
    try:
        health = service_service.get_service_health(service_name)
        return ServiceHealth(**health)
    except Exception as e:
        logger.error(f"Error getting service health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务健康状态失败",
        )

