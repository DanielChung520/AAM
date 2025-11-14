"""
@purpose: 模型配置数据类定义
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
from dataclasses import dataclass, field
from typing import Optional

from src.core.interfaces.i_model_provider import ModelProviderType


@dataclass
class ModelConfig:
    """
    模型配置数据类
    
    定义单个模型的完整配置信息
    """
    model_name: str
    provider_type: ModelProviderType
    enabled: bool = True
    
    # 配置字段（默认值）
    max_tokens: int = 8192
    temperature: float = 0.5
    
    # 元数据字段
    display_name: Optional[str] = None
    description: Optional[str] = None
    priority: int = 999  # 优先级，数字越小优先级越高，默认 999 表示最低优先级
    
    def __post_init__(self):
        """验证和规范化数据"""
        if not self.display_name:
            self.display_name = self.model_name
        
        # 验证 provider_type
        if isinstance(self.provider_type, str):
            try:
                self.provider_type = ModelProviderType(self.provider_type.lower())
            except ValueError:
                raise ValueError(f"无效的 provider_type: {self.provider_type}")
        
        # 验证数值范围
        if self.max_tokens < 1:
            raise ValueError(f"max_tokens 必须大于 0，当前值: {self.max_tokens}")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"temperature 必须在 0.0-2.0 之间，当前值: {self.temperature}")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "model_name": self.model_name,
            "display_name": self.display_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "enabled": self.enabled,
            "priority": self.priority,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, provider_type: ModelProviderType, data: dict) -> "ModelConfig":
        """
        从字典创建 ModelConfig 实例
        
        Args:
            provider_type: Provider 类型
            data: 模型配置字典
            
        Returns:
            ModelConfig 实例
        """
        # 验证必需字段
        if "model_name" not in data:
            raise ValueError("模型配置中缺少必需字段: model_name")
        
        return cls(
            model_name=data["model_name"],
            provider_type=provider_type,
            enabled=data.get("enabled", True),
            max_tokens=data.get("max_tokens", 8192),
            temperature=data.get("temperature", 0.5),
            display_name=data.get("display_name"),
            description=data.get("description"),
            priority=data.get("priority", 999),
        )

