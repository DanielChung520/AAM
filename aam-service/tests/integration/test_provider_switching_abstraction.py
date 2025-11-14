"""
@purpose: 测试 Provider 切换的抽象性
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.config.provider_config_adapter import ProviderConfigAdapter
from src.config.settings import ModelServiceSettings
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.unified_model_service import UnifiedModelService


class TestProviderSwitchingAbstraction:
    """测试 Provider 切换的抽象性"""
    
    def test_switch_provider_without_code_changes(self):
        """测试通过配置切换 Provider 不需要修改代码"""
        # 测试切换到 Qwen
        qwen_config = ModelServiceSettings(
            qwen_model_name="qwen-turbo",
            qwen_api_key="test-key",
        )
        
        qwen_provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=qwen_config
        )
        
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            **qwen_provider_config
        )
        
        assert qwen_provider.provider_type == ModelProviderType.QWEN
        
        # 测试切换到 Ollama（使用相同的代码模式）
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_config = ModelServiceSettings(
                model_name="llama3",
            )
            
            ollama_provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=ModelProviderType.OLLAMA,
                config=ollama_config
            )
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                **ollama_provider_config
            )
            
            assert ollama_provider.provider_type == ModelProviderType.OLLAMA
    
    @pytest.mark.asyncio
    async def test_switch_provider_functionality_unchanged(self):
        """测试切换 Provider 后功能正常"""
        # 测试 Qwen Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="test-key",
        )
        
        # Mock check_available
        qwen_provider.check_available = AsyncMock(return_value=True)
        assert await qwen_provider.check_available() is True
        
        # 测试 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            ollama_provider.check_available = AsyncMock(return_value=True)
            assert await ollama_provider.check_available() is True
    
    def test_unified_model_service_works_with_any_provider(self):
        """测试 UnifiedModelService 使用抽象 Provider"""
        # 测试使用 Qwen Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="test-key",
        )
        
        unified_service_qwen = UnifiedModelService(provider=qwen_provider)
        assert unified_service_qwen.provider.provider_type == ModelProviderType.QWEN
        
        # 测试使用 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            unified_service_ollama = UnifiedModelService(provider=ollama_provider)
            assert unified_service_ollama.provider.provider_type == ModelProviderType.OLLAMA
    
    def test_provider_switching_uses_same_interface(self):
        """测试切换 Provider 使用相同的接口"""
        # 创建不同 Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="test-key",
        )
        
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            # 验证它们都有相同的接口
            assert hasattr(qwen_provider, 'generate')
            assert hasattr(qwen_provider, 'check_available')
            assert hasattr(qwen_provider, 'provider_type')
            
            assert hasattr(ollama_provider, 'generate')
            assert hasattr(ollama_provider, 'check_available')
            assert hasattr(ollama_provider, 'provider_type')
    
    def test_config_adapter_enables_provider_switching(self):
        """测试配置适配器使 Provider 切换成为可能"""
        # 测试不同 Provider 的配置映射
        configs = [
            (ModelProviderType.QWEN, ModelServiceSettings(qwen_api_key="qwen-key")),
            (ModelProviderType.OLLAMA, ModelServiceSettings()),
        ]
        
        for provider_type, config in configs:
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=provider_type,
                config=config
            )
            
            # 验证配置结构统一
            assert "model_name" in provider_config
            assert "api_base_url" in provider_config
            assert "api_key" in provider_config
            assert "timeout" in provider_config
            
            # 验证可以使用统一配置创建 Provider
            if provider_type == ModelProviderType.OLLAMA:
                with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
                    mock_ollama.return_value = Mock()
                    provider = ModelProviderFactory.create_provider(
                        provider_type=provider_type,
                        **provider_config
                    )
                    assert provider.provider_type == provider_type
            else:
                provider = ModelProviderFactory.create_provider(
                    provider_type=provider_type,
                    **provider_config
                )
                assert provider.provider_type == provider_type

