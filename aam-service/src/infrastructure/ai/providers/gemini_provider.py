"""
@purpose: Gemini 模型服務提供商實現，封裝 Google Gemini API 調用
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


class GeminiProvider(IModelProvider):
    """
    Gemini 模型服務提供商
    
    封裝 Google Gemini API 的調用，提供統一的接口
    """

    def __init__(
        self,
        model_name: str = "gemini-pro",
        api_base_url: Optional[str] = None,  # 接受通用参数名
        api_key: Optional[str] = None,  # 接受通用参数名
        timeout: int = 120,
        max_tokens: int = 8192,  # 从模型配置获取的默认值
        temperature: float = 0.5,  # 从模型配置获取的默认值
    ):
        """
        初始化 Gemini Provider
        
        接受通用参数名，Provider自己处理默认值和验证。
        
        Args:
            model_name: Gemini 模型名稱（如 gemini-pro, gemini-pro-vision 等）
            api_base_url: API 基礎 URL（統一參數名，可選，Provider自己處理默認值）
            api_key: API 密鑰（統一參數名，必須設置，Provider自己驗證）
            timeout: 請求超時時間（秒）
            
        Raises:
            ValueError: 當api_key未設置時
        """
        # 处理模型名称：如果只提供了模型名（如 "gemini-pro"），需要转换为完整路径（如 "models/gemini-pro-latest"）
        if not model_name.startswith("models/"):
            # 映射常见的模型名称到完整路径
            model_mapping = {
                "gemini-pro": "gemini-pro-latest",
                "gemini-flash": "gemini-2.5-flash",
                "gemini-2.5-pro": "gemini-2.5-pro",
                "gemini-2.5-flash": "gemini-2.5-flash",
            }
            mapped_name = model_mapping.get(model_name, model_name)
            self.model_name = f"models/{mapped_name}"
        else:
            self.model_name = model_name
        
        # Provider自己处理默认值
        self.api_base_url = api_base_url or "https://generativelanguage.googleapis.com/v1beta"
        
        # Provider自己验证
        if not api_key:
            raise ValueError(
                "API Key必須設置。請通過以下方式之一設置：\n"
                "1. 環境變量 GEMINI_API_KEY（推薦）\n"
                "2. 創建Provider時傳入api_key參數\n"
                "3. 在.env文件中設置：GEMINI_API_KEY=your-api-key"
            )
        
        self.api_key = api_key
        self.timeout = timeout
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature
        
        logger.info(
            "Gemini Provider 初始化成功",
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
        return ModelProviderType.GEMINI

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
        # 檢查服務是否可用（可選，如果失敗則繼續嘗試生成）
        # 暫時跳過檢查，直接嘗試生成以提高性能
        # if not await self.check_available():
        #     raise RuntimeError("Gemini 服務不可用")
        
        try:
            # 構建請求體，使用模型配置中的默认值
            temperature = kwargs.get("temperature", self.default_temperature)
            max_output_tokens = kwargs.get("max_tokens", self.default_max_tokens)
            
            # Gemini API 請求格式
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens
                }
            }
            
            # 構建完整的 API URL（包含 API key 作為查詢參數）
            # model_name 已經包含 "models/" 前綴，所以直接使用
            api_url = f"{self.api_base_url}/{self.model_name}:generateContent?key={self.api_key}"
            
            # 發送 HTTP 請求
            headers = {
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    api_url,
                    json=request_body,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 解析 Gemini API 響應格式
                    # 響應格式通常為: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
                    candidates = data.get("candidates", [])
                    if candidates and len(candidates) > 0:
                        candidate = candidates[0]
                        # 检查是否有 finishReason 为 SAFETY（安全过滤）
                        finish_reason = candidate.get("finishReason", "")
                        if finish_reason == "SAFETY":
                            error_msg = "Gemini API 響應被安全過濾器阻止"
                            logger.warning(
                                error_msg,
                                extra={
                                    "model_name": self.model_name,
                                    "finish_reason": finish_reason,
                                },
                            )
                            raise RuntimeError(error_msg)
                        
                        content = candidate.get("content", {})
                        if not content:
                            error_msg = "Gemini API 響應格式異常：candidate 中未找到 content"
                            logger.error(
                                error_msg,
                                extra={
                                    "model_name": self.model_name,
                                    "candidate": json.dumps(candidate, ensure_ascii=False)[:500],
                                },
                            )
                            raise RuntimeError(error_msg)
                        
                        parts = content.get("parts", [])
                        # 处理 finishReason 为 MAX_TOKENS 的情况（响应被截断，但仍可能有部分内容）
                        if not parts or len(parts) == 0:
                            if finish_reason == "MAX_TOKENS":
                                error_msg = f"Gemini API 響應達到最大 token 數限制（{max_output_tokens}），且未返回任何內容。請增加 max_tokens 參數"
                                logger.warning(
                                    error_msg,
                                    extra={
                                        "model_name": self.model_name,
                                        "finish_reason": finish_reason,
                                        "max_output_tokens": max_output_tokens,
                                    },
                                )
                                raise RuntimeError(error_msg)
                            else:
                                error_msg = "Gemini API 響應格式異常：未找到 parts"
                                logger.error(
                                    error_msg,
                                    extra={
                                        "model_name": self.model_name,
                                        "finish_reason": finish_reason,
                                        "content": json.dumps(content, ensure_ascii=False)[:500],
                                    },
                                )
                                raise RuntimeError(error_msg)
                        
                        if parts and len(parts) > 0:
                            # 获取第一个 part 的 text
                            result = parts[0].get("text", "")
                            if not result:
                                # 如果 text 为空，尝试其他字段
                                result = str(parts[0])
                            logger.debug(
                                "Gemini 文本生成成功",
                                extra={
                                    "model_name": self.model_name,
                                    "prompt_length": len(prompt),
                                    "response_length": len(result),
                                },
                            )
                            return result
                        else:
                            # 如果 parts 为空，记录详细信息以便调试
                            error_msg = "Gemini API 響應格式異常：未找到 parts"
                            logger.error(
                                error_msg,
                                extra={
                                    "model_name": self.model_name,
                                    "candidate": json.dumps(candidate, ensure_ascii=False)[:500],
                                    "response_data": json.dumps(data, ensure_ascii=False)[:500],
                                },
                            )
                            raise RuntimeError(error_msg)
                    else:
                        error_msg = "Gemini API 響應格式異常：未找到 candidates"
                        logger.error(
                            error_msg,
                            extra={
                                "model_name": self.model_name,
                                "response_data": json.dumps(data, ensure_ascii=False)[:500],
                            },
                        )
                        raise RuntimeError(error_msg)
                else:
                    error_msg = f"Gemini API 返回錯誤: {response.status_code}"
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
                f"Gemini 文本生成超時（{self.timeout}秒）",
                extra={
                    "model_name": self.model_name,
                    "api_base_url": self.api_base_url,
                    "timeout": self.timeout,
                },
            )
            raise RuntimeError(f"Gemini 文本生成超時（{self.timeout}秒）") from e
        except Exception as e:
            logger.error(
                f"Gemini 文本生成失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "api_base_url": self.api_base_url,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"Gemini 文本生成失敗: {e}") from e

    async def check_available(self) -> bool:
        """
        檢查 Gemini 服務是否可用
        
        通過發送一個簡單的測試請求來檢查 API 可用性
        
        Returns:
            True 如果 Gemini 可用，False 否則
        """
        try:
            # 發送一個簡單的測試請求
            test_request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "test"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": 10
                }
            }
            
            # model_name 已經包含 "models/" 前綴，所以直接使用
            api_url = f"{self.api_base_url}/{self.model_name}:generateContent?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    api_url,
                    json=test_request_body,
                    headers=headers
                )
                # 如果返回 200 或 401（認證錯誤但服務可用），則認為服務可用
                # 401 表示 API Key 可能無效，但服務本身是可用的
                return response.status_code in [200, 401]
        except Exception as e:
            logger.warning(
                f"Gemini 服務不可用: {e}",
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

