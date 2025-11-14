"""
@purpose: 測試 PersonalityInsights 模型的數據驗證和序列化
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from pydantic import ValidationError

from src.models.domain.personality import PersonalityInsights


class TestPersonalityInsights:
    """測試 PersonalityInsights 模型"""

    def test_valid_personality_insights(self):
        """測試有效的個性分析結果"""
        insights = PersonalityInsights(
            style_tags={"formal": 10, "casual": 5},
            sentiment="positive",
            language_patterns=["polite", "professional"],
            confidence_score=0.85,
        )
        assert insights.style_tags["formal"] == 10
        assert insights.sentiment == "positive"
        assert len(insights.language_patterns) == 2
        assert insights.confidence_score == 0.85

    def test_default_values(self):
        """測試默認值"""
        insights = PersonalityInsights()
        assert insights.style_tags == {}
        assert insights.sentiment == "neutral"
        assert insights.language_patterns == []
        assert insights.confidence_score == 0.0

    def test_invalid_confidence_score_too_high(self):
        """測試置信度分數超出上限"""
        with pytest.raises(ValidationError):
            PersonalityInsights(confidence_score=1.5)

    def test_invalid_confidence_score_negative(self):
        """測試置信度分數為負數"""
        with pytest.raises(ValidationError):
            PersonalityInsights(confidence_score=-0.1)

    def test_valid_confidence_score_boundaries(self):
        """測試置信度分數邊界值"""
        # 最小值
        insights_min = PersonalityInsights(confidence_score=0.0)
        assert insights_min.confidence_score == 0.0

        # 最大值
        insights_max = PersonalityInsights(confidence_score=1.0)
        assert insights_max.confidence_score == 1.0

    def test_json_serialization(self):
        """測試 JSON 序列化"""
        insights = PersonalityInsights(
            style_tags={"formal": 10},
            sentiment="positive",
            confidence_score=0.9,
        )
        json_str = insights.model_dump_json()
        assert "formal" in json_str
        assert "positive" in json_str
        assert "0.9" in json_str

    def test_empty_style_tags(self):
        """測試空風格標籤"""
        insights = PersonalityInsights(style_tags={})
        assert insights.style_tags == {}

    def test_empty_language_patterns(self):
        """測試空語言模式列表"""
        insights = PersonalityInsights(language_patterns=[])
        assert insights.language_patterns == []

