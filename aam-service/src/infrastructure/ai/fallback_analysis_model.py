"""
@purpose: 降級策略分析模型，實現多層級降級邏輯（EB-mM → Ollama 本地模型 → LLM 抽象層）
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-13
"""
import logging
from typing import Optional

import structlog

from src.config.settings import AISettings
from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = structlog.get_logger(__name__)


class FallbackAnalysisModel(IAnalysisModel):
    """
    降級策略分析模型
    
    實現多層級降級策略：
    1. 優先級 1: EB-mM (Enterprise Bot mini-Model)
    2. 優先級 2: Ollama 本地模型
    3. 優先級 3: LLM 抽象層（通過 UnifiedModelService + Provider，可以是 Qwen、Ollama 或其他）
    
    降級邏輯：
    - 嘗試 EB-mM → 評估質量 → 不達標則降級
    - 嘗試 Ollama 本地模型 → 評估質量 → 不達標則降級
    - 嘗試 LLM 抽象層 → 直接使用（最後保障，不評估質量）
    """

    def __init__(
        self,
        eb_mm_model: Optional[IAnalysisModel] = None,
        ollama_local_model: Optional[IAnalysisModel] = None,
        llm_model: Optional[IAnalysisModel] = None,
        quality_evaluator: Optional[QualityEvaluator] = None,
        settings: Optional[AISettings] = None,
    ):
        """
        初始化降級策略分析模型
        
        Args:
            eb_mm_model: EB-mM 模型實例（優先級 1）
            ollama_local_model: Ollama 本地模型實例（優先級 2）
            llm_model: LLM 抽象層模型實例（優先級 3）
            quality_evaluator: 質量評估器實例
            settings: AI 配置設置
        """
        self.eb_mm_model = eb_mm_model
        self.ollama_local_model = ollama_local_model
        self.llm_model = llm_model
        self.settings = settings or AISettings()
        
        # 創建質量評估器
        self.quality_evaluator = quality_evaluator or QualityEvaluator(
            quality_threshold=self.settings.quality_threshold
        )
        
        logger.info(
            "降級策略分析模型已初始化",
            eb_mm_enabled=eb_mm_model is not None,
            ollama_local_enabled=ollama_local_model is not None,
            llm_enabled=llm_model is not None,
            quality_threshold=self.settings.quality_threshold,
            quality_evaluation_enabled=self.settings.quality_evaluation_enabled,
        )

    async def extract_knowledge(
        self, text: str, user_id: str, session_id: str
    ) -> KnowledgeAsset:
        """
        提取知識（使用降級策略）
        
        Args:
            text: 輸入文本
            user_id: 用戶 ID
            session_id: 會話 ID
            
        Returns:
            知識資產對象
        """
        # 嘗試優先級 1: Eb-MM
        if self.eb_mm_model is not None:
            try:
                if await self.eb_mm_model.check_available():
                    logger.debug(
                        "嘗試使用 Eb-MM 模型提取知識",
                        user_id=user_id,
                        session_id=session_id,
                    )
                    
                    knowledge = await self.eb_mm_model.extract_knowledge(
                        text, user_id, session_id
                    )
                    
                    # 評估質量
                    if self.settings.quality_evaluation_enabled:
                        quality_result = self.quality_evaluator.evaluate(
                            knowledge, threshold=self.settings.quality_threshold
                        )
                        
                        if quality_result.meets_threshold:
                            logger.info(
                                "Eb-MM 模型提取成功，質量達標",
                                user_id=user_id,
                                session_id=session_id,
                                quality_score=quality_result.overall_score,
                                threshold=self.settings.quality_threshold,
                            )
                            return knowledge
                        else:
                            logger.warning(
                                "Eb-MM 模型提取質量不達標，降級到下一個模型",
                                user_id=user_id,
                                session_id=session_id,
                                quality_score=quality_result.overall_score,
                                threshold=self.settings.quality_threshold,
                            )
                    else:
                        # 如果未啟用質量評估，直接返回
                        logger.info(
                            "Eb-MM 模型提取成功（質量評估已禁用）",
                            user_id=user_id,
                            session_id=session_id,
                        )
                        return knowledge
                        
            except Exception as e:
                logger.warning(
                    "Eb-MM 模型提取失敗，降級到下一個模型",
                    user_id=user_id,
                    session_id=session_id,
                    error=str(e),
                    exc_info=e,
                )
        
        # 嘗試優先級 2: Ollama 本地模型
        if self.ollama_local_model is not None:
            try:
                if await self.ollama_local_model.check_available():
                    logger.debug(
                        "嘗試使用 Ollama 本地模型提取知識",
                        user_id=user_id,
                        session_id=session_id,
                    )
                    
                    knowledge = await self.ollama_local_model.extract_knowledge(
                        text, user_id, session_id
                    )
                    
                    # 評估質量
                    if self.settings.quality_evaluation_enabled:
                        quality_result = self.quality_evaluator.evaluate(
                            knowledge, threshold=self.settings.quality_threshold
                        )
                        
                        if quality_result.meets_threshold:
                            logger.info(
                                "Ollama 本地模型提取成功，質量達標",
                                user_id=user_id,
                                session_id=session_id,
                                quality_score=quality_result.overall_score,
                                threshold=self.settings.quality_threshold,
                            )
                            return knowledge
                        else:
                            logger.warning(
                                "Ollama 本地模型提取質量不達標，降級到 LLM 抽象層",
                                user_id=user_id,
                                session_id=session_id,
                                quality_score=quality_result.overall_score,
                                threshold=self.settings.quality_threshold,
                            )
                    else:
                        # 如果未啟用質量評估，直接返回
                        logger.info(
                            "Ollama 本地模型提取成功（質量評估已禁用）",
                            user_id=user_id,
                            session_id=session_id,
                        )
                        return knowledge
                        
            except Exception as e:
                logger.warning(
                    "Ollama 本地模型提取失敗，降級到 LLM 抽象層",
                    user_id=user_id,
                    session_id=session_id,
                    error=str(e),
                    exc_info=e,
                )
        
        # 嘗試優先級 3: LLM 抽象層（最後保障，不評估質量）
        if self.llm_model is not None:
            try:
                if await self.llm_model.check_available():
                    logger.debug(
                        "嘗試使用 LLM 抽象層提取知識（最後保障）",
                        user_id=user_id,
                        session_id=session_id,
                    )
                    
                    knowledge = await self.llm_model.extract_knowledge(
                        text, user_id, session_id
                    )
                    
                    logger.info(
                        "LLM 抽象層提取成功（最後保障）",
                        user_id=user_id,
                        session_id=session_id,
                    )
                    return knowledge
                    
            except Exception as e:
                logger.error(
                    "LLM 抽象層提取失敗（所有模型都失敗）",
                    user_id=user_id,
                    session_id=session_id,
                    error=str(e),
                    exc_info=e,
                )
        
        # 所有模型都不可用或失敗，返回空結果
        logger.error(
            "所有模型都不可用或失敗，返回空知識資產",
            user_id=user_id,
            session_id=session_id,
        )
        
        # 返回一個空的知識資產（作為最後的降級）
        from datetime import datetime
        
        return KnowledgeAsset(
            user_id=user_id,
            session_id=session_id,
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )

    async def analyze_personality(self, text: str) -> PersonalityInsights:
        """
        分析用戶個性（使用降級策略）
        
        Args:
            text: 輸入文本
            
        Returns:
            個性分析結果
        """
        # 嘗試優先級 1: Eb-MM
        if self.eb_mm_model is not None:
            try:
                if await self.eb_mm_model.check_available():
                    logger.debug("嘗試使用 Eb-MM 模型分析個性")
                    return await self.eb_mm_model.analyze_personality(text)
            except Exception as e:
                logger.warning(
                    "Eb-MM 模型個性分析失敗，降級到下一個模型",
                    error=str(e),
                    exc_info=e,
                )
        
        # 嘗試優先級 2: Ollama 本地模型
        if self.ollama_local_model is not None:
            try:
                if await self.ollama_local_model.check_available():
                    logger.debug("嘗試使用 Ollama 本地模型分析個性")
                    return await self.ollama_local_model.analyze_personality(text)
            except Exception as e:
                logger.warning(
                    "Ollama 本地模型個性分析失敗，降級到 LLM 抽象層",
                    error=str(e),
                    exc_info=e,
                )
        
        # 嘗試優先級 3: LLM 抽象層
        if self.llm_model is not None:
            try:
                if await self.llm_model.check_available():
                    logger.debug("嘗試使用 LLM 抽象層分析個性（最後保障）")
                    return await self.llm_model.analyze_personality(text)
            except Exception as e:
                logger.error(
                    "LLM 抽象層個性分析失敗（所有模型都失敗）",
                    error=str(e),
                    exc_info=e,
                )
        
        # 所有模型都不可用或失敗，返回默認結果
        logger.error("所有模型都不可用或失敗，返回默認個性分析結果")
        return PersonalityInsights(
            style_tags={},
            sentiment="neutral",
            language_patterns=[],
            confidence_score=0.0,
        )

    async def check_available(self) -> bool:
        """
        檢查是否有任何模型可用
        
        Returns:
            如果至少有一個模型可用則返回 True
        """
        # 檢查各層級模型
        if self.eb_mm_model is not None:
            if await self.eb_mm_model.check_available():
                return True
        
        if self.ollama_local_model is not None:
            if await self.ollama_local_model.check_available():
                return True
        
        if self.llm_model is not None:
            if await self.llm_model.check_available():
                return True
        
        return False

