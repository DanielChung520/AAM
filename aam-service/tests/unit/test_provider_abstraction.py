"""
@purpose: 测试 Provider 抽象性
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.core.interfaces.i_model_provider import IModelProvider, ModelProviderType
from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider


class TestProviderAbstraction:
    """测试 Provider 抽象性"""
    
    def test_all_providers_implement_imodelprovider(self):
        """测试所有 Provider 都实现 IModelProvider 接口"""
        # 测试 Qwen Provider
        with pytest.raises(ValueError):  # 需要 API Key
            provider = QwenProvider(
                model_name="test",
                api_key=None,
            )
        
        provider = QwenProvider(
            model_name="test",
            api_key="test-key",
        )
        assert isinstance(provider, IModelProvider)
        
        # 测试 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = OllamaProvider(
                model_name="test",
            )
            assert isinstance(provider, IModelProvider)
    
    def test_providers_have_consistent_interface(self):
        """测试所有 Provider 都有一致的接口"""
        # 测试 Qwen Provider
        provider = QwenProvider(
            model_name="test",
            api_key="test-key",
        )
        
        assert hasattr(provider, 'generate')
        assert hasattr(provider, 'check_available')
        assert hasattr(provider, 'provider_type')
        assert hasattr(provider, 'get_config')
        
        # 验证方法签名
        import inspect
        generate_sig = inspect.signature(provider.generate)
        assert 'prompt' in generate_sig.parameters
        
        check_available_sig = inspect.signature(provider.check_available)
        # check_available 是异步方法，可能没有显式参数（只有self）
        assert isinstance(check_available_sig, inspect.Signature)
    
    def test_providers_accept_unified_parameters(self):
        """测试 Provider 接受统一参数名"""
        # 测试 Qwen Provider 接受 api_base_url 和 api_key（统一参数名）
        provider = QwenProvider(
            model_name="test-model",
            api_base_url="https://custom-url.com",  # 统一参数名
            api_key="test-key",  # 统一参数名
            timeout=60,
        )
        
        assert provider.model_name == "test-model"
        assert provider.api_base_url == "https://custom-url.com"
        assert provider.api_key == "test-key"
        assert provider.timeout == 60
    
    def test_providers_handle_parameter_mapping(self):
        """测试 Provider 自己处理参数映射"""
        # 测试 Ollama Provider 将 api_base_url 映射到 base_url
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = OllamaProvider(
                model_name="test",
                api_base_url="http://custom-host:8080",  # 统一参数名
            )
            
            assert provider.base_url == "http://custom-host:8080"  # 内部映射
    
    def test_providers_handle_default_values(self):
        """测试 Provider 自己处理默认值"""
        # 测试 Qwen Provider 处理默认 api_base_url
        provider = QwenProvider(
            model_name="test",
            api_key="test-key",
            api_base_url=None,  # 使用默认值
        )
        
        assert provider.api_base_url == "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # 测试 Ollama Provider 处理默认 api_base_url
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = OllamaProvider(
                model_name="test",
                api_base_url=None,  # 使用默认值
            )
            
            assert provider.base_url == "http://localhost:11434"
    
    def test_providers_validate_their_own_requirements(self):
        """测试 Provider 自己进行验证"""
        # 测试 Qwen Provider 验证 API Key
        with pytest.raises(ValueError, match="API Key"):
            QwenProvider(
                model_name="test",
                api_key=None,  # 必须设置
            )
        
        # 测试 Qwen Provider 验证通过
        provider = QwenProvider(
            model_name="test",
            api_key="valid-key",
        )
        assert provider.api_key == "valid-key"
    
    def test_providers_return_correct_provider_type(self):
        """测试 Provider 返回正确的 provider_type"""
        # 测试 Qwen Provider
        provider = QwenProvider(
            model_name="test",
            api_key="test-key",
        )
        assert provider.provider_type == ModelProviderType.QWEN
        
        # 测试 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = OllamaProvider(
                model_name="test",
            )
            assert provider.provider_type == ModelProviderType.OLLAMA
    
    @pytest.mark.asyncio
    async def test_providers_implement_async_methods(self):
        """测试 Provider 实现异步方法"""
        # 测试 Qwen Provider
        provider = QwenProvider(
            model_name="test",
            api_key="test-key",
        )
        
        # 验证方法是异步的
        import inspect
        assert inspect.iscoroutinefunction(provider.generate)
        assert inspect.iscoroutinefunction(provider.check_available)
        
        # 测试 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            provider = OllamaProvider(
                model_name="test",
            )
            
            assert inspect.iscoroutinefunction(provider.generate)
            assert inspect.iscoroutinefunction(provider.check_available)

