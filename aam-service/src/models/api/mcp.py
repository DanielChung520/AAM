"""
@purpose: 定義 Model Context Protocol (MCP) 的數據模型，包括 PartialMCP 和 EnrichedMCP
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    """對話消息模型"""
    role: Literal["user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息內容")


class UserProfile(BaseModel):
    """用戶畫像模型（基礎版）"""
    user_id: str = Field(..., description="用戶 ID")


class UserProfileEnriched(UserProfile):
    """用戶畫像模型（豐富化版）"""
    long_term_style_tags: List[str] = Field(
        default_factory=list, description="長期風格標籤列表"
    )
    current_sentiment: str = Field(
        default="neutral", description="當前情感狀態"
    )


class SessionContext(BaseModel):
    """會話上下文模型"""
    session_id: str = Field(..., description="會話 ID")
    current_query: str = Field(..., description="當前查詢")
    short_term_memory: List[Message] = Field(
        default_factory=list, description="短期記憶（對話歷史）"
    )


class PartialMCP(BaseModel):
    """部分 MCP（請求體）- POST /v1/mcp/enrich"""
    user_profile: UserProfile = Field(..., description="用戶畫像")
    session_context: SessionContext = Field(..., description="會話上下文")


class Metadata(BaseModel):
    """元數據模型"""
    request_id: UUID = Field(default_factory=uuid4, description="請求 ID")
    aam_version: str = Field(default="1.0", description="AAM 版本號")


class RetrievedDoc(BaseModel):
    """檢索到的文檔模型"""
    source: str = Field(..., description="文檔來源")
    content: str = Field(..., description="文檔內容")
    score: float = Field(..., ge=0.0, le=1.0, description="相關性分數")


class KnowledgeTriple(BaseModel):
    """知識三元組模型"""
    subject: str = Field(..., description="主語")
    predicate: str = Field(..., description="謂語")
    object: str = Field(..., description="賓語")
    category: Optional[str] = Field(
        default=None, description="預定義分類標籤（中文）"
    )
    ai_category: Optional[str] = Field(
        default=None, description="AI 原始分類標籤"
    )


class RetrievedKnowledge(BaseModel):
    """檢索到的知識模型"""
    docs: List[RetrievedDoc] = Field(
        default_factory=list, description="相關文檔列表"
    )
    kg_triples: List[KnowledgeTriple] = Field(
        default_factory=list, description="知識圖譜三元組列表"
    )


class EnrichedMCP(BaseModel):
    """豐富化 MCP（響應體）- POST /v1/mcp/enrich"""
    metadata: Metadata = Field(default_factory=Metadata, description="元數據")
    user_profile: UserProfileEnriched = Field(..., description="豐富化後的用戶畫像")
    session_context: SessionContext = Field(..., description="會話上下文（原樣返回）")
    retrieved_knowledge: RetrievedKnowledge = Field(
        default_factory=RetrievedKnowledge, description="檢索到的知識"
    )

