"""
@purpose: 模型模塊的統一導出入口
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
# API 模型
from .api.mcp import (
    EnrichedMCP,
    KnowledgeTriple,
    Message,
    Metadata,
    PartialMCP,
    RetrievedDoc,
    RetrievedKnowledge,
    SessionContext,
    UserProfile,
    UserProfileEnriched,
)

# 領域模型
from .domain.database import KnowledgeAsset, UserProfileDB
from .domain.dialogue import DialogueArchiveMessage
from .domain.personality import PersonalityInsights

__all__ = [
    # API 模型
    "Message",
    "UserProfile",
    "UserProfileEnriched",
    "SessionContext",
    "PartialMCP",
    "Metadata",
    "RetrievedDoc",
    "KnowledgeTriple",
    "RetrievedKnowledge",
    "EnrichedMCP",
    # 領域模型
    "DialogueArchiveMessage",
    "KnowledgeAsset",
    "UserProfileDB",
    "PersonalityInsights",
]

