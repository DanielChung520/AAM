"""
@purpose: 版本管理路由，提供版本创建、查询、比较等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.version_service import VersionService
from src.infrastructure.database import get_db
from src.models.database import User
from src.models.schemas.version import (
    Version,
    VersionCreateRequest,
    VersionDetail,
    VersionCompareResponse,
    VersionListResponse,
    VersionFilter,
    VersionStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/versions", tags=["版本管理"])


def get_version_service(db: Session = Depends(get_db)) -> VersionService:
    """
    获取版本服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        VersionService: 版本服务实例
    """
    return VersionService(db)


@router.get("", response_model=VersionListResponse, status_code=status.HTTP_200_OK)
async def list_versions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[VersionStatus] = Query(None, description="版本状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    created_after: Optional[str] = Query(None, description="创建时间起始（ISO 格式）"),
    created_before: Optional[str] = Query(None, description="创建时间结束（ISO 格式）"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序（asc/desc）"),
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    获取版本列表

    Args:
        page: 页码
        page_size: 每页数量
        status: 版本状态过滤
        search: 搜索关键词
        created_after: 创建时间起始
        created_before: 创建时间结束
        sort_by: 排序字段
        sort_order: 排序顺序
        current_user: 当前认证用户
        version_service: 版本服务

    Returns:
        VersionListResponse: 版本列表响应
    """
    try:
        from datetime import datetime

        filters = VersionFilter(
            status=status,
            search=search,
            created_after=datetime.fromisoformat(created_after) if created_after else None,
            created_before=datetime.fromisoformat(created_before) if created_before else None,
        )

        versions, total = version_service.list_versions(
            page=page,
            page_size=page_size,
            filters=filters if any([status, search, created_after, created_before]) else None,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = (total + page_size - 1) // page_size

        return VersionListResponse(
            items=versions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"获取版本列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取版本列表失败",
        )


@router.post("", response_model=Version, status_code=status.HTTP_201_CREATED)
async def create_version(
    request: VersionCreateRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    创建新版本

    Args:
        request: 版本创建请求
        current_user: 当前认证用户
        version_service: 版本服务

    Returns:
        Version: 创建的版本对象
    """
    try:
        version = version_service.create_version(
            version=request.version,
            git_tag=request.git_tag,
            description=request.description,
            image_tag=request.image_tag,
            created_by=current_user.id,
        )
        return version
    except ValueError as e:
        logger.warning(f"创建版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"创建版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建版本失败",
        )


@router.get("/{version}", response_model=VersionDetail, status_code=status.HTTP_200_OK)
async def get_version(
    version: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    获取版本详情

    Args:
        version: 版本号
        current_user: 当前认证用户
        version_service: 版本服务

    Returns:
        VersionDetail: 版本详情
    """
    try:
        version_obj = version_service.get_version(version)
        if not version_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"版本 {version} 不存在",
            )

        # 获取版本配置
        version_config = version_service.repository.get_version_config(version_obj)

        return VersionDetail(
            version=version_obj.version,
            status=version_obj.status,
            git_commit=version_obj.git_commit,
            git_branch=version_obj.git_branch,
            git_tag=version_obj.git_tag,
            image_tag=version_obj.image_tag,
            created_at=version_obj.created_at,
            created_by=version_obj.creator.username if version_obj.creator else None,
            description=version_obj.description,
            config_snapshot=version_config.config_snapshot if version_config else None,
            docker_compose_config=version_config.docker_compose_config if version_config else None,
            environment_variables=version_config.environment_variables if version_config else None,
            service_config=version_config.service_config if version_config else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取版本详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取版本详情失败",
        )


@router.get("/{v1}/compare/{v2}", response_model=VersionCompareResponse, status_code=status.HTTP_200_OK)
async def compare_versions(
    v1: str,
    v2: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    比较两个版本的配置差异

    Args:
        v1: 版本1
        v2: 版本2
        current_user: 当前认证用户
        version_service: 版本服务

    Returns:
        VersionCompareResponse: 版本比较结果
    """
    try:
        result = version_service.compare_versions(v1, v2)
        return VersionCompareResponse(**result)
    except ValueError as e:
        logger.warning(f"比较版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"比较版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="比较版本失败",
        )


@router.get("/active", response_model=Version, status_code=status.HTTP_200_OK)
async def get_active_version(
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    获取当前活动版本

    Args:
        current_user: 当前认证用户
        version_service: 版本服务

    Returns:
        Version: 活动版本对象
    """
    try:
        version = version_service.get_active_version()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="当前没有活动版本",
            )
        return version
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取活动版本失败",
        )


@router.delete("/{version}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(
    version: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    version_service: VersionService = Depends(get_version_service),
):
    """
    删除版本（仅非活动版本）

    Args:
        version: 版本号
        current_user: 当前认证用户
        version_service: 版本服务
    """
    try:
        success = version_service.delete_version(version)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"版本 {version} 不存在",
            )
    except ValueError as e:
        logger.warning(f"删除版本失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除版本失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除版本失败",
        )

