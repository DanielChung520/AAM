"""
@purpose: Qwen 模型服務提供商實現，封裝阿里云 Qwen API 調用
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import logging
from typing import Any, Optional

import httpx

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType

logger = logging.getLogger(__name__)


class QwenProvider(IModelProvider):
    """
    Qwen 模型服務提供商
    
    封裝阿里云 Qwen API 的調用，提供統一的接口
    """

    def __init__(
        self,
        model_name: str = "qwen-turbo",
        api_base_url: Optional[str] = None,  # 接受通用参数名
        api_key: Optional[str] = None,  # 接受通用参数名
        timeout: int = 120,
        max_tokens: int = 8192,  # 从模型配置获取的默认值
        temperature: float = 0.5,  # 从模型配置获取的默认值
    ):
        """
        初始化 Qwen Provider
        
        接受通用参数名，Provider自己处理默认值和验证。
        
        Args:
            model_name: Qwen 模型名稱（如 qwen-turbo, qwen-plus, qwen-max 等）
            api_base_url: API 基礎 URL（統一參數名，可選，Provider自己處理默認值）
            api_key: API 密鑰（統一參數名，必須設置，Provider自己驗證）
            timeout: 請求超時時間（秒）
            
        Raises:
            ValueError: 當api_key未設置時
        """
        self.model_name = model_name
        # Provider自己处理默认值
        self.api_base_url = api_base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # Provider自己验证
        if not api_key:
            raise ValueError(
                "API Key必須設置。請通過以下方式之一設置：\n"
                "1. 環境變量 QWEN_API_KEY（推薦）\n"
                "2. 創建Provider時傳入api_key參數\n"
                "3. 在.env文件中設置：QWEN_API_KEY=your-api-key"
            )
        
        self.api_key = api_key
        self.timeout = timeout
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature
        
        logger.info(
            "Qwen Provider 初始化成功",
            extra={
                "model_name": self.model_name,
                "api_base_url": self.api_base_url,
                "default_max_tokens": self.default_max_tokens,
                "default_temperature": self.default_temperature,
            },
        )

    @property
    def provider_type(self) -> ModelProviderType:
        """返回提供商類型"""
        return ModelProviderType.QWEN

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        生成文本（使用非流式 HTTP 請求）
        
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
            raise RuntimeError("Qwen 服務不可用")
        
        try:
            # 構建請求體，使用模型配置中的默认值
            temperature = kwargs.get("temperature", self.default_temperature)
            max_tokens = kwargs.get("max_tokens", self.default_max_tokens)
            
            request_body = {
                "model": self.model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            
            # 發送 HTTP 請求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_base_url,
                    json=request_body,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 解析 Qwen API 響應格式
                    # 響應格式通常為: {"output": {"choices": [{"message": {"content": "..."}}]}}
                    output = data.get("output", {})
                    choices = output.get("choices", [])
                    if choices and len(choices) > 0:
                        message = choices[0].get("message", {})
                        result = message.get("content", "")
                        logger.debug(
                            "Qwen 文本生成成功",
                            extra={
                                "model_name": self.model_name,
                                "prompt_length": len(prompt),
                                "response_length": len(result),
                            },
                        )
                        return result
                    else:
                        error_msg = "Qwen API 響應格式異常：未找到 choices"
                        logger.error(
                            error_msg,
                            extra={
                                "model_name": self.model_name,
                                "response_data": json.dumps(data, ensure_ascii=False)[:500],
                            },
                        )
                        raise RuntimeError(error_msg)
                else:
                    error_msg = f"Qwen API 返回錯誤: {response.status_code}"
                    logger.error(
                        error_msg,
                        extra={
                            "model_name": self.model_name,
                            "api_base_url": self.api_base_url,
                            "status_code": response.status_code,
                            "response_text": response.text[:500],
                        },
                    )
                    raise RuntimeError(error_msg)
                    
        except httpx.TimeoutException as e:
            logger.error(
                f"Qwen 文本生成超時（{self.timeout}秒）",
                extra={
                    "model_name": self.model_name,
                    "api_base_url": self.api_base_url,
                    "timeout": self.timeout,
                },
            )
            raise RuntimeError(f"Qwen 文本生成超時（{self.timeout}秒）") from e
        except Exception as e:
            logger.error(
                f"Qwen 文本生成失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "api_base_url": self.api_base_url,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"Qwen 文本生成失敗: {e}") from e

    async def check_available(self) -> bool:
        """
        檢查 Qwen 服務是否可用
        
        通過發送一個簡單的測試請求來檢查 API 可用性
        
        Returns:
            True 如果 Qwen 可用，False 否則
        """
        try:
            # 發送一個簡單的測試請求
            test_request_body = {
                "model": self.model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "test"
                        }
                    ]
                },
                "parameters": {
                    "temperature": 0.0,
                    "max_tokens": 10
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.api_base_url,
                    json=test_request_body,
                    headers=headers
                )
                # 如果返回 200 或 401（認證錯誤但服務可用），則認為服務可用
                # 401 表示 API Key 可能無效，但服務本身是可用的
                return response.status_code in [200, 401]
        except Exception as e:
            logger.warning(
                f"Qwen 服務不可用: {e}",
                extra={"api_base_url": self.api_base_url, "error": str(e)},
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
            "api_base_url": self.api_base_url,
            "timeout": self.timeout,
        }

