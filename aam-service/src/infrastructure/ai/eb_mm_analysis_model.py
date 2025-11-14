"""
@purpose: EB-mM (Enterprise Bot mini-Model) 業務邏輯層實現，通過統一模型服務調用，實現知識提取和個性分析
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
from datetime import datetime
from typing import Optional

import structlog

from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.infrastructure.ai.triple_classifier import TripleClassifier
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = structlog.get_logger(__name__)


class EbMMAnalysisModel(IAnalysisModel):
    """
    EB-mM (Enterprise Bot mini-Model) 業務邏輯層
    
    通過統一模型服務調用 EB-mM 模型，實現：
    - NER (命名實體識別)
    - KE (知識提取)
    - KT (知識三元組提取)
    - 個性分析
    
    使用針對 EB-mM 優化的 Prompt 設計
    """

    def __init__(self, unified_model_service: UnifiedModelService):
        """
        初始化 EB-mM 分析模型
        
        Args:
            unified_model_service: 統一模型服務實例
        """
        self.model_service = unified_model_service
        self.triple_classifier = TripleClassifier(unified_model_service.provider)
        logger.info(
            "EB-mM 分析模型初始化成功",
            extra={
                "provider_type": unified_model_service.provider.provider_type.value,
            },
        )

    async def extract_knowledge(
        self, text: str, user_id: str, session_id: str
    ) -> KnowledgeAsset:
        """
        提取知識（NER, KE, KT）
        
        Args:
            text: 輸入文本
            user_id: 用戶 ID
            session_id: 會話 ID
            
        Returns:
            知識資產對象
            
        Raises:
            RuntimeError: 當服務不可用或提取失敗時
        """
        # 檢查服務是否可用
        if not await self.check_available():
            logger.error(
                "EB-mM 模型服務不可用，無法提取知識",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                },
            )
            raise RuntimeError("EB-mM 模型服務不可用")

        try:
            # 提取 NER
            entities = await self._extract_ner(text)
            
            # 提取 KE（知識點）
            key_points = await self._extract_ke(text)
            
            # 提取 KT（知識三元組）
            triples = await self._extract_kt(text)
            
            # 對三元組進行分類
            if triples:
                try:
                    classified_triples = await self.triple_classifier.classify_triples(
                        triples
                    )
                    triples = classified_triples
                    logger.debug(
                        "EB-mM 三元組分類完成",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "triple_count": len(triples),
                        },
                    )
                except Exception as e:
                    logger.warning(
                        f"EB-mM 三元組分類失敗，使用原始三元組: {e}",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "error": str(e),
                        },
                    )
                    # 分類失敗時，繼續使用原始三元組
            
            # 構建知識資產
            knowledge = KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=int(datetime.utcnow().timestamp()),
                source_type="dialogue",
                entities=entities,
                triples_json=json.dumps(triples, ensure_ascii=False),
            )
            
            logger.info(
                "EB-mM 知識提取成功",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "entity_count": len(entities),
                    "triple_count": len(triples),
                    "key_point_count": len(key_points),
                },
            )
            
            return knowledge
        
        except Exception as e:
            logger.error(
                f"EB-mM 知識提取失敗: {e}",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"EB-mM 知識提取失敗: {e}") from e

    async def _extract_ner(self, text: str) -> list[str]:
        """
        提取命名實體（NER）
        
        Args:
            text: 輸入文本
            
        Returns:
            實體列表
        """
        try:
            # 構建針對 EB-mM 優化的 NER Prompt
            ner_prompt = """你是一個專業的命名實體識別系統，專門針對企業對話場景進行優化。

請從以下文本中提取所有命名實體，包括但不限於：
- 人名（Person）
- 地名（Location）
- 組織名（Organization）
- 產品名（Product）
- 日期和時間（Date/Time）
- 技術術語（Technical Term）
- 業務概念（Business Concept）

文本: {text}

