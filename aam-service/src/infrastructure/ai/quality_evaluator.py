"""
@purpose: 質量評估器，用於評估知識提取的質量（實體、三元組等）
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
from typing import Dict, List, Optional

import structlog

from src.models.domain.database import KnowledgeAsset
from src.models.domain.quality import QualityEvaluationResult

logger = structlog.get_logger(__name__)


class QualityEvaluator:
    """
    質量評估器
    
    評估知識提取的質量，包括：
    - 實體提取質量（0-0.5分）
      - 實體數量: 0-0.2
      - 實體類型多樣性: 0-0.2
      - 實體置信度: 0-0.1（暫不支持，預留）
    - 三元組質量（0-0.5分）
      - 三元組數量: 0-0.2
      - 三元組完整性: 0-0.2
      - 三元組合理性: 0-0.1（基礎實現）
    
    總分: 0.0 - 1.0
    """

    def __init__(self, quality_threshold: float = 0.7):
        """
        初始化質量評估器
        
        Args:
            quality_threshold: 質量閾值（0.0-1.0），默認為 0.7
        """
        self.quality_threshold = quality_threshold
        logger.debug(
            "質量評估器已初始化",
            quality_threshold=quality_threshold,
        )

    def evaluate(
        self, knowledge: KnowledgeAsset, threshold: Optional[float] = None
    ) -> QualityEvaluationResult:
        """
        評估知識資產的質量
        
        Args:
            knowledge: 知識資產對象
            threshold: 質量閾值（可選），如果不提供則使用實例的默認閾值
            
        Returns:
            質量評估結果
        """
        used_threshold = threshold if threshold is not None else self.quality_threshold

        # 評估實體提取質量
        entity_score = self._evaluate_entity_quality(knowledge)
        
        # 評估三元組質量
        triple_score = self._evaluate_triple_quality(knowledge)
        
        # 計算綜合分數
        overall_score = entity_score + triple_score
        
        # 檢查是否達到閾值
        meets_threshold = overall_score >= used_threshold
        
        # 構建詳細信息
        details: Dict[str, float] = {
            "entity_count_score": self._calculate_entity_count_score(knowledge.entities),
            "entity_diversity_score": self._calculate_entity_diversity_score(
                knowledge.entities
            ),
            "triple_count_score": self._calculate_triple_count_score(knowledge),
            "triple_completeness_score": self._calculate_triple_completeness_score(
                knowledge
            ),
            "triple_reasonableness_score": self._calculate_triple_reasonableness_score(
                knowledge
            ),
        }
        
        # 獲取實體和三元組數量
        entity_count = len(knowledge.entities)
        triple_count = self._get_triple_count(knowledge)
        
        result = QualityEvaluationResult(
            overall_score=overall_score,
            entity_score=entity_score,
            triple_score=triple_score,
            entity_count=entity_count,
            triple_count=triple_count,
            details=details,
            meets_threshold=meets_threshold,
            threshold=used_threshold,
        )
        
        logger.debug(
            "質量評估完成",
            overall_score=overall_score,
            entity_score=entity_score,
            triple_score=triple_score,
            meets_threshold=meets_threshold,
            threshold=used_threshold,
        )
        
        return result

    def _evaluate_entity_quality(self, knowledge: KnowledgeAsset) -> float:
        """
        評估實體提取質量（0-0.5分）
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            實體質量分數（0.0-0.5）
        """
        score = 0.0
        
        # 實體數量評分（0-0.2）
        score += self._calculate_entity_count_score(knowledge.entities)
        
        # 實體類型多樣性評分（0-0.2）
        score += self._calculate_entity_diversity_score(knowledge.entities)
        
        # 實體置信度評分（0-0.1，暫不支持，預留）
        # TODO: 如果實體包含置信度信息，可以在此評估
        
        return min(0.5, score)

    def _evaluate_triple_quality(self, knowledge: KnowledgeAsset) -> float:
        """
        評估三元組質量（0-0.5分）
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組質量分數（0.0-0.5）
        """
        score = 0.0
        
        # 三元組數量評分（0-0.2）
        score += self._calculate_triple_count_score(knowledge)
        
        # 三元組完整性評分（0-0.2）
        score += self._calculate_triple_completeness_score(knowledge)
        
        # 三元組合理性評分（0-0.1）
        score += self._calculate_triple_reasonableness_score(knowledge)
        
        return min(0.5, score)

    def _calculate_entity_count_score(self, entities: List[str]) -> float:
        """
        計算實體數量評分（0-0.2）
        
        評分規則：
        - 0 個實體: 0 分
        - 1-4 個實體: 0.05 * 數量
        - 4+ 個實體: 0.2 分（上限）
        
        Args:
            entities: 實體列表
            
        Returns:
            實體數量評分（0.0-0.2）
        """
        count = len(entities)
        if count == 0:
            return 0.0
        
        # 每個實體 0.05 分，最多 0.2 分（4 個實體）
        score = min(0.2, count * 0.05)
        return score

    def _calculate_entity_diversity_score(self, entities: List[str]) -> float:
        """
        計算實體類型多樣性評分（0-0.2）
        
        評分規則：
        - 基於實體的唯一性（去重後的數量）
        - 如果所有實體都不同，則得分較高
        
        Args:
            entities: 實體列表
            
        Returns:
            實體多樣性評分（0.0-0.2）
        """
        if not entities:
            return 0.0
        
        # 計算唯一實體數量
        unique_entities = len(set(entities))
        total_entities = len(entities)
        
        if total_entities == 0:
            return 0.0
        
        # 多樣性比率（唯一實體 / 總實體）
        diversity_ratio = unique_entities / total_entities
        
        # 基於多樣性比率和數量計算分數
        # 如果多樣性高且數量多，得分較高
        base_score = diversity_ratio * 0.15  # 基礎分數（0-0.15）
        bonus_score = min(0.05, unique_entities * 0.01)  # 數量獎勵（最多 0.05）
        
        return min(0.2, base_score + bonus_score)

    def _calculate_triple_count_score(self, knowledge: KnowledgeAsset) -> float:
        """
        計算三元組數量評分（0-0.2）
        
        評分規則：
        - 0 個三元組: 0 分
        - 1-4 個三元組: 0.05 * 數量
        - 4+ 個三元組: 0.2 分（上限）
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組數量評分（0.0-0.2）
        """
        triples = self._parse_triples(knowledge)
        count = len(triples)
        
        if count == 0:
            return 0.0
        
        # 每個三元組 0.05 分，最多 0.2 分（4 個三元組）
        score = min(0.2, count * 0.05)
        return score

    def _calculate_triple_completeness_score(
        self, knowledge: KnowledgeAsset
    ) -> float:
        """
        計算三元組完整性評分（0-0.2）
        
        評分規則：
        - 檢查每個三元組是否包含 subject, predicate, object
        - 完整性 = 完整三元組數量 / 總三元組數量
        - 分數 = 完整性 * 0.2
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組完整性評分（0.0-0.2）
        """
        triples = self._parse_triples(knowledge)
        
        if not triples:
            return 0.0
        
        # 計算完整三元組數量
        complete_triples = [
            t
            for t in triples
            if t.get("subject") and t.get("predicate") and t.get("object")
        ]
        
        completeness_ratio = len(complete_triples) / len(triples)
        score = completeness_ratio * 0.2
        
        return score

    def _calculate_triple_reasonableness_score(
        self, knowledge: KnowledgeAsset
    ) -> float:
        """
        計算三元組合理性評分（0-0.1）
        
        評分規則（基礎實現）：
        - 檢查三元組的 subject, predicate, object 是否為非空字符串
        - 如果所有三元組都合理，則得分較高
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組合理性評分（0.0-0.1）
        """
        triples = self._parse_triples(knowledge)
        
        if not triples:
            return 0.0
        
        # 計算合理三元組數量
        # 合理性：subject, predicate, object 都是非空字符串
        reasonable_triples = [
            t
            for t in triples
            if (
                isinstance(t.get("subject"), str)
                and t.get("subject").strip()
                and isinstance(t.get("predicate"), str)
                and t.get("predicate").strip()
                and isinstance(t.get("object"), str)
                and t.get("object").strip()
            )
        ]
        
        reasonableness_ratio = len(reasonable_triples) / len(triples)
        score = reasonableness_ratio * 0.1
        
        return score

    def _parse_triples(self, knowledge: KnowledgeAsset) -> List[Dict]:
        """
        解析三元組 JSON 字符串
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組列表
        """
        try:
            triples = json.loads(knowledge.triples_json)
            if not isinstance(triples, list):
                return []
            return triples
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.warning(
                "解析三元組 JSON 失敗",
                error=str(e),
                triples_json=knowledge.triples_json,
            )
            return []

    def _get_triple_count(self, knowledge: KnowledgeAsset) -> int:
        """
        獲取三元組數量
        
        Args:
            knowledge: 知識資產對象
            
        Returns:
            三元組數量
        """
        triples = self._parse_triples(knowledge)
        return len(triples)

