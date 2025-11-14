"""
@purpose: Provider 配置适配器，将配置层的 Provider 特定配置映射到通用参数
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import logging
from typing import Dict, Any, Optional

from src.core.interfaces.i_model_provider import ModelProviderType
from src.config.model_config_loader import get_model_config_loader
from src.config.settings import ModelServiceSettings

logger = logging.getLogger(__name__)


class ProviderConfigAdapter:
    """
    Provider 配置适配器
    
    将配置层的 Provider 特定配置映射到通用参数，实现真正的抽象层
    """
    
    @staticmethod
    def get_provider_config(
        provider_type: ModelProviderType,
        config: ModelServiceSettings,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将配置层的Provider特定配置映射到通用参数
        
        Args:
            provider_type: Provider 类型
            config: 模型服务配置
            model_name: 指定的模型名称（可选，如果未指定则从配置文件获取默认模型）
            
        Returns:
            包含通用参数的字典：
            - model_name: 模型名称
            - api_base_url: API 基础 URL
            - api_key: API 密钥（如果需要）
            - timeout: 超时时间（秒）
            - max_tokens: 最大 token 数（从模型配置获取）
            - temperature: 温度参数（从模型配置获取）
        """
        # 获取模型配置加载器
        loader = get_model_config_loader(config.model_config_path)
        
        # 确定要使用的模型名称
        final_model_name = None
        model_config = None
        
        if model_name:
            # 如果指定了模型名称，验证该模型是否存在且启用
            model_config = loader.get_model_config(provider_type, model_name)
            if model_config and model_config.enabled:
                final_model_name = model_name
            else:
                logger.warning(
                    f"指定的模型 {model_name} 不存在或未启用，将使用默认模型",
                    extra={
                        "provider_type": provider_type.value,
                        "model_name": model_name,
                    }
                )
        
        if not final_model_name:
            # 从配置文件获取默认模型
            default_model = loader.get_default_model(provider_type)
            if default_model:
                final_model_name = default_model.model_name
                model_config = default_model
            else:
                # 回退到硬编码默认值
                logger.warning(
                    f"配置文件未找到 {provider_type.value} 的启用模型，使用硬编码默认值"
                )
        
        # 获取模型配置中的参数
        max_tokens = model_config.max_tokens if model_config else 8192
        temperature = model_config.temperature if model_config else 0.5
        
        # 根据 Provider 类型获取配置
        if provider_type == ModelProviderType.QWEN:
            return {
                "model_name": final_model_name or config.qwen_model_name or "qwen-turbo",
                "api_base_url": config.qwen_api_base_url,
                "api_key": config.qwen_api_key,
                "timeout": config.qwen_timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif provider_type == ModelProviderType.OLLAMA:
            return {
                "model_name": final_model_name or config.model_name or "llama3",
                "api_base_url": config.api_base_url or "http://localhost:11434",
                "api_key": None,  # Ollama 不需要 API Key
                "timeout": config.timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif provider_type == ModelProviderType.OPENAI:
            return {
                "model_name": final_model_name or config.model_name or "gpt-3.5-turbo",
                "api_base_url": config.openai_api_base_url or "https://api.openai.com/v1",
                "api_key": config.openai_api_key,
                "timeout": config.timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif provider_type == ModelProviderType.VLLM:
            return {
                "model_name": final_model_name or config.model_name,
                "api_base_url": config.vllm_api_base_url or config.api_base_url,
                "api_key": config.api_key,
                "timeout": config.timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif provider_type == ModelProviderType.ANTHROPIC:
            return {
                "model_name": final_model_name or config.model_name or "claude-3-sonnet-20240229",
                "api_base_url": config.api_base_url or "https://api.anthropic.com/v1",
                "api_key": config.api_key,
                "timeout": config.timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif provider_type == ModelProviderType.GEMINI:
            return {
                "model_name": final_model_name or config.gemini_model_name or "gemini-2.5-flash",
                "api_base_url": config.gemini_api_base_url,
                "api_key": config.gemini_api_key,
                "timeout": config.gemini_timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        else:
            # 默认使用通用配置
            return {
                "model_name": final_model_name or config.model_name or "llama3",
                "api_base_url": config.api_base_url,
                "api_key": config.api_key,
                "timeout": config.timeout,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

