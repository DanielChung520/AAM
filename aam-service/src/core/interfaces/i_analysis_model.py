"""
@purpose: 定義 AI 分析模型的抽象接口，用於知識提取和個性分析
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights
from src.models.domain.quality import QualityEvaluationResult


class IAnalysisModel(ABC):
    """AI 分析模型抽象接口"""

    @abstractmethod
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
        """
        pass

    @abstractmethod
    async def analyze_personality(self, text: str) -> PersonalityInsights:
        """
        分析用戶個性
        
        Args:
            text: 輸入文本
            
        Returns:
            個性分析結果
        """
        pass

    async def check_available(self) -> bool:
        """
        檢查模型服務是否可用
        
        Returns:
            如果模型服務可用返回 True，否則返回 False
        """
        # 默認實現：假設模型可用
        # 具體實現類可以覆蓋此方法以提供真實的可用性檢查
        return True

    async def evaluate_quality(
        self, knowledge: KnowledgeAsset, threshold: Optional[float] = None
    ) -> Optional[QualityEvaluationResult]:
        """
        評估知識提取的質量（可選方法）
        
        Args:
            knowledge: 知識資產對象
            threshold: 質量閾值（可選）
            
        Returns:
            質量評估結果，如果模型不支持質量評估則返回 None
        """
        # 默認實現：返回 None，表示不支持質量評估
        # 具體實現類可以覆蓋此方法以提供質量評估
        return None

