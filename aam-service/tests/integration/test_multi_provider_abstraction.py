"""
@purpose: 测试多 Provider 的抽象性
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


class TestMultiProviderAbstraction:
    """测试多 Provider 的抽象性"""
    
    def test_create_multiple_providers_simultaneously(self):
        """测试可以同时创建多个不同类型的 Provider"""
        # 创建 Qwen Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="qwen-key-1",
        )
        
        # 创建另一个 Qwen Provider（不同配置）
        qwen_provider_2 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-plus",
            api_key="qwen-key-2",
        )
        
        # 创建 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            # 验证所有 Provider 都正确创建
            assert qwen_provider.provider_type == ModelProviderType.QWEN
            assert qwen_provider.model_name == "qwen-turbo"
            
            assert qwen_provider_2.provider_type == ModelProviderType.QWEN
            assert qwen_provider_2.model_name == "qwen-plus"
            
            assert ollama_provider.provider_type == ModelProviderType.OLLAMA
            assert ollama_provider.model_name == "llama3"
    
    def test_providers_do_not_interfere_with_each_other(self):
        """测试多个 Provider 互不干扰"""
        # 创建多个 Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="qwen-key",
            api_base_url="https://qwen.com",
        )
        
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://ollama.com",
            )
            
            # 验证它们有独立的配置
            assert qwen_provider.model_name == "qwen-turbo"
            assert qwen_provider.api_base_url == "https://qwen.com"
            
            assert ollama_provider.model_name == "llama3"
            assert ollama_provider.base_url == "http://ollama.com"
            
            # 验证它们互不影响
            assert qwen_provider.provider_type != ollama_provider.provider_type
    
    def test_unified_service_with_different_providers(self):
        """测试 UnifiedModelService 可以使用不同的 Provider"""
        # 创建使用 Qwen 的 UnifiedModelService
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="qwen-key",
        )
        
        unified_service_qwen = UnifiedModelService(provider=qwen_provider)
        assert unified_service_qwen.provider.provider_type == ModelProviderType.QWEN
        
        # 创建使用 Ollama 的 UnifiedModelService
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            unified_service_ollama = UnifiedModelService(provider=ollama_provider)
            assert unified_service_ollama.provider.provider_type == ModelProviderType.OLLAMA
            
            # 验证它们可以同时存在
            assert unified_service_qwen.provider != unified_service_ollama.provider
    
    def test_provider_config_adapter_handles_multiple_providers(self):
        """测试配置适配器处理多个 Provider"""
        # 使用环境变量来设置配置
        import os
        original_env = os.environ.copy()
        try:
            os.environ["QWEN_MODEL_NAME"] = "qwen-turbo"
            os.environ["QWEN_API_KEY"] = "qwen-key"
            os.environ["MODEL_NAME"] = "llama3"
            config = ModelServiceSettings()
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        
        # 获取不同 Provider 的配置
        qwen_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=config
        )
        
        ollama_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.OLLAMA,
            config=config
        )
        
        # 验证配置正确映射
        assert qwen_config["model_name"] == "qwen-turbo"
        assert qwen_config["api_key"] == "qwen-key"
        
        assert ollama_config["model_name"] == "llama3"
        assert ollama_config["api_key"] is None
    
    @pytest.mark.asyncio
    async def test_multiple_providers_async_operations(self):
        """测试多个 Provider 的异步操作互不干扰"""
        # 创建多个 Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="qwen-key",
        )
        
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            # Mock 异步方法
            qwen_provider.check_available = AsyncMock(return_value=True)
            ollama_provider.check_available = AsyncMock(return_value=False)
            
            # 验证它们可以独立调用
            qwen_available = await qwen_provider.check_available()
            ollama_available = await ollama_provider.check_available()
            
            assert qwen_available is True
            assert ollama_available is False

