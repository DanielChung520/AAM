"""
@purpose: Qwen Provider 單元測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.qwen_provider import QwenProvider


class TestQwenProvider:
    """Qwen Provider 測試類"""

    def test_qwen_provider_type(self):
        """測試 Qwen Provider 類型"""
        provider = QwenProvider(
            model_name="qwen-turbo",
            api_base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            api_key="test-key",
        )
        
        assert provider.provider_type == ModelProviderType.QWEN

    def test_qwen_provider_initialization(self):
        """測試 Qwen Provider 初始化"""
        provider = QwenProvider(
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
            timeout=60,
        )
        
        assert provider.model_name == "qwen-turbo"
        assert provider.api_base_url == "https://test.com/api"
        assert provider.api_key == "test-key"
        assert provider.timeout == 60

    @pytest.mark.asyncio
    async def test_qwen_provider_check_available_success(self):
        """測試 Qwen Provider 可用性檢查（成功）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": "test"
                            }
                        }
                    ]
                }
            }
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            result = await provider.check_available()
            assert result is True

    @pytest.mark.asyncio
    async def test_qwen_provider_check_available_unauthorized(self):
        """測試 Qwen Provider 可用性檢查（401，服務可用但認證失敗）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應（401 表示服務可用但認證失敗）
            mock_response = MagicMock()
            mock_response.status_code = 401
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            result = await provider.check_available()
            # 401 表示服務可用，只是認證失敗
            assert result is True

    @pytest.mark.asyncio
    async def test_qwen_provider_check_available_failure(self):
        """測試 Qwen Provider 可用性檢查（失敗）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 異常
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Connection error")
            )
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            result = await provider.check_available()
            assert result is False

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_success(self):
        """測試 Qwen Provider 文本生成（成功）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": "生成的文本內容"
                            }
                        }
                    ]
                }
            }
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            result = await provider.generate("測試提示詞")
            assert result == "生成的文本內容"

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_with_parameters(self):
        """測試 Qwen Provider 文本生成（帶參數）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": "生成的文本內容"
                            }
                        }
                    ]
                }
            }
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            result = await provider.generate("測試提示詞", temperature=0.7, max_tokens=1000)
            assert result == "生成的文本內容"
            
            # 驗證請求參數
            call_args = mock_post.call_args
            assert call_args is not None
            request_body = call_args[1]["json"]
            assert request_body["parameters"]["temperature"] == 0.7
            assert request_body["parameters"]["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_unavailable(self):
        """測試 Qwen Provider 文本生成（服務不可用）"""
        provider = QwenProvider(
            model_name="qwen-turbo",
            api_key="test-key",
        )
        
        # Mock 可用性檢查失敗
        provider.check_available = AsyncMock(return_value=False)
        
        with pytest.raises(RuntimeError, match="不可用"):
            await provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_api_error(self):
        """測試 Qwen Provider 文本生成（API 錯誤）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應（錯誤狀態碼）
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            with pytest.raises(RuntimeError, match="返回錯誤"):
                await provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_timeout(self):
        """測試 Qwen Provider 文本生成（超時）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock 超時異常
            import httpx
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
                timeout=120,
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            with pytest.raises(RuntimeError, match="超時"):
                await provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_invalid_response_format(self):
        """測試 Qwen Provider 文本生成（無效響應格式）"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應（無效格式）
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "choices": []
                }
            }
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            provider = QwenProvider(
                model_name="qwen-turbo",
                api_key="test-key",
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            with pytest.raises(RuntimeError, match="響應格式異常"):
                await provider.generate("測試提示詞")

    def test_qwen_provider_get_config(self):
        """測試 Qwen Provider 獲取配置"""
        provider = QwenProvider(
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
            timeout=120,
        )
        
        config = provider.get_config()
        assert config["provider_type"] == "qwen"
        assert config["model_name"] == "qwen-turbo"
        assert config["api_base_url"] == "https://test.com/api"
        assert config["timeout"] == 120

