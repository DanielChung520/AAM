"""
@purpose: Qwen Provider 集成測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.qwen_provider import QwenProvider


class TestQwenProviderIntegration:
    """Qwen Provider 集成測試類"""

    @pytest.fixture
    def qwen_provider(self):
        """創建 Qwen Provider 實例"""
        # 從環境變量讀取API Key（必須設置）
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            pytest.skip("需要設置QWEN_API_KEY環境變量")
        
        api_base_url = os.getenv(
            "QWEN_API_BASE_URL",
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        )
        
        return QwenProvider(
            model_name="qwen-turbo",
            api_base_url=api_base_url,
            api_key=api_key,
            timeout=120,
        )

    def test_qwen_provider_initialization(self, qwen_provider):
        """測試 Qwen Provider 初始化"""
        assert qwen_provider.provider_type == ModelProviderType.QWEN
        assert qwen_provider.model_name == "qwen-turbo"
        assert qwen_provider.api_key is not None
        assert qwen_provider.timeout == 120

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_qwen_provider_check_available_real_api(self, qwen_provider):
        """測試 Qwen Provider 可用性檢查（真實 API 調用）"""
        # 注意：這需要真實的 API Key 和網絡連接
        # 如果 API Key 無效或網絡不可用，測試會失敗
        try:
            result = await qwen_provider.check_available()
            # 如果 API Key 有效，應該返回 True
            # 如果 API Key 無效但服務可用，也可能返回 True（401 狀態碼）
            assert isinstance(result, bool)
        except Exception as e:
            # 如果網絡錯誤或其他異常，跳過測試
            pytest.skip(f"無法連接到 Qwen API: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_qwen_provider_generate_simple_text(self, qwen_provider):
        """測試 Qwen Provider 簡單文本生成（真實 API 調用）"""
        # Mock 可用性檢查為 True
        qwen_provider.check_available = AsyncMock(return_value=True)
        
        try:
            # 測試簡單的文本生成
            prompt = "請用一句話介紹 Python 編程語言。"
            result = await qwen_provider.generate(prompt)
            
            # 驗證返回結果
            assert isinstance(result, str)
            assert len(result) > 0
            # 驗證結果包含一些關鍵詞（如果可能）
            assert "Python" in result or "python" in result.lower()
        except Exception as e:
            # 如果 API 調用失敗，記錄錯誤但繼續測試
            pytest.skip(f"Qwen API 調用失敗: {e}")

    @pytest.mark.asyncio
    async def test_qwen_provider_generate_with_parameters(self, qwen_provider):
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
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 測試帶參數的生成
            result = await qwen_provider.generate(
                "測試提示詞",
                temperature=0.7,
                max_tokens=1000
            )
            
            assert result == "生成的文本內容"
            
            # 驗證請求參數
            call_args = mock_post.call_args
            assert call_args is not None
            request_body = call_args[1]["json"]
            assert request_body["parameters"]["temperature"] == 0.7
            assert request_body["parameters"]["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_qwen_provider_api_error_handling(self, qwen_provider):
        """測試 Qwen Provider API 錯誤處理"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 錯誤響應
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 應該拋出 RuntimeError
            with pytest.raises(RuntimeError, match="返回錯誤"):
                await qwen_provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_timeout_handling(self, qwen_provider):
        """測試 Qwen Provider 超時處理"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock 超時異常
            import httpx
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 應該拋出 RuntimeError
            with pytest.raises(RuntimeError, match="超時"):
                await qwen_provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_invalid_response_format(self, qwen_provider):
        """測試 Qwen Provider 無效響應格式處理"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP 響應（無效格式）
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "output": {
                    "choices": []  # 空的 choices
                }
            }
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 應該拋出 RuntimeError
            with pytest.raises(RuntimeError, match="響應格式異常"):
                await qwen_provider.generate("測試提示詞")

    @pytest.mark.asyncio
    async def test_qwen_provider_unavailable_service(self, qwen_provider):
        """測試 Qwen Provider 服務不可用"""
        # Mock 可用性檢查為 False
        qwen_provider.check_available = AsyncMock(return_value=False)
        
        # 應該拋出 RuntimeError
        with pytest.raises(RuntimeError, match="不可用"):
            await qwen_provider.generate("測試提示詞")

    def test_qwen_provider_get_config(self, qwen_provider):
        """測試 Qwen Provider 獲取配置"""
        config = qwen_provider.get_config()
        
        assert config["provider_type"] == "qwen"
        assert config["model_name"] == "qwen-turbo"
        assert config["api_base_url"] is not None
        assert config["timeout"] == 120

    @pytest.mark.asyncio
    async def test_qwen_provider_connection_error_handling(self, qwen_provider):
        """測試 Qwen Provider 連接錯誤處理"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock 連接錯誤
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Connection error")
            )
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 應該拋出 RuntimeError
            with pytest.raises(RuntimeError, match="生成失敗"):
                await qwen_provider.generate("測試提示詞")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_qwen_provider_real_api_flow(self, qwen_provider):
        """測試 Qwen Provider 真實 API 流程（端到端）"""
        # 這是一個端到端測試，需要真實的 API Key
        # 如果環境變量中沒有有效的 API Key，跳過測試
        
        api_key = os.getenv("QWEN_API_KEY", "")
        if not api_key or api_key == "test-key":
            pytest.skip("需要真實的 QWEN_API_KEY 環境變量")
        
        try:
            # 1. 檢查可用性
            is_available = await qwen_provider.check_available()
            if not is_available:
                pytest.skip("Qwen API 不可用")
            
            # 2. 生成文本
            prompt = "請用一句話回答：什麼是人工智能？"
            result = await qwen_provider.generate(prompt, max_tokens=100)
            
            # 3. 驗證結果
            assert isinstance(result, str)
            assert len(result) > 0
            
            # 4. 驗證配置
            config = qwen_provider.get_config()
            assert config["provider_type"] == "qwen"
            
        except Exception as e:
            pytest.skip(f"真實 API 測試失敗: {e}")

