"""
@purpose: 模型服務提供商接口單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider


class TestIModelProvider:
    """模型服務提供商接口測試類"""

    def test_ollama_provider_type(self):
        """測試 Ollama Provider 類型"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
            )
            
            assert provider.provider_type == ModelProviderType.OLLAMA

    @pytest.mark.asyncio
    async def test_ollama_provider_check_available_success(self):
        """測試 Ollama Provider 可用性檢查（成功）"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama, \
             patch('httpx.AsyncClient') as mock_client:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            # Mock HTTP 響應
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
            )
            
            result = await provider.check_available()
            assert result is True

    @pytest.mark.asyncio
    async def test_ollama_provider_check_available_failure(self):
        """測試 Ollama Provider 可用性檢查（失敗）"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama, \
             patch('httpx.AsyncClient') as mock_client:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            # Mock HTTP 異常
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Connection error"))
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
            )
            
            result = await provider.check_available()
            assert result is False

    @pytest.mark.asyncio
    async def test_ollama_provider_generate_success(self):
        """測試 Ollama Provider 文本生成（成功）"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama_instance.ainvoke = AsyncMock(return_value="生成的文本")
            mock_ollama.return_value = mock_ollama_instance
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
            )
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            result = await provider.generate("測試提示詞")
            assert result == "生成的文本"

    @pytest.mark.asyncio
    async def test_ollama_provider_generate_unavailable(self):
        """測試 Ollama Provider 文本生成（服務不可用）"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
            )
            
            # Mock 可用性檢查失敗
            provider.check_available = AsyncMock(return_value=False)
            
            with pytest.raises(RuntimeError, match="不可用"):
                await provider.generate("測試提示詞")

    def test_ollama_provider_get_config(self):
        """測試 Ollama Provider 獲取配置"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider = OllamaProvider(
                model_name="llama3",
                base_url="http://localhost:11434",
                timeout=120,
            )
            
            config = provider.get_config()
            assert config["provider_type"] == "ollama"
            assert config["model_name"] == "llama3"
            assert config["base_url"] == "http://localhost:11434"
            assert config["timeout"] == 120

