"""
@purpose: 三元組分類服務，實現 AI 自動分類和預定義分類映射
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import logging
from typing import List, Optional

from src.core.interfaces.i_model_provider import IModelProvider
from src.models.domain.triple_categories import (
    get_category_label,
    map_ai_category_to_predefined,
)

logger = logging.getLogger(__name__)


class TripleClassifier:
    """三元組分類服務"""

    def __init__(self, provider: IModelProvider):
        """
        初始化分類服務
        
        Args:
            provider: 模型服務提供商實例
        """
        self.provider = provider

    async def classify_triples(
        self, triples: List[dict]
    ) -> List[dict]:
        """
        對三元組列表進行分類
        
        Args:
            triples: 三元組列表，每個三元組包含 subject, predicate, object
            
        Returns:
            分類後的三元組列表，每個三元組包含 category 和 ai_category 字段
        """
        if not triples:
            return []

        classified_triples = []

        for triple in triples:
            if not isinstance(triple, dict):
                continue

            # 提取三元組信息
            subject = triple.get("subject", "")
            predicate = triple.get("predicate", "")
            object_val = triple.get("object", "")

            if not subject or not predicate or not object_val:
                # 如果三元組不完整，跳過分類
                classified_triples.append(triple)
                continue

            try:
                # 調用 AI 模型進行分類
                ai_category = await self._classify_with_ai(
                    subject, predicate, object_val
                )

                # 映射到預定義分類
                category_key = map_ai_category_to_predefined(ai_category)
                category_label = get_category_label(category_key)

                # 添加分類標籤到三元組
                classified_triple = {
                    **triple,
                    "category": category_label,
                    "ai_category": ai_category,
                }

                classified_triples.append(classified_triple)

            except Exception as e:
                logger.warning(
                    f"三元組分類失敗: {e}",
                    extra={
                        "subject": subject,
                        "predicate": predicate,
                        "object": object_val,
                        "error": str(e),
                    },
                )
                # 分類失敗時，使用默認分類
                classified_triple = {
                    **triple,
                    "category": "其他",
                    "ai_category": None,
                }
                classified_triples.append(classified_triple)

        return classified_triples

    async def _classify_with_ai(
        self, subject: str, predicate: str, object_val: str
    ) -> str:
        """
        使用 AI 模型對單個三元組進行分類
        
        Args:
            subject: 主語
            predicate: 謂語
            object_val: 賓語
            
        Returns:
            AI 分類標籤（字符串）
        """
        # 構建分類 Prompt
        classification_prompt = f"""你是一個專業的知識三元組分類系統。請根據以下三元組的內容，判斷它屬於哪個分類領域。

三元組：
- 主語（Subject）: {subject}
- 謂語（Predicate）: {predicate}
- 賓語（Object）: {object_val}

請從以下分類中選擇最合適的一個（只返回分類名稱，不要返回其他內容）：
- 技術（technology）
- 業務（business）
- 教育（education）
- 醫療（medical）
- 金融（finance）
- 人物關係（person_relation）
- 時間關係（temporal）
- 其他（other）

如果以上分類都不合適，請返回一個簡短的中文分類名稱（不超過10個字）。

分類結果："""

        try:
            # 調用 Provider 進行分類
            result = await self.provider.generate(classification_prompt)

            # 清理結果（去除空白字符和換行）
            ai_category = result.strip() if result else "其他"

            # 如果結果太長，截斷
            if len(ai_category) > 50:
                ai_category = ai_category[:50]

            return ai_category

        except Exception as e:
            logger.warning(
                f"AI 分類調用失敗: {e}",
                extra={
                    "subject": subject,
                    "predicate": predicate,
                    "object": object_val,
                    "error": str(e),
                },
            )
            # 返回默認分類
            return "其他"

    async def classify_triples_batch(
        self, triples: List[dict], batch_size: int = 5
    ) -> List[dict]:
        """
        批量對三元組進行分類（優化性能）
        
        Args:
            triples: 三元組列表
            batch_size: 批次大小，默認為 5
            
        Returns:
            分類後的三元組列表
        """
        if not triples:
            return []

        # 如果三元組數量較少，直接分類
        if len(triples) <= batch_size:
            return await self.classify_triples(triples)

        # 分批處理
        classified_triples = []
        for i in range(0, len(triples), batch_size):
            batch = triples[i : i + batch_size]
            batch_classified = await self.classify_triples(batch)
            classified_triples.extend(batch_classified)

        return classified_triples

