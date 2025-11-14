"""
@purpose: 測試 MCP 協議模型的數據驗證和序列化
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest
from pydantic import ValidationError

from src.models.api.mcp import (
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


class TestMessage:
    """測試 Message 模型"""

    def test_valid_message_user(self):
        """測試有效的用戶消息"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_valid_message_assistant(self):
        """測試有效的助手消息"""
        msg = Message(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_invalid_role(self):
        """測試無效的角色"""
        with pytest.raises(ValidationError):
            Message(role="invalid", content="test")


class TestUserProfile:
    """測試 UserProfile 模型"""

    def test_valid_user_profile(self):
        """測試有效的用戶畫像"""
        profile = UserProfile(user_id="user123")
        assert profile.user_id == "user123"

    def test_user_profile_enriched(self):
        """測試豐富化用戶畫像"""
        profile = UserProfileEnriched(
            user_id="user123",
            long_term_style_tags=["formal", "professional"],
            current_sentiment="positive",
        )
        assert profile.user_id == "user123"
        assert len(profile.long_term_style_tags) == 2
        assert profile.current_sentiment == "positive"


class TestSessionContext:
    """測試 SessionContext 模型"""

    def test_valid_session_context(self):
        """測試有效的會話上下文"""
        context = SessionContext(
            session_id="session123",
            current_query="What is AI?",
            short_term_memory=[
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Hi!"),
            ],
        )
        assert context.session_id == "session123"
        assert context.current_query == "What is AI?"
        assert len(context.short_term_memory) == 2


class TestPartialMCP:
    """測試 PartialMCP 模型"""

    def test_valid_partial_mcp(self):
        """測試有效的 PartialMCP"""
        mcp = PartialMCP(
            user_profile=UserProfile(user_id="user123"),
            session_context=SessionContext(
                session_id="session123", current_query="test"
            ),
        )
        assert mcp.user_profile.user_id == "user123"
        assert mcp.session_context.session_id == "session123"


class TestEnrichedMCP:
    """測試 EnrichedMCP 模型"""

    def test_valid_enriched_mcp(self):
        """測試有效的 EnrichedMCP"""
        mcp = EnrichedMCP(
            user_profile=UserProfileEnriched(
                user_id="user123",
                long_term_style_tags=["formal"],
                current_sentiment="positive",
            ),
            session_context=SessionContext(
                session_id="session123", current_query="test"
            ),
            retrieved_knowledge=RetrievedKnowledge(
                docs=[
                    RetrievedDoc(
                        source="doc1", content="content1", score=0.95
                    )
                ],
                kg_triples=[
                    KnowledgeTriple(
                        subject="AI", predicate="is", object="technology"
                    )
                ],
            ),
        )
        assert mcp.metadata.aam_version == "1.0"
        assert mcp.user_profile.user_id == "user123"
        assert len(mcp.retrieved_knowledge.docs) == 1
        assert len(mcp.retrieved_knowledge.kg_triples) == 1


class TestRetrievedDoc:
    """測試 RetrievedDoc 模型"""

    def test_valid_retrieved_doc(self):
        """測試有效的檢索文檔"""
        doc = RetrievedDoc(source="doc1", content="content", score=0.85)
        assert doc.source == "doc1"
        assert doc.content == "content"
        assert doc.score == 0.85

    def test_invalid_score_range(self):
        """測試無效的分數範圍"""
        with pytest.raises(ValidationError):
            RetrievedDoc(source="doc1", content="content", score=1.5)

        with pytest.raises(ValidationError):
            RetrievedDoc(source="doc1", content="content", score=-0.1)


class TestKnowledgeTriple:
    """測試 KnowledgeTriple 模型"""

    def test_valid_knowledge_triple(self):
        """測試有效的知識三元組"""
        triple = KnowledgeTriple(
            subject="Python", predicate="is_a", object="programming_language"
        )
        assert triple.subject == "Python"
        assert triple.predicate == "is_a"
        assert triple.object == "programming_language"