請以 JSON 格式返回，格式：
{{
    "entities": ["實體1", "實體2", ...],
    "entity_types": {{
        "實體1": "類型1",
        "實體2": "類型2"
    }},
    "confidence_scores": {{
        "實體1": 0.95,
        "實體2": 0.87
    }}
}}""".format(text=text)
            
            # 調用統一模型服務
            result = await self.model_service.provider.generate(ner_prompt)
            
            # 解析 JSON
            try:
                result_dict = json.loads(result)
                entities = result_dict.get("entities", [])
                if not isinstance(entities, list):
                    entities = []
                return entities
            except json.JSONDecodeError:
                logger.warning(
                    "NER 提取結果不是有效的 JSON，嘗試解析文本",
                    extra={"result": result[:100]},
                )
                return []
        
        except Exception as e:
            logger.warning(f"NER 提取失敗: {e}，返回空列表")
            return []

    async def _extract_ke(self, text: str) -> list[str]:
        """
        提取關鍵知識（KE）
        
        Args:
            text: 輸入文本
            
        Returns:
            知識點列表
        """
        try:
            # 構建針對 EB-mM 優化的 KE Prompt
            ke_prompt = """你是一個專業的知識提取系統，專門針對企業對話場景進行優化。

請從以下文本中提取關鍵知識，包括：
- 重要概念（Important Concepts）
- 關鍵事實（Key Facts）
- 核心觀點（Core Opinions）
- 業務規則（Business Rules）
- 決策依據（Decision Basis）

文本: {text}

請以 JSON 格式返回，格式：
{{
    "key_points": ["知識點1", "知識點2", ...],
    "concepts": ["概念1", "概念2", ...],
    "facts": ["事實1", "事實2", ...]
}}""".format(text=text)
            
            # 調用統一模型服務
            result = await self.model_service.provider.generate(ke_prompt)
            
            # 解析 JSON
            try:
                result_dict = json.loads(result)
                key_points = result_dict.get("key_points", [])
                concepts = result_dict.get("concepts", [])
                facts = result_dict.get("facts", [])
                
                # 合併所有知識點
                all_key_points = []
                if isinstance(key_points, list):
                    all_key_points.extend(key_points)
                if isinstance(concepts, list):
                    all_key_points.extend(concepts)
                if isinstance(facts, list):
                    all_key_points.extend(facts)
                
                return all_key_points
            except json.JSONDecodeError:
                logger.warning(
                    "KE 提取結果不是有效的 JSON，返回空列表",
                    extra={"result": result[:100]},
                )
                return []
        
        except Exception as e:
            logger.warning(f"KE 提取失敗: {e}，返回空列表")
            return []

    async def _extract_kt(self, text: str) -> list[dict]:
        """
        提取知識三元組（KT）
        
        Args:
            text: 輸入文本
            
        Returns:
            三元組列表
        """
        try:
            # 構建針對 EB-mM 優化的 KT Prompt
            kt_prompt = """你是一個專業的知識三元組提取系統，專門針對企業對話場景進行優化。

請從以下文本中提取知識三元組（主體-謂詞-客體關係）。

三元組格式要求：
- 主體（Subject）：實體或概念
- 謂詞（Predicate）：關係或動作
- 客體（Object）：實體、概念或值

文本: {text}

請以 JSON 格式返回，格式：
{{
    "triples": [
        {{"subject": "主體", "predicate": "謂詞", "object": "客體"}},
        ...
    ]
}}""".format(text=text)
            
            # 調用統一模型服務
            result = await self.model_service.provider.generate(kt_prompt)
            
            # 解析 JSON
            try:
                result_dict = json.loads(result)
                triples = result_dict.get("triples", [])
                if not isinstance(triples, list):
                    triples = []
                
                # 驗證三元組格式
                validated_triples = []
                for triple in triples:
                    if (
                        isinstance(triple, dict)
                        and "subject" in triple
                        and "predicate" in triple
                        and "object" in triple
                    ):
                        validated_triples.append(triple)
                
                return validated_triples
            except json.JSONDecodeError:
                logger.warning(
                    "KT 提取結果不是有效的 JSON，返回空列表",
                    extra={"result": result[:100]},
                )
                return []
        
        except Exception as e:
            logger.warning(f"KT 提取失敗: {e}，返回空列表")
            return []

    async def analyze_personality(self, text: str) -> PersonalityInsights:
        """
        分析用戶個性
        
        Args:
            text: 輸入文本
            
        Returns:
            個性分析結果
            
        Raises:
            RuntimeError: 當服務不可用或分析失敗時
        """
        # 檢查服務是否可用
        if not await self.check_available():
            logger.error("EB-mM 模型服務不可用，無法分析個性")
            raise RuntimeError("EB-mM 模型服務不可用")

        try:
            # 構建針對 EB-mM 優化的個性分析 Prompt
            personality_prompt = """你是一個專業的用戶個性分析系統，專門針對企業對話場景進行優化。

