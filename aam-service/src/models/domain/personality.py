"""
@purpose: 定義用戶個性分析結果的數據模型，用於 AI 模型分析輸出
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import Dict, List

from pydantic import BaseModel, Field


class PersonalityInsights(BaseModel):
    """用戶個性分析結果模型 - IAnalysisModel.analyze_personality 返回類型"""
    style_tags: Dict[str, int] = Field(
        default_factory=dict,
        description="風格標籤字典，例如：{'formal': 10, 'casual': 5}"
    )
    sentiment: str = Field(
        default="neutral",
        description="情感狀態，例如：'positive', 'negative', 'neutral'"
    )
    language_patterns: List[str] = Field(
        default_factory=list,
        description="語言模式列表（可選）"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="分析置信度分數（0.0-1.0）"
    )

