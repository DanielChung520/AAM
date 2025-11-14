"""
@purpose: 領域模型模塊導出
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from .database import KnowledgeAsset, UserProfileDB
from .dialogue import DialogueArchiveMessage
from .personality import PersonalityInsights
from .quality import QualityEvaluationResult

__all__ = [
    "DialogueArchiveMessage",
    "KnowledgeAsset",
    "UserProfileDB",
    "PersonalityInsights",
    "QualityEvaluationResult",
]

