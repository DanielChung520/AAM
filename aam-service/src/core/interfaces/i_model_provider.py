"""
@purpose: 定義模型服務提供商的抽象接口，用於統一不同後端模型服務的調用
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict


class ModelProviderType(str, Enum):
    """模型服務提供商類型枚舉"""
    
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    GEMINI = "gemini"
    CUSTOM = "custom"


class IModelProvider(ABC):
    """模型服務提供商抽象接口"""
    
    @property
    @abstractmethod
    def provider_type(self) -> ModelProviderType:
        """
        返回提供商類型
        
        Returns:
            提供商類型枚舉值
        """
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        生成文本
        
        Args:
            prompt: 輸入提示詞
            **kwargs: 其他參數（如 temperature, max_tokens 等）
            
        Returns:
            生成的文本內容
            
        Raises:
            RuntimeError: 當服務不可用或生成失敗時
        """
        pass
    
    @abstractmethod
    async def check_available(self) -> bool:
        """
        檢查服務是否可用
        
        Returns:
            如果服務可用返回 True，否則返回 False
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        獲取提供商配置信息（可選方法）
        
        Returns:
            配置信息字典
        """
        return {}

