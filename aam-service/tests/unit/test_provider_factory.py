"""
@purpose: Provider 工廠單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import patch, MagicMock

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider
from src.infrastructure.ai.providers.qwen_provider import QwenProvider


class TestModelProviderFactory:
    """Provider 工廠測試類"""

    def test_create_ollama_provider(self):
        """測試創建 Ollama Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",
                timeout=120,
            )
            
            assert isinstance(provider, OllamaProvider)
            assert provider.model_name == "llama3"
            assert provider.base_url == "http://localhost:11434"
            assert provider.timeout == 120

    def test_create_ollama_provider_with_kwargs(self):
        """測試創建 Ollama Provider（帶額外參數）"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",
                timeout=120,
                ollama_base_url="http://custom:11434",
                ollama_timeout=60,
            )
            
            assert isinstance(provider, OllamaProvider)
            assert provider.base_url == "http://custom:11434"
            assert provider.timeout == 60

    def test_create_vllm_provider_not_implemented(self):
        """測試創建 vLLM Provider（未實現）"""
        with pytest.raises(ValueError, match="尚未實現"):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.VLLM,
                model_name="test-model",
            )

    def test_create_openai_provider_not_implemented(self):
        """測試創建 OpenAI Provider（未實現）"""
        with pytest.raises(ValueError, match="尚未實現"):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OPENAI,
                model_name="gpt-3.5-turbo",
            )

    def test_create_provider_from_config(self):
        """測試從配置字典創建 Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            config = {
                "provider_type": "ollama",
                "model_name": "llama3",
                "api_base_url": "http://localhost:11434",
                "timeout": 120,
            }
            
            provider = ModelProviderFactory.create_provider_from_config(config)
            
            assert isinstance(provider, OllamaProvider)

    def test_create_provider_from_config_missing_provider_type(self):
        """測試從配置字典創建 Provider（缺少 provider_type）"""
        config = {
            "model_name": "llama3",
        }
        
        with pytest.raises(ValueError, match="缺少 provider_type"):
            ModelProviderFactory.create_provider_from_config(config)

    def test_create_provider_from_config_missing_model_name(self):
        """測試從配置字典創建 Provider（缺少 model_name）"""
        config = {
            "provider_type": "ollama",
        }
        
        with pytest.raises(ValueError, match="缺少 model_name"):
            ModelProviderFactory.create_provider_from_config(config)

    def test_create_provider_from_config_invalid_provider_type(self):
        """測試從配置字典創建 Provider（無效的 provider_type）"""
        config = {
            "provider_type": "invalid",
            "model_name": "llama3",
        }
        
        with pytest.raises(ValueError, match="無效的 provider_type"):
            ModelProviderFactory.create_provider_from_config(config)

    def test_create_qwen_provider(self):
        """測試創建 Qwen Provider"""
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
            timeout=120,
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.model_name == "qwen-turbo"
        assert provider.api_base_url == "https://test.com/api"
        assert provider.api_key == "test-key"
        assert provider.timeout == 120

    def test_create_qwen_provider_with_kwargs(self):
        """測試創建 Qwen Provider（帶額外參數）"""
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
            timeout=120,
            qwen_api_base_url="https://custom.com/api",
            qwen_api_key="custom-key",
            qwen_timeout=60,
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.api_base_url == "https://custom.com/api"
        assert provider.api_key == "custom-key"
        assert provider.timeout == 60

    def test_create_qwen_provider_from_config(self):
        """測試從配置字典創建 Qwen Provider"""
        config = {
            "provider_type": "qwen",
            "model_name": "qwen-turbo",
            "api_base_url": "https://test.com/api",
            "api_key": "test-key",
            "timeout": 120,
        }
        
        provider = ModelProviderFactory.create_provider_from_config(config)
        
        assert isinstance(provider, QwenProvider)

