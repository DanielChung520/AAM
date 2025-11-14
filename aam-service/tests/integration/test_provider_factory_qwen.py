"""
@purpose: Provider Factory Qwen 測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import pytest

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.providers.qwen_provider import QwenProvider


class TestProviderFactoryQwen:
    """Provider Factory Qwen 測試類"""

    def test_create_qwen_provider_from_factory(self):
        """測試通過 Factory 創建 Qwen Provider"""
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://test.com/api",
            api_key="test-key",
            timeout=120,
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.provider_type == ModelProviderType.QWEN
        assert provider.model_name == "qwen-turbo"
        assert provider.api_base_url == "https://test.com/api"
        assert provider.api_key == "test-key"
        assert provider.timeout == 120

    def test_create_qwen_provider_with_defaults(self):
        """測試使用默認值創建 Qwen Provider"""
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.model_name == "qwen-turbo"
        # 驗證使用了默認值
        assert provider.api_base_url is not None
        assert provider.api_key is not None

    def test_create_qwen_provider_with_kwargs(self):
        """測試通過 kwargs 傳遞 Qwen 特定配置"""
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://default.com/api",
            api_key="default-key",
            timeout=120,
            qwen_api_base_url="https://custom.com/api",
            qwen_api_key="custom-key",
            qwen_timeout=60,
        )
        
        assert isinstance(provider, QwenProvider)
        # kwargs 應該優先於參數
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
        assert provider.provider_type == ModelProviderType.QWEN
        assert provider.model_name == "qwen-turbo"
        assert provider.api_base_url == "https://test.com/api"
        assert provider.api_key == "test-key"

    def test_create_qwen_provider_config_priority(self):
        """測試配置優先級（kwargs > 參數 > 默認值）"""
        # 測試 1: 使用參數
        provider1 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://param.com/api",
            api_key="param-key",
        )
        assert provider1.api_base_url == "https://param.com/api"
        assert provider1.api_key == "param-key"
        
        # 測試 2: kwargs 優先於參數
        provider2 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            api_base_url="https://param.com/api",
            api_key="param-key",
            qwen_api_base_url="https://kwargs.com/api",
            qwen_api_key="kwargs-key",
        )
        assert provider2.api_base_url == "https://kwargs.com/api"
        assert provider2.api_key == "kwargs-key"

    def test_create_qwen_provider_with_partial_config(self):
        """測試使用部分配置創建 Qwen Provider"""
        # 只提供 model_name，其他使用默認值
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-plus",
        )
        
        assert isinstance(provider, QwenProvider)
        assert provider.model_name == "qwen-plus"
        # 驗證使用了默認值
        assert provider.api_base_url is not None
        assert provider.api_key is not None

    def test_create_qwen_provider_invalid_config(self):
        """測試無效配置處理"""
        # 缺少 model_name
        with pytest.raises(ValueError):
            ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                # 缺少 model_name
            )

    def test_create_qwen_provider_from_config_missing_fields(self):
        """測試從配置字典創建（缺少必需字段）"""
        # 缺少 provider_type
        with pytest.raises(ValueError, match="缺少 provider_type"):
            ModelProviderFactory.create_provider_from_config({
                "model_name": "qwen-turbo",
            })
        
        # 缺少 model_name
        with pytest.raises(ValueError, match="缺少 model_name"):
            ModelProviderFactory.create_provider_from_config({
                "provider_type": "qwen",
            })

    def test_create_qwen_provider_different_models(self):
        """測試創建不同模型的 Qwen Provider"""
        models = ["qwen-turbo", "qwen-plus", "qwen-max"]
        
        for model_name in models:
            provider = ModelProviderFactory.create_provider(
                provider_type=ModelProviderType.QWEN,
                model_name=model_name,
            )
            
            assert isinstance(provider, QwenProvider)
            assert provider.model_name == model_name

    def test_create_qwen_provider_timeout_config(self):
        """測試 Qwen Provider 超時配置"""
        # 測試默認超時
        provider1 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
        )
        assert provider1.timeout == 120  # 默認值
        
        # 測試自定義超時
        provider2 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            timeout=60,
        )
        assert provider2.timeout == 60
        
        # 測試通過 kwargs 設置超時
        provider3 = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.QWEN,
            model_name="qwen-turbo",
            timeout=120,
            qwen_timeout=90,
        )
        assert provider3.timeout == 90

