"""
@purpose: 實現記憶服務的核心業務邏輯，協調數據存取和 AI 模型，提供 MCP 豐富化和對話歸檔功能
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.core.interfaces.i_knowledge_store import IKnowledgeStore
from src.core.interfaces.i_memory_service import IMemoryService
from src.core.interfaces.i_persona_store import IPersonaStore
from src.models.api.mcp import (
    EnrichedMCP,
    KnowledgeTriple,
    Metadata,
    PartialMCP,
    RetrievedKnowledge,
    UserProfileEnriched,
)
from src.models.domain.database import KnowledgeAsset, UserProfileDB
from src.models.domain.dialogue import DialogueArchiveMessage
from src.models.domain.personality import PersonalityInsights

# 配置日志
logger = logging.getLogger(__name__)


class MemoryServiceImpl(IMemoryService):
    """記憶服務實現類 - 核心業務邏輯層"""

    def __init__(
        self,
        knowledge_store: IKnowledgeStore,
        persona_store: IPersonaStore,
        analysis_model: IAnalysisModel,
    ):
        """
        初始化記憶服務
        
        Args:
            knowledge_store: 知識庫存儲接口實現
            persona_store: 用戶畫像存儲接口實現
            analysis_model: AI 分析模型接口實現
        """
        self.knowledge_store = knowledge_store
        self.persona_store = persona_store
        self.analysis_model = analysis_model

    async def enrich(self, mcp: PartialMCP) -> EnrichedMCP:
        """
        豐富化 MCP（同步 API 調用）
        
        Args:
            mcp: 部分 MCP（請求體）
            
        Returns:
            豐富化後的 MCP（響應體）
        """
        user_id = mcp.user_profile.user_id
        query = mcp.session_context.current_query
        session_id = mcp.session_context.session_id
        
        logger.info(
            f"Enriching MCP for user_id={user_id}, session_id={session_id}, query={query[:50]}..."
        )
        
        try:
            # 並行查詢知識庫和用戶畫像
            knowledge_docs, user_profile = await asyncio.gather(
                self.knowledge_store.search(query, user_id),
                self.persona_store.get(user_id),
                return_exceptions=True,
            )
            
            # 處理知識庫查詢結果
            if isinstance(knowledge_docs, Exception):
                logger.error(
                    f"Failed to search knowledge store: {knowledge_docs}",
                    exc_info=knowledge_docs,
                )
                knowledge_docs = []
            
            # 處理用戶畫像查詢結果
            if isinstance(user_profile, Exception):
                logger.error(
                    f"Failed to get user profile: {user_profile}",
                    exc_info=user_profile,
                )
                user_profile = None
            
            # 轉換用戶畫像為豐富化版本
            enriched_profile = self._convert_user_profile_to_enriched(
                user_profile, user_id
            )
            
            # 組裝檢索到的知識（目前 kg_triples 為空，因為接口不支持返回三元組）
            retrieved_knowledge = RetrievedKnowledge(
                docs=knowledge_docs,
                kg_triples=[],  # 當前接口不支持返回三元組
            )
            
            # 創建元數據
            metadata = Metadata()
            
            # 組裝並返回 EnrichedMCP
            enriched_mcp = EnrichedMCP(
                metadata=metadata,
                user_profile=enriched_profile,
                session_context=mcp.session_context,
                retrieved_knowledge=retrieved_knowledge,
            )
            
            logger.info(
                f"Successfully enriched MCP for user_id={user_id}, "
                f"found {len(knowledge_docs)} docs, "
                f"request_id={metadata.request_id}"
            )
            
            return enriched_mcp
            
        except Exception as e:
            logger.error(
                f"Unexpected error during enrich: {e}",
                exc_info=e,
                extra={"user_id": user_id, "session_id": session_id},
            )
            # 返回空結果而非拋出異常，確保 API 穩定性
            return EnrichedMCP(
                metadata=Metadata(),
                user_profile=UserProfileEnriched(user_id=user_id),
                session_context=mcp.session_context,
                retrieved_knowledge=RetrievedKnowledge(),
            )

    async def archive(self, message: DialogueArchiveMessage) -> None:
        """
        歸檔對話消息（異步處理）
        
        Args:
            message: 對話歸檔消息
        """
        user_id = message.user_id
        dialog_id = message.dialog_id
        session_id = dialog_id  # 使用 dialog_id 作為 session_id
        
        logger.info(
            f"Archiving dialogue for user_id={user_id}, dialog_id={dialog_id}, turn={message.turn}"
        )
        
        try:
            # 構建文本內容
            text_content = f"{message.user_query} {message.ai_response}"
            
            # 並行調用 AI 模型進行分析
            knowledge, personality = await asyncio.gather(
                self.analysis_model.extract_knowledge(
                    text_content, user_id, session_id
                ),
                self.analysis_model.analyze_personality(text_content),
                return_exceptions=True,
            )
            
            # 處理知識提取結果
            if isinstance(knowledge, Exception):
                logger.error(
                    f"Failed to extract knowledge: {knowledge}",
                    exc_info=knowledge,
                    extra={"user_id": user_id, "dialog_id": dialog_id},
                )
                # 知識提取失敗時，創建一個基本的 KnowledgeAsset
                knowledge = KnowledgeAsset(
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=int(message.timestamp.timestamp()),
                    source_type="dialogue",
                    entities=[],
                    triples_json="[]",
                )
            
            # 處理個性分析結果
            if isinstance(personality, Exception):
                logger.error(
                    f"Failed to analyze personality: {personality}",
                    exc_info=personality,
                    extra={"user_id": user_id, "dialog_id": dialog_id},
                )
                # 個性分析失敗時，創建一個基本的 PersonalityInsights
                personality = PersonalityInsights()
            
            # 保存知識資產
            try:
                # 使用 dialog_id + turn + timestamp 生成唯一的文檔 ID，避免覆蓋
                doc_id = f"{dialog_id}_turn{message.turn}_{int(message.timestamp.timestamp())}"
                await self.knowledge_store.save(knowledge, text_content, doc_id=doc_id)
                logger.debug(
                    f"Successfully saved knowledge asset for user_id={user_id}, dialog_id={dialog_id}, turn={message.turn}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to save knowledge asset: {e}",
                    exc_info=e,
                    extra={"user_id": user_id, "dialog_id": dialog_id},
                )
                # 繼續處理，不阻塞流程
            
            # 更新用戶畫像
            try:
                # 獲取現有用戶畫像
                existing_profile = await self.persona_store.get(user_id)
                
                # 合併新的個性分析結果
                updated_profile = self._merge_personality_insights(
                    existing_profile, personality, user_id
                )
                
                # 保存更新後的畫像
                await self.persona_store.save_or_update(updated_profile)
                logger.debug(
                    f"Successfully updated user profile for user_id={user_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to update user profile: {e}",
                    exc_info=e,
                    extra={"user_id": user_id, "dialog_id": dialog_id},
                )
                # 繼續處理，不阻塞流程
            
            logger.info(
                f"Successfully archived dialogue for user_id={user_id}, dialog_id={dialog_id}"
            )
            
        except Exception as e:
            logger.error(
                f"Unexpected error during archive: {e}",
                exc_info=e,
                extra={"user_id": user_id, "dialog_id": dialog_id},
            )
            # 記錄錯誤但允許繼續處理，避免阻塞消息隊列

    def _convert_user_profile_to_enriched(
        self, profile: Optional[UserProfileDB], user_id: str
    ) -> UserProfileEnriched:
        """
        將 UserProfileDB 轉換為 UserProfileEnriched
        
        Args:
            profile: 用戶畫像數據庫模型，如果為 None 則創建默認值
            user_id: 用戶 ID
            
        Returns:
            豐富化後的用戶畫像
        """
        if profile is None:
            # 如果用戶畫像不存在，返回默認值
            return UserProfileEnriched(
                user_id=user_id,
                long_term_style_tags=[],
                current_sentiment="neutral",
            )
        
        # 從 style_tags 字典中提取標籤列表（轉換為 long_term_style_tags）
        # 只包含計數 > 0 的標籤
        long_term_style_tags = [
            tag for tag, count in profile.style_tags.items() if count > 0
        ]
        
        # 從 sentiment_history 字典中確定當前情感（選擇計數最高的）
        current_sentiment = "neutral"
        if profile.sentiment_history:
            current_sentiment = max(
                profile.sentiment_history.items(), key=lambda x: x[1]
            )[0]
        
        return UserProfileEnriched(
            user_id=user_id,
            long_term_style_tags=long_term_style_tags,
            current_sentiment=current_sentiment,
        )

    def _merge_personality_insights(
        self,
        existing_profile: Optional[UserProfileDB],
        personality: PersonalityInsights,
        user_id: str,
    ) -> UserProfileDB:
        """
        合併 PersonalityInsights 到現有的 UserProfileDB
        
        Args:
            existing_profile: 現有用戶畫像，如果為 None 則創建新畫像
            personality: 新的個性分析結果
            user_id: 用戶 ID
            
        Returns:
            合併後的用戶畫像
        """
        if existing_profile is None:
            # 如果用戶畫像不存在，創建新畫像
            return UserProfileDB(
                user_id=user_id,
                style_tags=personality.style_tags.copy(),
                sentiment_history={
                    personality.sentiment: 1
                },  # 初始化情感歷史
                last_updated=datetime.utcnow(),
            )
        
        # 合併 style_tags（累加計數）
        merged_style_tags = existing_profile.style_tags.copy()
        for tag, count in personality.style_tags.items():
            merged_style_tags[tag] = merged_style_tags.get(tag, 0) + count
        
        # 合併 sentiment_history（累加計數）
        merged_sentiment_history = existing_profile.sentiment_history.copy()
        sentiment_key = personality.sentiment
        merged_sentiment_history[sentiment_key] = (
            merged_sentiment_history.get(sentiment_key, 0) + 1
        )
        
        # 更新時間戳
        return UserProfileDB(
            user_id=user_id,
            style_tags=merged_style_tags,
            sentiment_history=merged_sentiment_history,
            last_updated=datetime.utcnow(),
        )

