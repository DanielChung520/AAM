"""
@purpose: Mock AI 分析模型實現，用於測試和開發階段（臨時實現）
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import logging
from datetime import datetime

from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = logging.getLogger(__name__)


class MockAnalysisModel(IAnalysisModel):
    """Mock AI 分析模型實現（臨時實現，用於測試和開發）"""

    async def extract_knowledge(
        self, text: str, user_id: str, session_id: str
    ) -> KnowledgeAsset:
        """
        提取知識（Mock 實現）

        Args:
            text: 輸入文本
            user_id: 用戶 ID
            session_id: 會話 ID

        Returns:
            知識資產對象（Mock 數據）
        """
        logger.warning(
            "使用 Mock 分析模型提取知識（臨時實現）",
            user_id=user_id,
            session_id=session_id,
            text_length=len(text),
        )

        # 返回基本的 Mock 知識資產
        return KnowledgeAsset(
            user_id=user_id,
            session_id=session_id,
            timestamp=int(datetime.utcnow().timestamp()),
            source_type="dialogue",
            entities=[],  # Mock: 空實體列表
            triples_json="[]",  # Mock: 空三元組列表
        )

    async def analyze_personality(self, text: str) -> PersonalityInsights:
        """
        分析用戶個性（Mock 實現）

        Args:
            text: 輸入文本

        Returns:
            個性分析結果（Mock 數據）
        """
        logger.warning(
            "使用 Mock 分析模型分析個性（臨時實現）",
            text_length=len(text),
        )

        # 返回基本的 Mock 個性分析結果
        return PersonalityInsights(
            style_tags={},  # Mock: 空風格標籤
            sentiment="neutral",  # Mock: 中性情感
            language_patterns=[],  # Mock: 空語言模式
            confidence_score=0.5,  # Mock: 中等置信度
        )

