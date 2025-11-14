"""
@purpose: 系统设置路由，提供配置管理、环境变量、健康检查、备份恢复等 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.settings_service import SettingsService
from src.infrastructure.database import get_db
from src.models.database import User
from src.models.schemas.settings import (
    SystemSettingsResponse,
    SystemSettingsUpdateRequest,
    EnvironmentVariableListResponse,
    EnvironmentVariableUpdateRequest,
    SystemHealthStatusResponse,
    BackupListResponse,
    BackupRequest,
    BackupRestoreRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["系统设置"])


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """
    获取系统设置服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        SettingsService: 系统设置服务实例
    """
    return SettingsService(db=db)


@router.get("", response_model=SystemSettingsResponse, status_code=status.HTTP_200_OK)
async def get_system_settings(
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    获取系统配置

    Args:
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        SystemSettingsResponse: 系统配置响应
    """
    try:
        settings = settings_service.get_system_settings()
        return SystemSettingsResponse(**settings)
    except Exception as e:
        logger.error(f"Error getting system settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统配置失败",
        )


@router.put("", response_model=SystemSettingsResponse, status_code=status.HTTP_200_OK)
async def update_system_settings(
    request: SystemSettingsUpdateRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    更新系统配置

    Args:
        request: 系统配置更新请求
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        SystemSettingsResponse: 更新后的系统配置响应
    """
    try:
        updates = request.model_dump(exclude_unset=True)
        updated_settings = settings_service.update_system_settings(updates)
        return SystemSettingsResponse(**updated_settings)
    except Exception as e:
        logger.error(f"Error updating system settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新系统配置失败",
        )


@router.get("/environment", response_model=EnvironmentVariableListResponse, status_code=status.HTTP_200_OK)
async def get_environment_variables(
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    获取环境变量列表

    Args:
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        EnvironmentVariableListResponse: 环境变量列表响应
    """
    try:
        env_vars = settings_service.get_environment_variables()
        return EnvironmentVariableListResponse(items=env_vars, total=len(env_vars))
    except Exception as e:
        logger.error(f"Error getting environment variables: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取环境变量列表失败",
        )


@router.put("/environment/{key}", status_code=status.HTTP_200_OK)
async def update_environment_variable(
    key: str,
    request: EnvironmentVariableUpdateRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    更新环境变量

    Args:
        key: 环境变量键
        request: 环境变量更新请求
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        Dict: 更新结果
    """
    try:
        success = settings_service.update_environment_variable(
            key, request.value, request.description
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新环境变量失败",
            )
        return {"success": True, "message": f"环境变量 {key} 已更新"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating environment variable: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新环境变量失败: {str(e)}",
        )


@router.get("/health", response_model=SystemHealthStatusResponse, status_code=status.HTTP_200_OK)
async def get_system_health(
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    获取系统健康状态

    Args:
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        SystemHealthStatusResponse: 系统健康状态响应
    """
    try:
        health = settings_service.get_system_health()
        return SystemHealthStatusResponse(**health)
    except Exception as e:
        logger.error(f"Error getting system health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统健康状态失败",
        )


@router.post("/backup", status_code=status.HTTP_201_CREATED)
async def create_backup(
    request: BackupRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    创建系统备份

    Args:
        request: 备份请求
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        Dict: 备份记录信息
    """
    try:
        backup = settings_service.create_backup(
            name=request.name,
            include_database=request.include_database,
            include_config=request.include_config,
            include_versions=request.include_versions,
            description=request.description,
        )
        return backup
    except Exception as e:
        logger.error(f"Error creating backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建备份失败: {str(e)}",
        )


@router.get("/backups", response_model=BackupListResponse, status_code=status.HTTP_200_OK)
async def list_backups(
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    获取备份列表

    Args:
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        BackupListResponse: 备份列表响应
    """
    try:
        backups = settings_service.list_backups()
        return BackupListResponse(items=backups, total=len(backups))
    except Exception as e:
        logger.error(f"Error listing backups: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取备份列表失败",
        )


@router.post("/restore/{backup_id}", status_code=status.HTTP_200_OK)
async def restore_backup(
    backup_id: str,
    request: BackupRestoreRequest,
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    恢复系统备份

    Args:
        backup_id: 备份 ID
        request: 备份恢复请求
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        Dict: 恢复结果
    """
    try:
        success = settings_service.restore_backup(
            backup_id=backup_id,
            restore_database=request.restore_database,
            restore_config=request.restore_config,
            restore_versions=request.restore_versions,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="恢复备份失败",
            )
        return {"success": True, "message": f"备份 {backup_id} 恢复成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复备份失败: {str(e)}",
        )


@router.get("/backups/{backup_id}/download", status_code=status.HTTP_200_OK)
async def download_backup(
    backup_id: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    下载备份文件

    Args:
        backup_id: 备份 ID
        current_user: 当前认证用户
        settings_service: 系统设置服务

    Returns:
        FileResponse: 备份文件
    """
    try:
        from pathlib import Path

        backup_dir = Path("backups")
        archive_path = backup_dir / f"{backup_id}.tar.gz"

        if not archive_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"备份文件不存在: {backup_id}",
            )

        return FileResponse(
            path=str(archive_path),
            filename=f"{backup_id}.tar.gz",
            media_type="application/gzip",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载备份失败: {str(e)}",
        )

