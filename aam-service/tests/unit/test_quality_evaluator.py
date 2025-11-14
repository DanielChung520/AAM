"""
@purpose: 質量評估器單元測試
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import pytest

from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset


class TestQualityEvaluator:
    """質量評估器測試類"""

    def test_evaluate_empty_knowledge(self):
        """測試評估空知識資產"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        
        result = evaluator.evaluate(knowledge)
        
        assert result.overall_score == 0.0
        assert result.entity_score == 0.0
        assert result.triple_score == 0.0
        assert result.entity_count == 0
        assert result.triple_count == 0
        assert result.meets_threshold is False

    def test_evaluate_entity_quality(self):
        """測試實體提取質量評估"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2", "實體3", "實體4"],
            triples_json="[]",
        )
        
        result = evaluator.evaluate(knowledge)
        
        assert result.entity_count == 4
        assert result.entity_score > 0.0
        assert result.entity_score <= 0.5

    def test_evaluate_triple_quality(self):
        """測試三元組質量評估"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        triples = [
            {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
            {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"},
        ]
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=[],
            triples_json=json.dumps(triples),
        )
        
        result = evaluator.evaluate(knowledge)
        
        assert result.triple_count == 2
        assert result.triple_score > 0.0
        assert result.triple_score <= 0.5

    def test_evaluate_incomplete_triples(self):
        """測試不完整三元組評估"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        triples = [
            {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
            {"subject": "主體2", "predicate": "謂詞2"},  # 缺少 object
            {"subject": "主體3"},  # 缺少 predicate 和 object
        ]
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=[],
            triples_json=json.dumps(triples),
        )
        
        result = evaluator.evaluate(knowledge)
        
        assert result.triple_count == 3
        # 完整性分數應該較低
        assert result.triple_score < 0.5

    def test_evaluate_meets_threshold(self):
        """測試質量閾值判斷"""
        evaluator = QualityEvaluator(quality_threshold=0.3)
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2", "實體3", "實體4"],
            triples_json=json.dumps([
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
                {"subject": "主體2", "predicate": "謂詞2", "object": "客體2"},
            ]),
        )
        
        result = evaluator.evaluate(knowledge)
        
        # 應該達到較低的閾值
        assert result.meets_threshold is True

    def test_evaluate_custom_threshold(self):
        """測試自定義質量閾值"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2"],
            triples_json=json.dumps([
                {"subject": "主體1", "predicate": "謂詞1", "object": "客體1"},
            ]),
        )
        
        # 使用默認閾值
        result1 = evaluator.evaluate(knowledge)
        
        # 使用自定義閾值（較低）
        result2 = evaluator.evaluate(knowledge, threshold=0.1)
        
        assert result1.overall_score == result2.overall_score
        assert result1.meets_threshold != result2.meets_threshold

    def test_evaluate_invalid_triples_json(self):
        """測試無效的三元組 JSON"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        knowledge = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1"],
            triples_json="invalid json",
        )
        
        result = evaluator.evaluate(knowledge)
        
        # 應該能夠處理無效 JSON，返回 0 分
        assert result.triple_count == 0
        assert result.triple_score == 0.0

    def test_evaluate_entity_diversity(self):
        """測試實體多樣性評估"""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        
        # 測試唯一實體（高多樣性）
        knowledge1 = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體2", "實體3"],
            triples_json="[]",
        )
        result1 = evaluator.evaluate(knowledge1)
        
        # 測試重複實體（低多樣性）
        knowledge2 = KnowledgeAsset(
            user_id="test_user",
            session_id="test_session",
            timestamp=1234567890,
            source_type="dialogue",
            entities=["實體1", "實體1", "實體1"],
            triples_json="[]",
        )
        result2 = evaluator.evaluate(knowledge2)
        
        # 唯一實體應該得分更高
        assert result1.entity_score > result2.entity_score

