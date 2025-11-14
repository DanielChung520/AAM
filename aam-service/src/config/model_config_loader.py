"""
@purpose: 模型配置加载器，负责加载和管理模型配置文件
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.config.model_config import ModelConfig
from src.core.interfaces.i_model_provider import ModelProviderType

logger = logging.getLogger(__name__)


class ModelConfigLoader:
    """
    模型配置加载器
    
    负责加载、验证和管理模型配置文件
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化模型配置加载器
        
        Args:
            config_path: 模型配置文件路径，如果为 None，使用默认路径 config/models.json
        """
        if config_path is None:
            # 默认路径：项目根目录下的 config/models.json
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "models.json"
        
        self.config_path = Path(config_path)
        self._config_cache: Optional[Dict[str, Dict[str, List[ModelConfig]]]] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                logger.warning(
                    f"模型配置文件不存在: {self.config_path}，将使用默认配置"
                )
                self._config_cache = {}
                return
            
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 验证和解析配置
            self._config_cache = {}
            for provider_str, provider_data in data.items():
                try:
                    provider_type = ModelProviderType(provider_str.lower())
                except ValueError:
                    logger.warning(
                        f"跳过未知的 Provider 类型: {provider_str}"
                    )
                    continue
                
                if "models" not in provider_data:
                    logger.warning(
                        f"Provider {provider_str} 配置中缺少 'models' 字段"
                    )
                    continue
                
                models = []
                for model_data in provider_data["models"]:
                    try:
                        model_config = ModelConfig.from_dict(
                            provider_type=provider_type,
                            data=model_data
                        )
                        models.append(model_config)
                    except Exception as e:
                        logger.error(
                            f"加载模型配置失败: {e}",
                            extra={
                                "provider": provider_str,
                                "model_data": model_data,
                            }
                        )
                        continue
                
                self._config_cache[provider_type.value] = {
                    "models": models
                }
            
            logger.info(
                f"成功加载模型配置文件: {self.config_path}",
                extra={
                    "providers": list(self._config_cache.keys()),
                    "total_models": sum(
                        len(v["models"]) for v in self._config_cache.values()
                    ),
                }
            )
        
        except json.JSONDecodeError as e:
            logger.error(
                f"模型配置文件 JSON 格式错误: {e}",
                extra={"config_path": str(self.config_path)}
            )
            self._config_cache = {}
        except Exception as e:
            logger.error(
                f"加载模型配置文件失败: {e}",
                extra={"config_path": str(self.config_path)}
            )
            self._config_cache = {}
    
    def reload_configs(self) -> None:
        """重新加载配置文件（支持热更新）"""
        logger.info("重新加载模型配置文件")
        self._load_config()
    
    def get_enabled_models(
        self, provider_type: ModelProviderType
    ) -> List[ModelConfig]:
        """
        获取指定 Provider 的启用模型列表
        
        Args:
            provider_type: Provider 类型
            
        Returns:
            启用的模型配置列表，按 priority 排序
        """
        if self._config_cache is None:
            return []
        
        provider_key = provider_type.value
        if provider_key not in self._config_cache:
            return []
        
        models = [
            model for model in self._config_cache[provider_key]["models"]
            if model.enabled
        ]
        
        # 按 priority 排序（数字越小优先级越高）
        models.sort(key=lambda m: m.priority)
        
        return models
    
    def get_model_config(
        self, provider_type: ModelProviderType, model_name: str
    ) -> Optional[ModelConfig]:
        """
        获取特定模型的完整配置
        
        Args:
            provider_type: Provider 类型
            model_name: 模型名称
            
        Returns:
            模型配置，如果未找到返回 None
        """
        if self._config_cache is None:
            return None
        
        provider_key = provider_type.value
        if provider_key not in self._config_cache:
            return None
        
        for model in self._config_cache[provider_key]["models"]:
            if model.model_name == model_name:
                return model
        
        return None
    
    def get_default_model(
        self, provider_type: ModelProviderType
    ) -> Optional[ModelConfig]:
        """
        获取默认模型（优先级最高或第一个启用的）
        
        Args:
            provider_type: Provider 类型
            
        Returns:
            默认模型配置，如果未找到返回 None
        """
        enabled_models = self.get_enabled_models(provider_type)
        if enabled_models:
            return enabled_models[0]  # 已经按 priority 排序
        return None
    
    def list_all_models(
        self, provider_type: Optional[ModelProviderType] = None
    ) -> Dict[str, List[ModelConfig]]:
        """
        列出所有模型（包括启用的和禁用的）
        
        Args:
            provider_type: 如果指定，只返回该 Provider 的模型；否则返回所有 Provider 的模型
            
        Returns:
            字典，key 为 provider_type.value，value 为模型配置列表
        """
        if self._config_cache is None:
            return {}
        
        if provider_type:
            provider_key = provider_type.value
            if provider_key in self._config_cache:
                return {
                    provider_key: self._config_cache[provider_key]["models"]
                }
            return {}
        
        return {
            provider_key: data["models"]
            for provider_key, data in self._config_cache.items()
        }
    
    def validate_config(self) -> bool:
        """
        验证配置文件格式和必需字段
        
        Returns:
            True 如果配置有效，False 否则
        """
        if self._config_cache is None:
            return False
        
        errors = []
        
        for provider_key, provider_data in self._config_cache.items():
            if "models" not in provider_data:
                errors.append(f"Provider {provider_key} 缺少 'models' 字段")
                continue
            
            for i, model in enumerate(provider_data["models"]):
                if not model.model_name:
                    errors.append(
                        f"Provider {provider_key} 模型 #{i} 缺少 model_name"
                    )
                if model.max_tokens < 1:
                    errors.append(
                        f"Provider {provider_key} 模型 {model.model_name} "
                        f"max_tokens 无效: {model.max_tokens}"
                    )
                if not 0.0 <= model.temperature <= 2.0:
                    errors.append(
                        f"Provider {provider_key} 模型 {model.model_name} "
                        f"temperature 无效: {model.temperature}"
                    )
        
        if errors:
            logger.error(
                "模型配置验证失败",
                extra={"errors": errors}
            )
            return False
        
        return True
    
    def is_model_enabled(
        self, provider_type: ModelProviderType, model_name: str
    ) -> bool:
        """
        检查模型是否启用
        
        Args:
            provider_type: Provider 类型
            model_name: 模型名称
            
        Returns:
            True 如果模型启用，False 否则
        """
        model_config = self.get_model_config(provider_type, model_name)
        return model_config is not None and model_config.enabled


# 全局单例实例
_loader_instance: Optional[ModelConfigLoader] = None


def get_model_config_loader(config_path: Optional[str] = None) -> ModelConfigLoader:
    """
    获取模型配置加载器单例
    
    Args:
        config_path: 模型配置文件路径，如果为 None，使用默认路径
        
    Returns:
        ModelConfigLoader 实例
    """
    global _loader_instance
    
    if _loader_instance is None:
        _loader_instance = ModelConfigLoader(config_path)
    
    return _loader_instance

