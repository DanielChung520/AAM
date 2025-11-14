"""
@purpose: 統一模型服務，通過 Provider 進行模型調用，實現知識提取和個性分析
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-13
"""
import json
import logging
import re
from datetime import datetime
from typing import Optional

from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.core.interfaces.i_model_provider import IModelProvider
from src.infrastructure.ai.triple_classifier import TripleClassifier
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = logging.getLogger(__name__)


def extract_json_from_markdown(text: str) -> str:
    """
    從 Markdown 代碼塊中提取 JSON
    
    處理以下格式：
    - ```json\n{...}\n```
    - ```\n{...}\n```
    - 純 JSON 文本
    
    Args:
        text: 可能包含 Markdown 代碼塊的文本
        
    Returns:
        提取的 JSON 字符串
    """
    if not text:
        return ""
    
    # 移除首尾空白
    text = text.strip()
    
    # 嘗試匹配 Markdown 代碼塊（```json 或 ```）
    markdown_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(markdown_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 如果沒有代碼塊，嘗試找到 JSON 對象（從 { 開始到 } 結束）
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(0).strip()
    
    # 如果都沒有，返回原文本
    return text


class UnifiedModelService(IAnalysisModel):
    """
    統一模型服務
    
    通過 Provider 進行模型調用，實現知識提取和個性分析
    """

    def __init__(self, provider: IModelProvider):
        """
        初始化統一模型服務
        
        Args:
            provider: 模型服務提供商實例
        """
        self.provider = provider
        self.triple_classifier = TripleClassifier(provider)
        logger.info(
            "統一模型服務初始化成功",
            extra={
                "provider_type": provider.provider_type.value,
                "provider_config": provider.get_config(),
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
        if not await self.provider.check_available():
            logger.error(
                "模型服務不可用，無法提取知識",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "provider_type": self.provider.provider_type.value,
                },
            )
            raise RuntimeError("模型服務不可用")
        
        try:
            # 提取 NER
            entities = await self._extract_ner(text)
            
            # 提取 KT
            triples = await self._extract_kt(text)
            
            # 對三元組進行分類
            if triples:
                try:
                    classified_triples = await self.triple_classifier.classify_triples(
                        triples
                    )
                    triples = classified_triples
                    logger.debug(
                        "三元組分類完成",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "triple_count": len(triples),
                        },
                    )
                except Exception as e:
                    logger.warning(
                        f"三元組分類失敗，使用原始三元組: {e}",
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
                "知識提取成功",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "entity_count": len(entities),
                    "triple_count": len(triples),
                    "provider_type": self.provider.provider_type.value,
                },
            )
            
            return knowledge
        
        except Exception as e:
            logger.error(
                f"知識提取失敗: {e}",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "error": str(e),
                    "provider_type": self.provider.provider_type.value,
                },
            )
            raise

    async def _extract_ner(self, text: str) -> list[str]:
        """
        提取命名實體
        
        Args:
            text: 輸入文本
            
        Returns:
            實體列表
        """
        try:
            # 構建 NER Prompt
            ner_prompt = f"""你是一個專業的命名實體識別系統。請從文本中提取所有命名實體（人名、地名、組織名、產品名、日期、時間等）。

請從以下文本中提取命名實體：

文本：{text}

請以 JSON 格式返回，格式如下：
{{
  "entities": ["實體1", "實體2", ...]
}}"""
            
            # 調用 Provider
            result = await self.provider.generate(ner_prompt)
            
            # 從 Markdown 代碼塊中提取 JSON（如果有的話）
            json_text = extract_json_from_markdown(result)
            
            # 解析 JSON
            try:
                result_dict = json.loads(json_text)
                entities = result_dict.get("entities", [])
                if not isinstance(entities, list):
                    entities = []
                return entities
            except json.JSONDecodeError:
                # 如果返回的不是 JSON，嘗試提取實體
                logger.warning(
                    "NER 提取結果不是有效的 JSON，嘗試解析文本",
                    extra={"result": result[:100], "extracted_json": json_text[:100]},
                )
                # 簡單的文本解析（備用方案）
                return []
        
        except Exception as e:
            logger.warning(f"NER 提取失敗: {e}，返回空列表")
            return []

    async def _extract_kt(self, text: str) -> list[dict]:
        """
        提取知識三元組
        
        Args:
            text: 輸入文本
            
        Returns:
            三元組列表
        """
        try:
            # 構建 KT Prompt
            kt_prompt = f"""你是一個專業的知識三元組提取系統。請從文本中提取主體-謂詞-客體關係（三元組）。

請從以下文本中提取知識三元組：

文本：{text}

請以 JSON 格式返回，格式如下：
{{
  "triples": [
    {{"subject": "主體", "predicate": "謂詞", "object": "客體"}},
    ...
  ]
}}"""
            
            # 調用 Provider
            result = await self.provider.generate(kt_prompt)
            
            # 從 Markdown 代碼塊中提取 JSON（如果有的話）
            json_text = extract_json_from_markdown(result)
            
            # 解析 JSON
            try:
                result_dict = json.loads(json_text)
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
                    extra={"result": result[:100], "extracted_json": json_text[:100]},
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
        if not await self.provider.check_available():
            logger.error(
                "模型服務不可用，無法分析個性",
                extra={"provider_type": self.provider.provider_type.value},
            )
            raise RuntimeError("模型服務不可用")
        
        try:
            # 構建個性分析 Prompt
            personality_prompt = f"""你是一個專業的用戶個性分析系統。請分析文本中的語言風格、情感狀態和個性特徵。

請分析以下文本的個性特徵：

文本：{text}

請以 JSON 格式返回，格式如下：
{{
  "style_tags": {{"formal": 0.8, "casual": 0.2, ...}},
  "sentiment": "positive|negative|neutral",
  "language_patterns": ["模式1", "模式2", ...],
  "confidence_score": 0.85
}}"""
            
            # 調用 Provider
            result = await self.provider.generate(personality_prompt)
            
            # 從 Markdown 代碼塊中提取 JSON（如果有的話）
            json_text = extract_json_from_markdown(result)
            
            # 解析 JSON
            try:
                result_dict = json.loads(json_text)
                
                style_tags = result_dict.get("style_tags", {})
                if not isinstance(style_tags, dict):
                    style_tags = {}
                
                sentiment = result_dict.get("sentiment", "neutral")
                if sentiment not in ["positive", "negative", "neutral"]:
                    sentiment = "neutral"
                
                language_patterns = result_dict.get("language_patterns", [])
                if not isinstance(language_patterns, list):
                    language_patterns = []
                
                confidence_score = result_dict.get("confidence_score", 0.5)
                if not isinstance(confidence_score, (int, float)):
                    confidence_score = 0.5
                
                personality = PersonalityInsights(
                    style_tags=style_tags,
                    sentiment=sentiment,
                    language_patterns=language_patterns,
                    confidence_score=float(confidence_score),
                )
                
                logger.info(
                    "個性分析成功",
                    extra={
                        "sentiment": sentiment,
                        "confidence_score": confidence_score,
                        "provider_type": self.provider.provider_type.value,
                    },
                )
                
                return personality
            
            except json.JSONDecodeError as e:
                logger.error(
                    f"個性分析結果解析失敗: {e}",
                    extra={"result": result[:100], "extracted_json": json_text[:100]},
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
                f"個性分析失敗: {e}",
                extra={
                    "error": str(e),
                    "provider_type": self.provider.provider_type.value,
                },
            )
            raise RuntimeError(f"個性分析失敗: {e}") from e

    async def check_available(self) -> bool:
        """
        檢查模型服務是否可用
        
        Returns:
            如果模型服務可用返回 True，否則返回 False
        """
        return await self.provider.check_available()

