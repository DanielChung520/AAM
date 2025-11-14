"""
@purpose: 测试 Provider Factory 的抽象性
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import Mock, patch

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider


class TestProviderFactoryAbstraction:
    """测试 Factory 抽象性"""
    
    def test_factory_uses_unified_parameter_names(self):
        """测试 Factory 只使用统一参数名，不包含 Provider 特定参数名"""
        # 检查 Factory 代码中不包含 Provider 特定参数名
        factory_code = open("src/infrastructure/ai/providers/provider_factory.py").read()
        
        # 不应该包含这些 Provider 特定参数名
        provider_specific_params = [
            "qwen_api_key",
            "qwen_api_base_url",
            "qwen_timeout",
            "ollama_base_url",
            "ollama_timeout",
        ]
        
        for param in provider_specific_params:
            assert param not in factory_code, f"Factory 代码中不应包含 Provider 特定参数: {param}"
    
    def test_factory_no_provider_specific_validation(self):
        """测试 Factory 不包含 Provider 特定的验证逻辑"""
        factory_code = open("src/infrastructure/ai/providers/provider_factory.py").read()
        
        # 不应该包含 Provider 特定的验证逻辑
        provider_specific_validation = [
            "Qwen API Key",
            "QWEN_API_KEY",
        ]
        
        for validation in provider_specific_validation:
            # 允许在注释或文档字符串中出现，但不应该在代码逻辑中出现
            # 这里只检查是否在 raise ValueError 中出现
            if f'raise ValueError' in factory_code and validation in factory_code:
                # 检查是否在 raise 语句中
                lines = factory_code.split('\n')
                for i, line in enumerate(lines):
                    if 'raise ValueError' in line:
                        # 检查接下来的几行是否包含 Provider 特定验证
                        context = '\n'.join(lines[i:i+5])
                        if validation in context:
                            pytest.fail(f"Factory 代码中不应包含 Provider 特定验证: {validation}")
    
    def test_factory_creates_providers_with_unified_params(self):
        """测试 Factory 使用统一参数创建不同 Provider"""
        # 测试创建 Qwen Provider（需要 API Key）
        with pytest.raises(ValueError, match="API Key"):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                model_name="qwen-turbo",
                api_base_url="https://test.com",
                api_key=None,  # 统一参数名
                timeout=120,
            )
        
        # 测试创建 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",  # 统一参数名
                timeout=120,
            )
            assert isinstance(provider, OllamaProvider)
            assert provider.model_name == "llama3"
    
    def test_factory_passes_unified_params_to_providers(self):
        """测试 Factory 正确传递统一参数给 Provider"""
        # 测试 Qwen Provider 接收统一参数
        with pytest.raises(ValueError) as exc_info:
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                model_name="test-model",
                api_base_url="https://custom-url.com",
                api_key=None,
                timeout=60,
            )
        
        # 验证错误信息来自 Provider，不是 Factory
        assert "API Key" in str(exc_info.value)
        
        # 测试 Ollama Provider 接收统一参数
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="custom-model",
                api_base_url="http://custom-host:8080",
                timeout=90,
            )
            assert provider.model_name == "custom-model"
            assert provider.base_url == "http://custom-host:8080"
            assert provider.timeout == 90
    
    def test_factory_returns_imodelprovider_interface(self):
        """测试 Factory 创建的 Provider 都实现 IModelProvider 接口"""
        # 测试 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",
            )
            assert isinstance(provider, IModelProvider)
            assert hasattr(provider, 'generate')
            assert hasattr(provider, 'check_available')
            assert hasattr(provider, 'provider_type')
    
    def test_factory_handles_unsupported_provider_type(self):
        """测试 Factory 处理不支持的 Provider 类型"""
        with pytest.raises(ValueError, match="不支持的 Provider 類型"):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.CUSTOM,
                model_name="test",
            )

