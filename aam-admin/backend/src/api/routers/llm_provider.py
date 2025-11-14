"""
@purpose: LLM Provider 管理路由，提供 Provider 和模型配置管理 API
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.middleware.auth_middleware import auth_middleware
from src.core.services.config_service import ConfigService
from src.models.database import User
from src.models.schemas.llm_provider import (
    LLMProvider,
    ModelConfig,
    ModelConfigUpdate,
    ProviderTestResponse,
    ProviderListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm-providers", tags=["LLM Provider 管理"])


def get_config_service() -> ConfigService:
    """
    获取配置服务实例（依赖注入）

    Returns:
        ConfigService: 配置服务实例
    """
    return ConfigService()


@router.get("", response_model=ProviderListResponse, status_code=status.HTTP_200_OK)
async def get_providers(
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    获取所有 LLM Provider 列表

    Args:
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        ProviderListResponse: Provider 列表
    """
    try:
        providers = config_service.get_providers()
        return ProviderListResponse(providers=providers)
    except Exception as e:
        logger.error(f"获取 Provider 列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 Provider 列表失败",
        )


@router.get("/{provider_type}", response_model=LLMProvider, status_code=status.HTTP_200_OK)
async def get_provider(
    provider_type: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    获取指定 Provider 的配置

    Args:
        provider_type: Provider 类型 (qwen/gemini/ollama)
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        LLMProvider: Provider 配置

    Raises:
        HTTPException: 当 Provider 不存在时
    """
    try:
        provider = config_service.get_provider(provider_type.lower())
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_type} 不存在",
            )
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 Provider 配置失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 Provider 配置失败",
        )


@router.get(
    "/{provider_type}/models", response_model=List[ModelConfig], status_code=status.HTTP_200_OK
)
async def get_models(
    provider_type: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    获取指定 Provider 的模型列表

    Args:
        provider_type: Provider 类型
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        List[ModelConfig]: 模型列表

    Raises:
        HTTPException: 当 Provider 不存在时
    """
    try:
        provider = config_service.get_provider(provider_type.lower())
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_type} 不存在",
            )
        return provider.models
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模型列表失败",
        )


@router.put(
    "/{provider_type}/models/{model_name}",
    response_model=ModelConfig,
    status_code=status.HTTP_200_OK,
)
async def update_model(
    provider_type: str,
    model_name: str,
    updates: ModelConfigUpdate,
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    更新模型配置

    Args:
        provider_type: Provider 类型
        model_name: 模型名称
        updates: 更新数据
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        ModelConfig: 更新后的模型配置

    Raises:
        HTTPException: 当更新失败时
    """
    try:
        success = config_service.update_model_config(
            provider_type.lower(), model_name, updates
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新模型配置失败",
            )

        # 重新获取更新后的模型配置
        provider = config_service.get_provider(provider_type.lower())
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_type} 不存在",
            )

        # 查找更新后的模型
        updated_model = next(
            (m for m in provider.models if m.model_name == model_name), None
        )
        if not updated_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型 {model_name} 不存在",
            )

        return updated_model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模型配置失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新模型配置失败",
        )


@router.post(
    "/{provider_type}/models/{model_name}/toggle",
    response_model=ModelConfig,
    status_code=status.HTTP_200_OK,
)
async def toggle_model(
    provider_type: str,
    model_name: str,
    enabled: bool,
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    启用/禁用模型

    Args:
        provider_type: Provider 类型
        model_name: 模型名称
        enabled: 是否启用
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        ModelConfig: 更新后的模型配置

    Raises:
        HTTPException: 当操作失败时
    """
    try:
        success = config_service.toggle_model(provider_type.lower(), model_name, enabled)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="启用/禁用模型失败",
            )

        # 重新获取更新后的模型配置
        provider = config_service.get_provider(provider_type.lower())
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_type} 不存在",
            )

        # 查找更新后的模型
        updated_model = next(
            (m for m in provider.models if m.model_name == model_name), None
        )
        if not updated_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模型 {model_name} 不存在",
            )

        return updated_model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启用/禁用模型失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启用/禁用模型失败",
        )


@router.post(
    "/{provider_type}/test",
    response_model=ProviderTestResponse,
    status_code=status.HTTP_200_OK,
)
async def test_provider(
    provider_type: str,
    current_user: User = Depends(auth_middleware.get_current_user),
    config_service: ConfigService = Depends(get_config_service),
):
    """
    测试 Provider 连接

    Args:
        provider_type: Provider 类型
        current_user: 当前认证用户
        config_service: 配置服务

    Returns:
        ProviderTestResponse: 测试结果
    """
    try:
        result = config_service.test_provider(provider_type.lower())
        return ProviderTestResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            response_time_ms=result.get("response_time_ms"),
        )
    except Exception as e:
        logger.error(f"测试 Provider 失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="测试 Provider 失败",
        )

