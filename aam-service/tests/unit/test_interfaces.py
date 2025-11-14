"""
@purpose: 測試所有抽象接口的定義和約束
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import pytest

from src.core.interfaces import (
    IAnalysisModel,
    IKnowledgeStore,
    IMemoryService,
    IPersonaStore,
)
from src.models.api.mcp import EnrichedMCP, PartialMCP
from src.models.api.mcp import RetrievedDoc
from src.models.domain.database import KnowledgeAsset, UserProfileDB
from src.models.domain.dialogue import DialogueArchiveMessage
from src.models.domain.personality import PersonalityInsights


class TestIMemoryService:
    """測試 IMemoryService 接口"""

    def test_cannot_instantiate_interface(self):
        """測試接口不能被直接實例化"""
        with pytest.raises(TypeError):
            IMemoryService()

    def test_interface_has_enrich_method(self):
        """測試接口包含 enrich 方法"""
        assert hasattr(IMemoryService, "enrich")
        assert callable(getattr(IMemoryService, "enrich"))

    def test_interface_has_archive_method(self):
        """測試接口包含 archive 方法"""
        assert hasattr(IMemoryService, "archive")
        assert callable(getattr(IMemoryService, "archive"))

    def test_implementation_must_implement_all_methods(self):
        """測試實現類必須實現所有抽象方法"""

        class IncompleteImplementation(IMemoryService):
            async def enrich(self, mcp: PartialMCP) -> EnrichedMCP:
                pass

        # 缺少 archive 方法，應該無法實例化
        with pytest.raises(TypeError):
            IncompleteImplementation()

        class CompleteImplementation(IMemoryService):
            async def enrich(self, mcp: PartialMCP) -> EnrichedMCP:
                pass

            async def archive(self, message: DialogueArchiveMessage) -> None:
                pass

        # 完整實現可以實例化
        impl = CompleteImplementation()
        assert isinstance(impl, IMemoryService)


class TestIKnowledgeStore:
    """測試 IKnowledgeStore 接口"""

    def test_cannot_instantiate_interface(self):
        """測試接口不能被直接實例化"""
        with pytest.raises(TypeError):
            IKnowledgeStore()

    def test_interface_has_save_method(self):
        """測試接口包含 save 方法"""
        assert hasattr(IKnowledgeStore, "save")
        assert callable(getattr(IKnowledgeStore, "save"))

    def test_interface_has_search_method(self):
        """測試接口包含 search 方法"""
        assert hasattr(IKnowledgeStore, "search")
        assert callable(getattr(IKnowledgeStore, "search"))

    def test_implementation_must_implement_all_methods(self):
        """測試實現類必須實現所有抽象方法"""

        class CompleteImplementation(IKnowledgeStore):
            async def save(self, knowledge: KnowledgeAsset) -> None:
                pass

            async def search(
                self, query: str, user_id: str, limit: int = 10
            ) -> list[RetrievedDoc]:
                return []

        impl = CompleteImplementation()
        assert isinstance(impl, IKnowledgeStore)


class TestIPersonaStore:
    """測試 IPersonaStore 接口"""

    def test_cannot_instantiate_interface(self):
        """測試接口不能被直接實例化"""
        with pytest.raises(TypeError):
            IPersonaStore()

    def test_interface_has_save_or_update_method(self):
        """測試接口包含 save_or_update 方法"""
        assert hasattr(IPersonaStore, "save_or_update")
        assert callable(getattr(IPersonaStore, "save_or_update"))

    def test_interface_has_get_method(self):
        """測試接口包含 get 方法"""
        assert hasattr(IPersonaStore, "get")
        assert callable(getattr(IPersonaStore, "get"))

    def test_implementation_must_implement_all_methods(self):
        """測試實現類必須實現所有抽象方法"""

        class CompleteImplementation(IPersonaStore):
            async def save_or_update(self, profile: UserProfileDB) -> None:
                pass

            async def get(self, user_id: str) -> UserProfileDB | None:
                return None

        impl = CompleteImplementation()
        assert isinstance(impl, IPersonaStore)


class TestIAnalysisModel:
    """測試 IAnalysisModel 接口"""

    def test_cannot_instantiate_interface(self):
        """測試接口不能被直接實例化"""
        with pytest.raises(TypeError):
            IAnalysisModel()

    def test_interface_has_extract_knowledge_method(self):
        """測試接口包含 extract_knowledge 方法"""
        assert hasattr(IAnalysisModel, "extract_knowledge")
        assert callable(getattr(IAnalysisModel, "extract_knowledge"))

    def test_interface_has_analyze_personality_method(self):
        """測試接口包含 analyze_personality 方法"""
        assert hasattr(IAnalysisModel, "analyze_personality")
        assert callable(getattr(IAnalysisModel, "analyze_personality"))

    def test_implementation_must_implement_all_methods(self):
        """測試實現類必須實現所有抽象方法"""

        class CompleteImplementation(IAnalysisModel):
            async def extract_knowledge(
                self, text: str, user_id: str, session_id: str
            ) -> KnowledgeAsset:
                return KnowledgeAsset(
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=0,
                    source_type="dialogue",
                )

            async def analyze_personality(self, text: str) -> PersonalityInsights:
                return PersonalityInsights()
            
            # check_available 和 evaluate_quality 有默認實現，不需要覆蓋

        impl = CompleteImplementation()
        assert isinstance(impl, IAnalysisModel)
        
        # 測試默認實現的方法
        import asyncio
        assert asyncio.run(impl.check_available()) is True
        
        # 測試 evaluate_quality 默認實現（需要先獲取知識資產）
        knowledge = asyncio.run(impl.extract_knowledge("test", "user", "session"))
        result = asyncio.run(impl.evaluate_quality(knowledge))
        assert result is None  # 默認實現返回 None


class TestInterfaceInheritance:
    """測試接口繼承關係"""

    def test_all_interfaces_are_abc(self):
        """測試所有接口都繼承自 ABC"""
        from abc import ABC

        assert issubclass(IMemoryService, ABC)
        assert issubclass(IKnowledgeStore, ABC)
        assert issubclass(IPersonaStore, ABC)
        assert issubclass(IAnalysisModel, ABC)

