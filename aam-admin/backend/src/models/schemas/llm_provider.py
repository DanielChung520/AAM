"""
@purpose: LLM Provider 相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """模型配置响应模型"""

    model_name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    max_tokens: int = Field(8192, description="最大 token 数")
    temperature: float = Field(0.5, description="温度参数")
    enabled: bool = Field(True, description="是否启用")
    priority: int = Field(1, description="优先级（数字越小优先级越高）")
    description: Optional[str] = Field(None, description="模型描述")


class ModelConfigUpdate(BaseModel):
    """模型配置更新请求模型"""

    max_tokens: Optional[int] = Field(None, description="最大 token 数")
    temperature: Optional[float] = Field(None, description="温度参数")
    enabled: Optional[bool] = Field(None, description="是否启用")
    priority: Optional[int] = Field(None, description="优先级")
    description: Optional[str] = Field(None, description="模型描述")


class LLMProvider(BaseModel):
    """LLM Provider 响应模型"""

    provider_type: str = Field(..., description="Provider 类型 (qwen/gemini/ollama)")
    models: List[ModelConfig] = Field(default_factory=list, description="模型列表")
    status: str = Field("unknown", description="Provider 状态 (active/inactive/error)")


class ProviderTestResponse(BaseModel):
    """Provider 测试响应模型"""

    success: bool = Field(..., description="测试是否成功")
    message: str = Field(..., description="测试结果消息")
    response_time_ms: Optional[float] = Field(None, description="响应时间（毫秒）")


class ProviderListResponse(BaseModel):
    """Provider 列表响应模型"""

    providers: List[LLMProvider] = Field(default_factory=list, description="Provider 列表")

