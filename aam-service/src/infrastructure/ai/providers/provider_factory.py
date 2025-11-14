"""
@purpose: 模型服務提供商工廠，根據配置創建對應的 Provider
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import logging
from typing import Optional

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType
from src.infrastructure.ai.providers.gemini_provider import GeminiProvider
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider
from src.infrastructure.ai.providers.qwen_provider import QwenProvider

logger = logging.getLogger(__name__)


class ModelProviderFactory:
    """模型服務提供商工廠"""

    @staticmethod
    def create_provider(
        provider_type: ModelProviderType,
        model_name: str,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 120,
        max_tokens: int = 8192,  # 从模型配置获取
        temperature: float = 0.5,  # 从模型配置获取
        **kwargs: dict,  # 保留用于未来扩展，但不使用Provider特定参数名
    ) -> IModelProvider:
        """
        根據配置創建對應的 Provider
        
        使用統一參數名，實現真正的抽象層。每個Provider自己處理參數映射和驗證。
        
        Args:
            provider_type: 提供商類型
            model_name: 模型名稱
            api_base_url: API 基礎 URL（可選，統一參數名）
            api_key: API 密鑰（可選，統一參數名）
            timeout: 超時時間（秒）
            **kwargs: 其他參數（保留用於未來擴展，但不使用Provider特定參數名）
            
        Returns:
            Provider 實例
            
        Raises:
            ValueError: 當配置無效或 Provider 類型不支持時
        """
        try:
            if provider_type == ModelProviderType.OLLAMA:
                # 使用統一參數名，Provider自己處理默認值
                return OllamaProvider(
                    model_name=model_name,
                    api_base_url=api_base_url,  # 統一參數名，Provider內部映射到base_url
                    timeout=timeout,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            
            elif provider_type == ModelProviderType.VLLM:
                # vLLM Provider 尚未實現
                raise ValueError(
                    f"Provider 類型 {provider_type.value} 尚未實現。"
                    "請先實現 VLLMProvider 類。"
                )
            
            elif provider_type == ModelProviderType.OPENAI:
                # OpenAI Provider 尚未實現
                raise ValueError(
                    f"Provider 類型 {provider_type.value} 尚未實現。"
                    "請先實現 OpenAIProvider 類。"
                )
            
            elif provider_type == ModelProviderType.ANTHROPIC:
                # Anthropic Provider 尚未實現
                raise ValueError(
                    f"Provider 類型 {provider_type.value} 尚未實現。"
                    "請先實現 AnthropicProvider 類。"
                )
            
            elif provider_type == ModelProviderType.QWEN:
                # 使用統一參數名，Provider自己驗證
                return QwenProvider(
                    model_name=model_name,
                    api_base_url=api_base_url,  # 統一參數名，Provider自己處理默認值
                    api_key=api_key,  # 統一參數名，Provider自己驗證
                    timeout=timeout,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            
            elif provider_type == ModelProviderType.GEMINI:
                # 使用統一參數名，Provider自己驗證
                return GeminiProvider(
                    model_name=model_name,
                    api_base_url=api_base_url,  # 統一參數名，Provider自己處理默認值
                    api_key=api_key,  # 統一參數名，Provider自己驗證
                    timeout=timeout,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            
            else:
                raise ValueError(f"不支持的 Provider 類型: {provider_type.value}")
        
        except Exception as e:
            logger.error(
                f"創建 Provider 失敗: {e}",
                extra={
                    "provider_type": provider_type.value,
                    "model_name": model_name,
                    "error": str(e),
                },
            )
            raise ValueError(f"創建 Provider 失敗: {e}") from e

    @staticmethod
    def create_provider_from_config(config: dict) -> IModelProvider:
        """
        從配置字典創建 Provider
        
        Args:
            config: 配置字典，應包含 provider_type, model_name 等
            
        Returns:
            Provider 實例
            
        Raises:
            ValueError: 當配置無效時
        """
        # 驗證必需配置
        if "provider_type" not in config:
            raise ValueError("配置中缺少 provider_type")
        
        if "model_name" not in config:
            raise ValueError("配置中缺少 model_name")
        
        # 解析 provider_type
        provider_type_str = config["provider_type"]
        try:
            provider_type = ModelProviderType(provider_type_str)
        except ValueError as e:
            raise ValueError(
                f"無效的 provider_type: {provider_type_str}。"
                f"支持的類型: {[t.value for t in ModelProviderType]}"
            ) from e
        
        # 提取其他配置
        model_name = config["model_name"]
        api_base_url = config.get("api_base_url")
        api_key = config.get("api_key")
        timeout = config.get("timeout", 120)
        
        # 提取其他參數
        other_kwargs = {k: v for k, v in config.items() 
                       if k not in ["provider_type", "model_name", "api_base_url", "api_key", "timeout"]}
        
        return ModelProviderFactory.create_provider(
            provider_type=provider_type,
            model_name=model_name,
            api_base_url=api_base_url,
            api_key=api_key,
            timeout=timeout,
            **other_kwargs,
        )

