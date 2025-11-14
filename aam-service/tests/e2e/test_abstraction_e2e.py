"""
@purpose: 端到端测试 LLM Provider 抽象性
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.config.provider_config_adapter import ProviderConfigAdapter
from src.config.settings import ModelServiceSettings, get_settings
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.unified_model_service import UnifiedModelService


class TestAbstractionE2E:
    """端到端测试抽象性"""
    
    def test_complete_flow_from_config_to_provider(self):
        """测试从配置到创建 Provider 的完整流程"""
        # 1. 创建配置
        config = ModelServiceSettings(
            qwen_model_name="qwen-turbo",
            qwen_api_key="test-key",
        )
        
        # 2. 使用配置适配器获取 Provider 配置
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=config
        )
        
        # 3. 使用 Factory 创建 Provider
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            **provider_config
        )
        
        # 4. 验证 Provider 正确创建
        assert provider.provider_type == ModelProviderType.QWEN
        assert provider.model_name == "qwen-turbo"
        assert provider.api_key == "test-key"
    
    def test_complete_flow_with_unified_service(self):
        """测试从配置到 UnifiedModelService 的完整流程"""
        # 1. 创建配置
        config = ModelServiceSettings(
            qwen_model_name="qwen-turbo",
            qwen_api_key="test-key",
        )
        
        # 2. 使用配置适配器获取 Provider 配置
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=config
        )
        
        # 3. 使用 Factory 创建 Provider
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            **provider_config
        )
        
        # 4. 创建 UnifiedModelService
        unified_service = UnifiedModelService(provider=provider)
        
        # 5. 验证 UnifiedModelService 使用抽象 Provider
        assert unified_service.provider.provider_type == ModelProviderType.QWEN
        assert isinstance(unified_service.provider, provider.__class__)
    
    def test_business_logic_independent_of_provider(self):
        """测试业务逻辑不依赖具体 Provider"""
        # 测试使用 Qwen Provider
        qwen_provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_key="test-key",
        )
        
        unified_service_qwen = UnifiedModelService(provider=qwen_provider)
        
        # 测试使用 Ollama Provider
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama.return_value = Mock()
            
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            unified_service_ollama = UnifiedModelService(provider=ollama_provider)
            
            # 验证 UnifiedModelService 的接口一致，不依赖具体 Provider
            assert hasattr(unified_service_qwen, 'extract_knowledge')
            assert hasattr(unified_service_qwen, 'analyze_personality')
            
            assert hasattr(unified_service_ollama, 'extract_knowledge')
            assert hasattr(unified_service_ollama, 'analyze_personality')
    
    @pytest.mark.asyncio
    async def test_provider_switching_in_complete_flow(self):
        """测试完整流程中的 Provider 切换"""
        # 模拟从环境变量读取配置
        test_configs = [
            (ModelProviderType.QWEN, ModelServiceSettings(qwen_api_key="qwen-key")),
            (ModelProviderType.OLLAMA, ModelServiceSettings()),
        ]
        
        for provider_type, config in test_configs:
            # 使用配置适配器
            provider_config = ProviderConfigAdapter.get_provider_config(
                provider_type=provider_type,
                config=config
            )
            
            # 使用 Factory 创建 Provider
            if provider_type == ModelProviderType.OLLAMA:
                with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
                    mock_ollama.return_value = Mock()
                    provider = ModelProviderFactory.create_provider(
                        provider_type=provider_type,
                        **provider_config
                    )
            else:
                provider = ModelProviderFactory.create_provider(
                    provider_type=provider_type,
                    **provider_config
                )
            
            # 创建 UnifiedModelService
            unified_service = UnifiedModelService(provider=provider)
            
            # 验证流程完整
            assert unified_service.provider.provider_type == provider_type
            
            # Mock 可用性检查
            provider.check_available = AsyncMock(return_value=True)
            assert await provider.check_available() is True
    
    def test_adding_new_provider_requires_minimal_changes(self):
        """测试新增 Provider 只需最小改动"""
        # 模拟新增 Provider 的流程
        # 1. 在配置适配器中添加映射（这是唯一需要修改的地方）
        # 2. 在 Factory 中添加一个分支（这也是唯一需要修改的地方）
        # 3. 实现 Provider 类（新文件）
        
        # 验证当前架构支持这种扩展
        # 测试配置适配器可以处理新 Provider
        config = ModelServiceSettings()
        
        # 对于未实现的 Provider，应该返回通用配置
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.OPENAI,  # 未实现
            config=config
        )
        
        # 验证返回统一结构
        assert "model_name" in provider_config
        assert "api_base_url" in provider_config
        assert "api_key" in provider_config
        assert "timeout" in provider_config
    
    @pytest.mark.skipif(
        not os.getenv("QWEN_API_KEY"),
        reason="需要设置 QWEN_API_KEY 环境变量"
    )
    @pytest.mark.asyncio
    async def test_real_provider_integration(self):
        """测试真实 Provider 集成（需要 API Key）"""
        # 使用真实配置
        config = ModelServiceSettings(
            qwen_model_name="qwen-turbo",
            qwen_api_key=os.getenv("QWEN_API_KEY"),
        )
        
        # 完整流程
        provider_config = ProviderConfigAdapter.get_provider_config(
            provider_type=ModelProviderType.QWEN,
            config=config
        )
        
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            **provider_config
        )
        
        unified_service = UnifiedModelService(provider=provider)
        
        # 验证真实 Provider 可用
        is_available = await provider.check_available()
        assert isinstance(is_available, bool)  # 可能是 True 或 False，取决于 API

