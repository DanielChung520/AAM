"""
@purpose: Provider 切換集成測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.unified_model_service import UnifiedModelService


class TestProviderSwitching:
    """Provider 切換集成測試類"""

    @pytest.mark.asyncio
    async def test_switch_provider_ollama(self):
        """測試切換到 Ollama Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama_instance.ainvoke = AsyncMock(return_value='{"entities": ["test"]}')
            mock_ollama.return_value = mock_ollama_instance
            
            # 創建 Provider
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
                api_base_url="http://localhost:11434",
            )
            
            # 創建統一模型服務
            unified_service = UnifiedModelService(provider=provider)
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            # 測試服務可用
            assert await unified_service.check_available() is True
            
            # 測試 Provider 類型
            assert provider.provider_type == ModelProviderType.OLLAMA

    @pytest.mark.asyncio
    async def test_provider_configuration_switching(self):
        """測試通過配置切換 Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            # 配置 1: Ollama
            config1 = {
                "provider_type": "ollama",
                "model_name": "llama3",
                "api_base_url": "http://localhost:11434",
            }
            
            provider1 = ModelProviderFactory.create_provider_from_config(config1)
            assert provider1.provider_type == ModelProviderType.OLLAMA
            assert provider1.model_name == "llama3"
            
            # 配置 2: 不同的模型
            config2 = {
                "provider_type": "ollama",
                "model_name": "mistral",
                "api_base_url": "http://localhost:11434",
            }
            
            provider2 = ModelProviderFactory.create_provider_from_config(config2)
            assert provider2.provider_type == ModelProviderType.OLLAMA
            assert provider2.model_name == "mistral"

    @pytest.mark.asyncio
    async def test_unified_service_with_different_providers(self):
        """測試統一模型服務使用不同的 Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            # 創建 Provider
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            # 創建統一模型服務
            unified_service = UnifiedModelService(provider=provider)
            
            # Mock 可用性檢查
            provider.check_available = AsyncMock(return_value=True)
            
            # 驗證服務正常工作
            assert await unified_service.check_available() is True
            assert unified_service.provider.provider_type == ModelProviderType.OLLAMA

    @pytest.mark.asyncio
    async def test_switch_provider_qwen(self):
        """測試切換到 Qwen Provider"""
        # 創建 Qwen Provider
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
        )
        
        # 創建統一模型服務
        unified_service = UnifiedModelService(provider=provider)
        
        # Mock 可用性檢查
        provider.check_available = AsyncMock(return_value=True)
        
        # 測試服務可用
        assert await unified_service.check_available() is True
        
        # 測試 Provider 類型
        assert provider.provider_type == ModelProviderType.QWEN
        assert isinstance(provider, QwenProvider)

    @pytest.mark.asyncio
    async def test_switch_provider_ollama_to_qwen(self):
        """測試從 Ollama 切換到 Qwen Provider"""
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            # 創建 Ollama Provider
            ollama_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.OLLAMA,
                model_name="llama3",
            )
            
            # 創建 Qwen Provider
            qwen_provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                model_name="qwen-turbo",
            )
            
            # 驗證兩個 Provider 類型不同
            assert ollama_provider.provider_type == ModelProviderType.OLLAMA
            assert qwen_provider.provider_type == ModelProviderType.QWEN
            
            # 創建統一模型服務（使用 Qwen）
            unified_service = UnifiedModelService(provider=qwen_provider)
            
            # Mock 可用性檢查
            qwen_provider.check_available = AsyncMock(return_value=True)
            
            # 驗證服務正常工作
            assert await unified_service.check_available() is True
            assert unified_service.provider.provider_type == ModelProviderType.QWEN

    @pytest.mark.asyncio
    async def test_provider_configuration_switching_qwen(self):
        """測試通過配置切換到 Qwen Provider"""
        # 配置 1: Ollama
        config1 = {
            "provider_type": "ollama",
            "model_name": "llama3",
            "api_base_url": "http://localhost:11434",
        }
        
        with patch('src.infrastructure.ai.providers.ollama_provider.Ollama') as mock_ollama:
            mock_ollama_instance = MagicMock()
            mock_ollama.return_value = mock_ollama_instance
            
            provider1 = ModelProviderFactory.create_provider_from_config(config1)
            assert provider1.provider_type == ModelProviderType.OLLAMA
        
        # 配置 2: Qwen
        config2 = {
            "provider_type": "qwen",
            "model_name": "qwen-turbo",
            "api_base_url": "https://test.com/api",
            "api_key": "test-key",
        }
        
        provider2 = ModelProviderFactory.create_provider_from_config(config2)
        assert provider2.provider_type == ModelProviderType.QWEN
        assert isinstance(provider2, QwenProvider)
        assert provider2.model_name == "qwen-turbo"

    @pytest.mark.asyncio
    async def test_unified_service_with_qwen_provider(self):
        """測試統一模型服務使用 Qwen Provider"""
        # 創建 Qwen Provider
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
        )
        
        # 創建統一模型服務
        unified_service = UnifiedModelService(provider=provider)
        
        # Mock 可用性檢查
        provider.check_available = AsyncMock(return_value=True)
        
        # 驗證服務正常工作
        assert await unified_service.check_available() is True
        assert unified_service.provider.provider_type == ModelProviderType.QWEN
        assert isinstance(unified_service.provider, QwenProvider)

    def test_provider_factory_error_handling(self):
        """測試 Provider 工廠錯誤處理"""
        # 測試無效的 Provider 類型
        with pytest.raises(ValueError):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.VLLM,  # 未實現
                model_name="test",
            )
        
        # 測試缺少必需配置
        with pytest.raises(ValueError, match="缺少"):
            ModelProviderFactory.create_provider_from_config({
                "provider_type": "ollama",
                # 缺少 model_name
            })