請分析以下文本的用戶個性和風格特徵：

文本: {text}

請分析以下維度：
1. 語言風格標籤（Style Tags）：formal, casual, technical, creative, analytical 等
2. 情感狀態（Sentiment）：positive, negative, neutral
3. 語言模式（Language Patterns）：簡潔、詳細、專業、友好等
4. 溝通風格（Communication Style）：直接、委婉、正式、隨意等

請以 JSON 格式返回，格式：
{{
    "style_tags": {{"formal": 0.8, "technical": 0.9, ...}},
    "sentiment": "positive|negative|neutral",
    "language_patterns": ["簡潔", "專業", ...],
    "tone": "專業|友好|正式|隨意",
    "confidence_score": 0.85
}}""".format(text=text)
            
            # 調用統一模型服務
            result = await self.model_service.provider.generate(personality_prompt)
            
            # 解析 JSON
            try:
                result_dict = json.loads(result)
                
                style_tags = result_dict.get("style_tags", {})
                if not isinstance(style_tags, dict):
                    style_tags = {}
                
                # 將 style_tags 轉換為整數（PersonalityInsights 要求）
                style_tags_int = {}
                for key, value in style_tags.items():
                    if isinstance(value, (int, float)):
                        # 將浮點數轉換為整數（0-100 範圍）
                        style_tags_int[key] = int(value * 100) if value <= 1.0 else int(value)
                    else:
                        style_tags_int[key] = 0
                
                sentiment = result_dict.get("sentiment", "neutral")
                if sentiment not in ["positive", "negative", "neutral"]:
                    sentiment = "neutral"
                
                language_patterns = result_dict.get("language_patterns", [])
                if not isinstance(language_patterns, list):
                    language_patterns = []
                
                confidence_score = result_dict.get("confidence_score", 0.5)
                if not isinstance(confidence_score, (int, float)):
                    confidence_score = 0.5
                confidence_score = float(confidence_score)
                if confidence_score > 1.0:
                    confidence_score = confidence_score / 100.0
                
                personality = PersonalityInsights(
                    style_tags=style_tags_int,
                    sentiment=sentiment,
                    language_patterns=language_patterns,
                    confidence_score=confidence_score,
                )
                
                logger.info(
                    "EB-mM 個性分析成功",
                    extra={
                        "sentiment": sentiment,
                        "confidence_score": confidence_score,
                    },
                )
                
                return personality
            
            except json.JSONDecodeError as e:
                logger.error(
                    f"個性分析結果解析失敗: {e}",
                    extra={"result": result[:100]},
                )
                # 返回默認值
                return PersonalityInsights(
                    style_tags={},
                    sentiment="neutral",
                    language_patterns=[],
                    confidence_score=0.5,
                )
        
        except Exception as e:
            logger.error(
                f"EB-mM 個性分析失敗: {e}",
                extra={"error": str(e)},
            )
            raise RuntimeError(f"EB-mM 個性分析失敗: {e}") from e

    async def check_available(self) -> bool:
        """
        檢查 EB-mM 模型服務是否可用
        
        Returns:
            如果模型服務可用返回 True，否則返回 False
        """
        return await self.model_service.check_available()

