"""
@purpose: 定義質量評估相關的數據模型
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import Dict, Optional

from pydantic import BaseModel, Field


class QualityEvaluationResult(BaseModel):
    """質量評估結果模型"""
    
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="綜合質量分數（0.0-1.0）"
    )
    
    entity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=0.5,
        description="實體提取質量分數（0.0-0.5）"
    )
    
    triple_score: float = Field(
        default=0.0,
        ge=0.0,
        le=0.5,
        description="三元組質量分數（0.0-0.5）"
    )
    
    entity_count: int = Field(
        default=0,
        description="實體數量"
    )
    
    triple_count: int = Field(
        default=0,
        description="三元組數量"
    )
    
    details: Dict[str, float] = Field(
        default_factory=dict,
        description="詳細評估維度分數（可選）"
    )
    
    meets_threshold: bool = Field(
        default=False,
        description="是否達到質量閾值"
    )
    
    threshold: Optional[float] = Field(
        default=None,
        description="使用的質量閾值（如果提供）"
    )

