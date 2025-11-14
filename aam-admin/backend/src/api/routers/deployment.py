"""
@purpose: 部署管理路由，提供部署、回滚、状态查询等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.deployment_service import DeploymentService
from src.infrastructure.database import get_db
from src.models.database import User, DeploymentStatus
from src.models.schemas.deployment import (
    DeploymentRecord,
    DeploymentRequest,
    DeploymentPreviewResponse,
    DeploymentListResponse,
    DeploymentStatusResponse,
    RollbackRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/deployments", tags=["部署管理"])


def get_deployment_service(db: Session = Depends(get_db)) -> DeploymentService:
    """
    获取部署服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        DeploymentService: 部署服务实例
    """
    return DeploymentService(db)


@router.get("", response_model=DeploymentListResponse, status_code=status.HTTP_200_OK)
async def list_deployments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    version: Optional[str] = Query(None, description="版本号过滤"),
    status_filter: Optional[DeploymentStatus] = Query(None, description="状态过滤", alias="status"),
    operator_id: Optional[int] = Query(None, description="操作者 ID 过滤"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    sort_by: str = Query("deployment_time", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序（asc/desc）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    获取部署历史列表

    Args:
        page: 页码
        page_size: 每页数量
        version: 版本号过滤
        status_filter: 状态过滤
        operator_id: 操作者 ID 过滤
        start_time: 开始时间
        end_time: 结束时间
        sort_by: 排序字段
        sort_order: 排序顺序
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        DeploymentListResponse: 部署列表响应
    """
    try:
        from datetime import datetime

        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        deployments, total = deployment_service.history_service.list_deployments(
            page=page,
            page_size=page_size,
            version=version,
            status=status_filter,
            operator_id=operator_id,
            start_time=start_dt,
            end_time=end_dt,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # 转换为响应模型
        deployment_records = []
        for dep in deployments:
            operator_name = dep.operator_user.username if dep.operator_user else None
            deployment_records.append(
                DeploymentRecord(
                    id=dep.id,
                    version=dep.version,
                    status=dep.status,
                    operator_id=dep.operator_id,
                    operator_name=operator_name,
                    deployment_time=dep.deployment_time,
                    completed_time=dep.completed_time,
                    rollback_version=dep.rollback_version,
                    deployment_strategy=dep.deployment_strategy,
                    config_snapshot=dep.config_snapshot,
                    error_message=dep.error_message,
                    extra_data=dep.extra_data,
                )
            )

        total_pages = (total + page_size - 1) // page_size

        return DeploymentListResponse(
            items=deployment_records,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"获取部署列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部署列表失败",
        )


@router.get("/{deployment_id}", response_model=DeploymentRecord, status_code=status.HTTP_200_OK)
async def get_deployment(
    deployment_id: int,
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    获取部署详情

    Args:
        deployment_id: 部署记录 ID
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        DeploymentRecord: 部署记录
    """
    try:
        deployment = deployment_service.history_service.get_deployment(deployment_id)
        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"部署记录 {deployment_id} 不存在",
            )

        operator_name = deployment.operator_user.username if deployment.operator_user else None

        return DeploymentRecord(
            id=deployment.id,
            version=deployment.version,
            status=deployment.status,
            operator_id=deployment.operator_id,
            operator_name=operator_name,
            deployment_time=deployment.deployment_time,
            completed_time=deployment.completed_time,
            rollback_version=deployment.rollback_version,
            deployment_strategy=deployment.deployment_strategy,
            config_snapshot=deployment.config_snapshot,
            error_message=deployment.error_message,
            extra_data=deployment.extra_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取部署详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部署详情失败",
        )


@router.post("/versions/{version}/deploy", status_code=status.HTTP_201_CREATED)
async def deploy_version(
    version: str,
    request: DeploymentRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    部署指定版本

    Args:
        version: 版本号
        request: 部署请求
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        dict: 部署记录 ID
    """
    try:
        # 如果请求中指定了预览，只返回预览结果
        if request.preview:
            preview = deployment_service.preview_deployment(
                version, request.strategy, request.config
            )
            return preview.dict()

        # 执行部署
        deployment_id = deployment_service.deploy_version(
            version=version,
            strategy=request.strategy,
            operator_id=current_user.id,
            config=request.config,
        )

        return {"deployment_id": deployment_id, "message": "部署已启动"}
    except ValueError as e:
        logger.warning(f"部署版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"部署版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="部署版本失败",
        )


@router.post("/versions/{version}/rollback", status_code=status.HTTP_201_CREATED)
async def rollback_version(
    version: str,
    request: RollbackRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    回滚到指定版本

    Args:
        version: 要回滚到的版本号
        request: 回滚请求
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        dict: 部署记录 ID
    """
    try:
        deployment_id = deployment_service.rollback_version(
            version=version,
            operator_id=current_user.id,
            reason=request.reason,
        )

        return {"deployment_id": deployment_id, "message": "回滚已启动"}
    except ValueError as e:
        logger.warning(f"回滚版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"回滚版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="回滚版本失败",
        )


@router.post("/versions/active/switch", status_code=status.HTTP_200_OK)
async def switch_active_version(
    version: str = Query(..., description="要切换到的版本号"),
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    切换活动版本（零中断）

    Args:
        version: 要切换到的版本号
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        dict: 切换结果
    """
    try:
        success = deployment_service.switch_active_version(
            version=version, operator_id=current_user.id
        )

        return {"success": success, "message": f"活动版本已切换为 {version}"}
    except ValueError as e:
        logger.warning(f"切换活动版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"切换活动版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="切换活动版本失败",
        )


@router.get("/{deployment_id}/status", response_model=DeploymentStatusResponse, status_code=status.HTTP_200_OK)
async def get_deployment_status(
    deployment_id: int,
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    获取部署状态

    Args:
        deployment_id: 部署记录 ID
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        DeploymentStatusResponse: 部署状态
    """
    try:
        status_response = deployment_service.get_deployment_status(deployment_id)
        if not status_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"部署记录 {deployment_id} 不存在",
            )

        return status_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取部署状态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部署状态失败",
        )


@router.get("/{deployment_id}/logs", status_code=status.HTTP_200_OK)
async def get_deployment_logs(
    deployment_id: int,
    tail: int = Query(1000, ge=1, le=10000, description="返回最后 N 行日志"),
    current_user: User = Depends(auth_middleware.get_current_user),
    deployment_service: DeploymentService = Depends(get_deployment_service),
):
    """
    获取部署日志

    Args:
        deployment_id: 部署记录 ID
        tail: 返回最后 N 行日志
        current_user: 当前认证用户
        deployment_service: 部署服务

    Returns:
        dict: 部署日志
    """
    try:
        logs = deployment_service.get_deployment_logs(deployment_id, tail=tail)
        if logs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"部署记录 {deployment_id} 不存在或没有日志",
            )

        return {"deployment_id": deployment_id, "logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取部署日志失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部署日志失败",
        )

