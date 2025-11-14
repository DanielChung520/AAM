"""
@purpose: 對話歸檔流程端到端測試 - 測試計劃 A
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
from datetime import datetime

import pytest
import pytest_asyncio

from src.core.services.memory_service import MemoryServiceImpl
from src.models.api.mcp import RetrievedDoc
from tests.e2e.fixtures.dialogue_scenarios import (
    get_business_consultation_messages,
    get_casual_dialogue_messages,
    get_education_learning_messages,
    get_technical_consultation_messages,
)


@pytest.mark.e2e
@pytest.mark.dialogue_archive
class TestDialogueArchiveFlow:
    """
    對話歸檔流程端到端測試
    
    測試完整的對話歸檔流程：
    1. 執行對話歸檔
    2. 驗證語義分析（NER、KE、KT）
    3. 驗證知識存儲到 ChromaDB
    4. 驗證個人偏好存儲到 PostgreSQL
    """

    @pytest_asyncio.fixture
    async def clean_databases(self, knowledge_store, persona_store):
        """每個測試前清理數據庫"""
        # 清理 ChromaDB（刪除所有文檔）
        try:
            # 獲取所有文檔 ID
            results = knowledge_store.collection.get()
            if results and results["ids"]:
                knowledge_store.collection.delete(ids=results["ids"])
        except Exception:
            pass
        
        # 清理 PostgreSQL（刪除測試用戶）
        try:
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import text
            async with AsyncSession(persona_store.engine) as session:
                await session.execute(
                    text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%'")
                )
                await session.commit()
        except Exception:
            pass
        
        yield
        
        # 測試後再次清理
        try:
            results = knowledge_store.collection.get()
            if results and results["ids"]:
                knowledge_store.collection.delete(ids=results["ids"])
        except Exception:
            pass
        
        try:
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import text
            async with AsyncSession(persona_store.engine) as session:
                await session.execute(
                    text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%'")
                )
                await session.commit()
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_technical_consultation_dialogue_flow(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試場景一：技術諮詢對話的完整歸檔流程
        
        驗證：
        1. 對話歸檔執行成功
        2. 語義分析結果正確
        3. 知識存儲到 ChromaDB
        4. 個人偏好存儲到 PostgreSQL
        """
        # 使用帶預設結果的 Mock 模型
        memory_service.analysis_model = mock_analysis_model_with_results
        
        # 1. 準備對話數據
        messages = get_technical_consultation_messages()
        
        # 2. 執行歸檔（多輪對話）
        for message in messages:
            await memory_service.archive(message)
        
        # 3. 驗證知識存儲到 ChromaDB
        # 檢索所有存儲的知識
        all_results = knowledge_store.collection.get()
        assert all_results is not None
        assert len(all_results["ids"]) == len(messages), "應該存儲了所有輪次的知識"
        
        # 驗證每條知識的元數據
        # 獲取所有文檔的元數據進行驗證
        if all_results["metadatas"]:
            for metadata in all_results["metadatas"]:
                # 驗證元數據
                assert metadata["user_id"] == "user_tech_001"
                assert metadata["session_id"] == "tech_dialog_001"
                assert metadata["source_type"] == "dialogue"
                
                # 驗證實體
                entities = json.loads(metadata.get("entities", "[]"))
                assert len(entities) > 0, "應該提取了實體"
                assert "Python" in entities, "應該包含 Python 實體"
                
                # 驗證三元組
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                assert len(triples) > 0, "應該提取了三元組"
        
        # 4. 驗證個人偏好存儲到 PostgreSQL
        user_profile = await persona_store.get("user_tech_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        
        # 驗證用戶畫像內容
        assert user_profile.user_id == "user_tech_001"
        assert user_profile.style_tags is not None
        assert len(user_profile.style_tags) > 0, "應該有風格標籤"
        assert user_profile.sentiment is not None, "應該有情感情緒"
        assert user_profile.language_patterns is not None
        assert len(user_profile.language_patterns) > 0, "應該有語言模式"
        
        # 驗證風格標籤包含技術相關標籤
        assert "technical" in user_profile.style_tags or any(
            "技术" in str(v) or "technical" in str(k).lower()
            for k, v in user_profile.style_tags.items()
        ), "應該包含技術相關的風格標籤"

    @pytest.mark.asyncio
    async def test_business_consultation_dialogue_flow(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試場景二：業務諮詢對話的完整歸檔流程
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_business_consultation_messages()
        
        # 執行歸檔
        for message in messages:
            await memory_service.archive(message)
        
        # 驗證知識存儲
        all_results = knowledge_store.collection.get()
        assert len(all_results["ids"]) == len(messages)
        
        # 驗證用戶畫像
        user_profile = await persona_store.get("user_business_001")
        assert user_profile is not None
        assert user_profile.user_id == "user_business_001"

    @pytest.mark.asyncio
    async def test_casual_dialogue_flow(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試場景三：日常對話的完整歸檔流程
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_casual_dialogue_messages()
        
        # 執行歸檔
        for message in messages:
            await memory_service.archive(message)
        
        # 驗證知識存儲
        all_results = knowledge_store.collection.get()
        assert len(all_results["ids"]) == len(messages)
        
        # 驗證用戶畫像
        user_profile = await persona_store.get("user_casual_001")
        assert user_profile is not None
        assert user_profile.user_id == "user_casual_001"

    @pytest.mark.asyncio
    async def test_multi_turn_dialogue_accumulation(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試多輪對話的數據累積
        
        驗證：
        1. 每輪對話的知識都正確存儲
        2. 用戶畫像在多輪對話後正確累積更新
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_technical_consultation_messages()
        
        # 執行第一輪對話
        await memory_service.archive(messages[0])
        
        # 驗證第一輪後的狀態
        profile_after_turn1 = await persona_store.get("user_tech_001")
        assert profile_after_turn1 is not None
        
        # 執行第二輪對話
        await memory_service.archive(messages[1])
        
        # 驗證第二輪後的狀態（應該累積更新）
        profile_after_turn2 = await persona_store.get("user_tech_001")
        assert profile_after_turn2 is not None
        assert (
            profile_after_turn2.last_updated >= profile_after_turn1.last_updated
        ), "應該更新了時間戳"
        
        # 執行第三輪對話
        await memory_service.archive(messages[2])
        
        # 驗證最終狀態
        all_results = knowledge_store.collection.get()
        assert len(all_results["ids"]) == 3, "應該存儲了 3 輪對話的知識"
        
        final_profile = await persona_store.get("user_tech_001")
        assert final_profile is not None
        assert (
            final_profile.last_updated >= profile_after_turn2.last_updated
        ), "應該再次更新了時間戳"

    @pytest.mark.asyncio
    async def test_semantic_analysis_results_verification(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試語義分析結果驗證
        
        驗證：
        1. NER 提取結果
        2. KE 提取結果
        3. KT 提取結果
        4. 個性分析結果
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_technical_consultation_messages()
        
        # 執行歸檔
        await memory_service.archive(messages[0])
        
        # 驗證存儲的知識包含語義分析結果
        all_results = knowledge_store.collection.get()
        assert len(all_results["ids"]) > 0
        
        # 獲取第一條知識的元數據
        metadata = all_results["metadatas"][0]
        
        # 驗證 NER（實體）
        entities = json.loads(metadata.get("entities", "[]"))
        assert len(entities) > 0, "應該提取了實體"
        assert isinstance(entities, list), "實體應該是列表"
        
        # 驗證 KT（三元組）
        triples_json = metadata.get("triples_json", "[]")
        triples = json.loads(triples_json)
        assert len(triples) > 0, "應該提取了三元組"
        assert isinstance(triples, list), "三元組應該是列表"
        
        # 驗證三元組結構
        for triple in triples:
            assert "subject" in triple, "三元組應該有 subject"
            assert "predicate" in triple, "三元組應該有 predicate"
            assert "object" in triple, "三元組應該有 object"

    @pytest.mark.asyncio
    async def test_knowledge_retrieval_after_storage(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試知識檢索功能
        
        驗證存儲後的知識可以正確檢索
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_technical_consultation_messages()
        
        # 執行歸檔
        for message in messages:
            await memory_service.archive(message)
        
        # 檢索知識
        retrieved_docs = await knowledge_store.search(
            "Python", "user_tech_001", limit=10
        )
        
        # 驗證檢索結果
        assert len(retrieved_docs) > 0, "應該檢索到知識"
        
        # 驗證檢索結果的格式
        for doc in retrieved_docs:
            assert isinstance(doc, RetrievedDoc), "應該是 RetrievedDoc 對象"
            assert doc.source is not None, "應該有來源"
            assert doc.content is not None, "應該有內容"
            assert doc.score is not None, "應該有分數"
            assert 0 <= doc.score <= 1, "分數應該在 0-1 之間"

    @pytest.mark.asyncio
    async def test_personality_profile_retrieval_after_storage(
        self,
        memory_service: MemoryServiceImpl,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試用戶畫像檢索功能
        
        驗證存儲後的用戶畫像可以正確檢索
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        messages = get_technical_consultation_messages()
        
        # 執行歸檔
        for message in messages:
            await memory_service.archive(message)
        
        # 檢索用戶畫像
        user_profile = await persona_store.get("user_tech_001")
        
        # 驗證檢索結果
        assert user_profile is not None, "應該檢索到用戶畫像"
        assert user_profile.user_id == "user_tech_001"
        assert user_profile.style_tags is not None
        assert user_profile.sentiment is not None
        assert user_profile.language_patterns is not None
        assert user_profile.last_updated is not None

    @pytest.mark.asyncio
    async def test_education_learning_dialogue_flow(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        mock_analysis_model_with_results,
        clean_databases,
    ):
        """
        測試場景四：教育學習諮詢對話的完整歸檔流程
        
        驗證：
        1. 對話歸檔執行成功
        2. 語義分析結果正確（包含三元組分類標籤）
        3. 知識存儲到 ChromaDB（包含分類標籤）
        4. 個人偏好存儲到 PostgreSQL
        5. 三元組分類標籤正確存儲和檢索
        """
        memory_service.analysis_model = mock_analysis_model_with_results
        
        # 1. 準備對話數據
        messages = get_education_learning_messages()
        
        # 2. 執行歸檔（多輪對話）
        for message in messages:
            await memory_service.archive(message)
        
        # 3. 驗證知識存儲到 ChromaDB
        all_results = knowledge_store.collection.get()
        assert all_results is not None
        assert len(all_results["ids"]) == len(messages), "應該存儲了所有輪次的知識"
        
        # 驗證每條知識的元數據
        if all_results["metadatas"]:
            for metadata in all_results["metadatas"]:
                # 驗證元數據
                assert metadata["user_id"] == "user_education_001"
                assert metadata["session_id"] == "education_dialog_001"
                assert metadata["source_type"] == "dialogue"
                
                # 驗證實體
                entities = json.loads(metadata.get("entities", "[]"))
                assert len(entities) > 0, "應該提取了實體"
                
                # 驗證三元組
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                assert len(triples) > 0, "應該提取了三元組"
                
                # 驗證三元組分類標籤
                for triple in triples:
                    assert "subject" in triple, "三元組應該有 subject"
                    assert "predicate" in triple, "三元組應該有 predicate"
                    assert "object" in triple, "三元組應該有 object"
                    # 驗證分類標籤存在（可能為 None 或字符串）
                    assert "category" in triple, "三元組應該有 category 字段"
                    assert "ai_category" in triple, "三元組應該有 ai_category 字段"
                
                # 驗證 metadata 中的 triple_categories 字段
                triple_categories = metadata.get("triple_categories", "")
                assert triple_categories is not None, "應該有 triple_categories 字段"
                # 如果有分類，應該是非空字符串
                if triple_categories:
                    categories_list = triple_categories.split(",")
                    assert len(categories_list) > 0, "應該有分類標籤"
        
        # 4. 驗證個人偏好存儲到 PostgreSQL
        user_profile = await persona_store.get("user_education_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        
        # 驗證用戶畫像內容
        assert user_profile.user_id == "user_education_001"
        assert user_profile.style_tags is not None
        assert len(user_profile.style_tags) > 0, "應該有風格標籤"
        assert user_profile.sentiment_history is not None
        assert len(user_profile.sentiment_history) > 0, "應該有情感歷史"
        assert user_profile.last_updated is not None, "應該有更新時間戳"

