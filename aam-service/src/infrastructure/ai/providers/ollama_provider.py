"""
@purpose: Ollama 模型服務提供商實現，封裝 Ollama 服務調用
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import logging
from typing import Any, Optional

import httpx
from langchain_community.llms import Ollama

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType

logger = logging.getLogger(__name__)


class OllamaProvider(IModelProvider):
    """
    Ollama 模型服務提供商
    
    封裝 Ollama 服務的調用，提供統一的接口
    """

    def __init__(
        self,
        model_name: str = "llama3",
        api_base_url: Optional[str] = None,  # 接受通用参数名
        timeout: int = 120,
        max_tokens: int = 8192,  # 从模型配置获取的默认值
        temperature: float = 0.5,  # 从模型配置获取的默认值
        **kwargs: Any,  # 保留用于向后兼容（base_url）
    ):
        """
        初始化 Ollama Provider
        
        接受通用参数名，内部映射到自己的参数。Provider自己处理默认值和参数映射。
        
        Args:
            model_name: Ollama 模型名稱（如 llama3, mistral, qwen2.5 等）
            api_base_url: API 基礎 URL（統一參數名，可選）
            timeout: 請求超時時間（秒）
            **kwargs: 其他參數（保留用於向後兼容，如base_url）
        """
        self.model_name = model_name
        # Provider自己处理参数映射：api_base_url -> base_url
        # 支持向后兼容：如果传入了base_url，优先使用
        self.base_url = kwargs.get("base_url") or api_base_url or "http://localhost:11434"
        self.timeout = timeout
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature
        
        # 檢查依賴是否安裝
        if Ollama is None:
            raise ImportError(
                "langchain-community 未安裝。請運行: pip install langchain-community"
            )
        
        # 初始化 LangChain Ollama LLM
        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            logger.info(
                "Ollama Provider 初始化成功",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                },
            )
        except Exception as e:
            logger.error(
                f"Ollama Provider 初始化失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                    "error": str(e),
                },
            )
            raise

    @property
    def provider_type(self) -> ModelProviderType:
        """返回提供商類型"""
        return ModelProviderType.OLLAMA

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        生成文本（使用直接 HTTP 請求，非流式）
        
        Args:
            prompt: 輸入提示詞
            **kwargs: 其他參數（如 temperature, max_tokens 等）
            
        Returns:
            生成的文本內容
            
        Raises:
            RuntimeError: 當服務不可用或生成失敗時
        """
        # 檢查服務是否可用
        if not await self.check_available():
            raise RuntimeError("Ollama 服務不可用")
        
        try:
            # 使用直接 HTTP 請求（非流式），避免 aiohttp 流式讀取超時問題
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,  # 非流式，等待完整響應
                        **kwargs
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("response", "")
                    logger.debug(
                        "Ollama 文本生成成功",
                        extra={
                            "model_name": self.model_name,
                            "prompt_length": len(prompt),
                            "response_length": len(result),
                        },
                    )
                    return result
                else:
                    error_msg = f"Ollama API 返回錯誤: {response.status_code}"
                    logger.error(
                        error_msg,
                        extra={
                            "model_name": self.model_name,
                            "base_url": self.base_url,
                            "status_code": response.status_code,
                            "response_text": response.text[:200],
                        },
                    )
                    raise RuntimeError(error_msg)
                    
        except httpx.TimeoutException as e:
            logger.error(
                f"Ollama 文本生成超時（{self.timeout * 2}秒）",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                    "timeout": self.timeout * 2,
                },
            )
            raise RuntimeError(f"Ollama 文本生成超時（{self.timeout * 2}秒）") from e
        except Exception as e:
            logger.error(
                f"Ollama 文本生成失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"Ollama 文本生成失敗: {e}") from e

    async def check_available(self) -> bool:
        """
        檢查 Ollama 服務是否可用
        
        Returns:
            True 如果 Ollama 可用，False 否則
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(
                f"Ollama 服務不可用: {e}",
                extra={"base_url": self.base_url, "error": str(e)},
            )
            return False

    def get_config(self) -> dict[str, Any]:
        """
        獲取提供商配置信息
        
        Returns:
            配置信息字典
        """
        return {
            "provider_type": self.provider_type.value,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "timeout": self.timeout,
        }

