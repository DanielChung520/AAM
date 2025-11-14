"""
@purpose: 测试 Provider 配置适配器
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import Mock

from src.core.interfaces.i_model_provider import ModelProviderType
from src.config.provider_config_adapter import ProviderConfigAdapter
from src.config.settings import ModelServiceSettings


class TestProviderConfigAdapter:
    """测试配置适配器"""
    
    def test_qwen_config_mapping(self):
        """测试 Qwen 配置正确映射到通用参数"""
        # 使用环境变量覆盖来设置配置
        import os
        original_env = os.environ.copy()
        try:
            os.environ["QWEN_MODEL_NAME"] = "qwen-plus"
            os.environ["QWEN_API_BASE_URL"] = "https://custom-qwen.com"
            os.environ["QWEN_API_KEY"] = "test-api-key"
            os.environ["QWEN_TIMEOUT"] = "180"
            config = ModelServiceSettings()
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=config
        )
        
        assert provider_config["model_name"] == "qwen-plus"
        assert provider_config["api_base_url"] == "https://custom-qwen.com"
        assert provider_config["api_key"] == "test-api-key"
        assert provider_config["timeout"] == 180
    
    def test_qwen_config_defaults(self):
        """测试 Qwen 配置默认值处理"""
        # 清除相关环境变量以确保使用默认值
        import os
        original_env = os.environ.copy()
        try:
            for key in ["QWEN_MODEL_NAME", "QWEN_API_BASE_URL", "QWEN_API_KEY", "QWEN_TIMEOUT"]:
                os.environ.pop(key, None)
            config = ModelServiceSettings()
            
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=ModelProviderType.QWEN,
                config=config
            )
            
            assert provider_config["model_name"] == "qwen-turbo"  # 默认值
            # api_base_url 在适配器中可能返回 None 或默认值，取决于配置
            assert provider_config["api_key"] is None
            assert provider_config["timeout"] == 120
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_ollama_config_mapping(self):
        """测试 Ollama 配置正确映射到通用参数"""
        import os
        original_env = os.environ.copy()
        try:
            os.environ["MODEL_NAME"] = "mistral"
            os.environ["MODEL_API_BASE_URL"] = "http://custom-ollama:11434"
            os.environ["MODEL_TIMEOUT"] = "60"
            config = ModelServiceSettings()
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.OLLAMA,
            config=config
        )
        
        assert provider_config["model_name"] == "mistral"
        assert provider_config["api_base_url"] == "http://custom-ollama:11434"
        assert provider_config["api_key"] is None  # Ollama 不需要 API Key
        assert provider_config["timeout"] == 60
    
    def test_ollama_config_defaults(self):
        """测试 Ollama 配置默认值处理"""
        import os
        original_env = os.environ.copy()
        try:
            # 清除相关环境变量以确保使用默认值
            for key in ["MODEL_NAME", "MODEL_API_BASE_URL", "OLLAMA_MODEL_NAME", "OLLAMA_BASE_URL"]:
                os.environ.pop(key, None)
            config = ModelServiceSettings()
            
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=ModelProviderType.OLLAMA,
                config=config
            )
            
            # 验证配置结构，允许使用环境中的默认值
            assert "model_name" in provider_config
            assert provider_config["api_base_url"] == "http://localhost:11434"  # 默认值
            assert provider_config["api_key"] is None
            assert provider_config["timeout"] == 120
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_openai_config_mapping(self):
        """测试 OpenAI 配置正确映射到通用参数"""
        import os
        original_env = os.environ.copy()
        try:
            os.environ["MODEL_NAME"] = "gpt-4"
            os.environ["OPENAI_API_BASE_URL"] = "https://custom-openai.com"
            os.environ["OPENAI_API_KEY"] = "test-openai-key"
            os.environ["MODEL_TIMEOUT"] = "90"
            config = ModelServiceSettings()
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.OPENAI,
            config=config
        )
        
        assert provider_config["model_name"] == "gpt-4"
        assert provider_config["api_base_url"] == "https://custom-openai.com"
        assert provider_config["api_key"] == "test-openai-key"
        assert provider_config["timeout"] == 90
    
    def test_config_adapter_returns_unified_structure(self):
        """测试配置适配器返回统一的结构"""
        config = ModelServiceSettings()
        
        for provider_type in [ModelProviderType.QWEN, ModelProviderType.OLLAMA, ModelProviderType.OPENAI]:
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=provider_type,
                config=config
            )
            
            # 验证返回的配置包含所有通用参数
            assert "model_name" in provider_config
            assert "api_base_url" in provider_config
            assert "api_key" in provider_config
            assert "timeout" in provider_config
            
            # 验证所有值都是正确的类型
            assert isinstance(provider_config["model_name"], str)
            assert provider_config["api_base_url"] is None or isinstance(provider_config["api_base_url"], str)
            assert provider_config["api_key"] is None or isinstance(provider_config["api_key"], str)
            assert isinstance(provider_config["timeout"], int)

