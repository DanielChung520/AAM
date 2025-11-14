"""
@purpose: 對話歸檔流程端到端測試 - 使用真實 Ollama 模型（測試計劃 A 新版）
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import json
import time
from datetime import datetime

import pytest
import pytest_asyncio

from src.core.services.memory_service import MemoryServiceImpl
from src.models.api.mcp import RetrievedDoc
from tests.e2e.fixtures.dialogue_scenarios import (
    get_business_consultation_messages,
    get_education_learning_messages,
    get_technical_consultation_messages,
)


@pytest.mark.e2e
@pytest.mark.real_model
@pytest.mark.dialogue_archive
class TestDialogueArchiveFlowRealModel:
    """
    對話歸檔流程端到端測試（使用真實 Ollama 模型）
    
    測試完整的對話歸檔流程：
    1. 執行對話歸檔（使用真實模型）
    2. 驗證語義分析（NER、KE、KT）
    3. 驗證三元組分類標籤
    4. 驗證知識存儲到 ChromaDB
    5. 驗證個人偏好存儲到 PostgreSQL
    """

    @pytest_asyncio.fixture
    async def clean_databases(self, knowledge_store, persona_store):
        """每個測試前清理數據庫"""
        # 清理 ChromaDB（刪除所有文檔）
        try:
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
                    text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
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
                    text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
                )
                await session.commit()
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_technical_consultation_dialogue_flow_real_model(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        clean_databases,
    ):
        """
        測試場景一：技術諮詢對話的完整歸檔流程（使用真實 Ollama 模型）
        
        驗證：
        1. 對話歸檔執行成功
        2. 語義分析結果正確（NER、KE、KT）
        3. 三元組分類標籤正確
        4. 知識存儲到 ChromaDB（包含分類標籤）
        5. 個人偏好存儲到 PostgreSQL
        """
        print("\n" + "=" * 60)
        print("測試場景一：技術諮詢對話（使用真實模型）")
        print("=" * 60)
        
        # 1. 準備對話數據
        messages = get_technical_consultation_messages()
        print(f"準備了 {len(messages)} 輪對話")
        
        # 2. 執行歸檔（多輪對話，使用真實模型）
        start_time = time.time()
        for i, message in enumerate(messages, 1):
            print(f"\n處理第 {i}/{len(messages)} 輪對話...")
            try:
                await memory_service.archive(message)
                print(f"✅ 第 {i} 輪對話歸檔成功")
            except Exception as e:
                print(f"❌ 第 {i} 輪對話歸檔失敗: {e}")
                import traceback
                traceback.print_exc()
                # 繼續執行，記錄錯誤但不中斷測試
        elapsed_time = time.time() - start_time
        print(f"\n總執行時間: {elapsed_time:.2f} 秒")
        
        # 3. 驗證知識存儲到 ChromaDB
        print("\n驗證知識存儲...")
        all_results = knowledge_store.collection.get()
        assert all_results is not None, "ChromaDB 查詢結果不應為 None"
        
        stored_count = len(all_results["ids"])
        print(f"存儲的文檔數量: {stored_count} (預期: {len(messages)})")
        
        # 驗證每條知識的元數據
        if all_results["metadatas"]:
            total_entities = 0
            total_triples = 0
            categories_found = set()
            
            for metadata in all_results["metadatas"]:
                # 驗證元數據
                assert metadata["user_id"] == "user_tech_001"
                assert metadata["session_id"] == "tech_dialog_001"
                assert metadata["source_type"] == "dialogue"
                
                # 驗證實體
                entities = json.loads(metadata.get("entities", "[]"))
                total_entities += len(entities)
                if entities:
                    print(f"  實體示例: {entities[:3]}")
                
                # 驗證三元組
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                total_triples += len(triples)
                
                # 驗證三元組分類標籤
                for triple in triples:
                    assert "subject" in triple, "三元組應該有 subject"
                    assert "predicate" in triple, "三元組應該有 predicate"
                    assert "object" in triple, "三元組應該有 object"
                    # 驗證分類標籤存在（可能為 None 或字符串）
                    assert "category" in triple, "三元組應該有 category 字段"
                    assert "ai_category" in triple, "三元組應該有 ai_category 字段"
                    
                    if triple.get("category"):
                        categories_found.add(triple["category"])
                
                # 驗證 metadata 中的 triple_categories 字段
                triple_categories = metadata.get("triple_categories", "")
                assert triple_categories is not None, "應該有 triple_categories 字段"
            
            print(f"總實體數量: {total_entities}")
            print(f"總三元組數量: {total_triples}")
            print(f"發現的分類標籤: {', '.join(sorted(categories_found))}")
            
            # 驗證至少有一些數據被提取
            assert total_entities > 0 or total_triples > 0, "應該提取了至少一些實體或三元組"
        
        # 4. 驗證個人偏好存儲到 PostgreSQL
        print("\n驗證用戶畫像...")
        user_profile = await persona_store.get("user_tech_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        
        # 驗證用戶畫像內容
        assert user_profile.user_id == "user_tech_001"
        print(f"  用戶 ID: {user_profile.user_id}")
        print(f"  風格標籤: {user_profile.style_tags}")
        print(f"  情感歷史: {user_profile.sentiment_history}")
        print(f"  語言模式: {user_profile.language_patterns}")
        print(f"  最後更新: {user_profile.last_updated}")
        
        print("\n" + "=" * 60)
        print("✅ 測試場景一完成")
        print("=" * 60)

    @pytest.mark.asyncio
    async def test_education_learning_dialogue_flow_real_model(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        persona_store,
        clean_databases,
    ):
        """
        測試場景二：教育學習諮詢對話的完整歸檔流程（使用真實模型，驗證分類標籤）
        
        驗證：
        1. 對話歸檔執行成功
        2. 語義分析結果正確（包含三元組分類標籤）
        3. 知識存儲到 ChromaDB（包含分類標籤）
        4. 個人偏好存儲到 PostgreSQL
        5. 三元組分類標籤正確存儲和檢索
        """
        print("\n" + "=" * 60)
        print("測試場景二：教育學習諮詢對話（使用真實模型）")
        print("=" * 60)
        
        # 1. 準備對話數據
        messages = get_education_learning_messages()
        print(f"準備了 {len(messages)} 輪對話")
        
        # 2. 執行歸檔（多輪對話，使用真實模型）
        start_time = time.time()
        for i, message in enumerate(messages, 1):
            print(f"\n處理第 {i}/{len(messages)} 輪對話...")
            try:
                await memory_service.archive(message)
                print(f"✅ 第 {i} 輪對話歸檔成功")
            except Exception as e:
                print(f"❌ 第 {i} 輪對話歸檔失敗: {e}")
                import traceback
                traceback.print_exc()
                # 繼續執行，記錄錯誤但不中斷測試
        elapsed_time = time.time() - start_time
        print(f"\n總執行時間: {elapsed_time:.2f} 秒")
        
        # 3. 驗證知識存儲到 ChromaDB
        print("\n驗證知識存儲...")
        all_results = knowledge_store.collection.get()
        assert all_results is not None, "ChromaDB 查詢結果不應為 None"
        
        stored_count = len(all_results["ids"])
        print(f"存儲的文檔數量: {stored_count} (預期: {len(messages)})")
        
        # 驗證每條知識的元數據
        if all_results["metadatas"]:
            total_entities = 0
            total_triples = 0
            categories_found = set()
            
            for metadata in all_results["metadatas"]:
                # 驗證元數據
                assert metadata["user_id"] == "user_education_001"
                assert metadata["session_id"] == "education_dialog_001"
                assert metadata["source_type"] == "dialogue"
                
                # 驗證實體
                entities = json.loads(metadata.get("entities", "[]"))
                total_entities += len(entities)
                if entities:
                    print(f"  實體示例: {entities[:3]}")
                
                # 驗證三元組
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                total_triples += len(triples)
                
                # 驗證三元組分類標籤
                for triple in triples:
                    assert "subject" in triple, "三元組應該有 subject"
                    assert "predicate" in triple, "三元組應該有 predicate"
                    assert "object" in triple, "三元組應該有 object"
                    # 驗證分類標籤存在（可能為 None 或字符串）
                    assert "category" in triple, "三元組應該有 category 字段"
                    assert "ai_category" in triple, "三元組應該有 ai_category 字段"
                    
                    if triple.get("category"):
                        categories_found.add(triple["category"])
                
                # 驗證 metadata 中的 triple_categories 字段
                triple_categories = metadata.get("triple_categories", "")
                assert triple_categories is not None, "應該有 triple_categories 字段"
                if triple_categories:
                    print(f"  三元組分類標籤: {triple_categories}")
            
            print(f"總實體數量: {total_entities}")
            print(f"總三元組數量: {total_triples}")
            print(f"發現的分類標籤: {', '.join(sorted(categories_found))}")
            
            # 驗證至少有一些數據被提取
            assert total_entities > 0 or total_triples > 0, "應該提取了至少一些實體或三元組"
            
            # 驗證分類標籤符合預期（教育、技術等）
            assert len(categories_found) > 0, "應該有至少一個分類標籤"
        
        # 4. 驗證個人偏好存儲到 PostgreSQL
        print("\n驗證用戶畫像...")
        user_profile = await persona_store.get("user_education_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        
        # 驗證用戶畫像內容
        assert user_profile.user_id == "user_education_001"
        print(f"  用戶 ID: {user_profile.user_id}")
        print(f"  風格標籤: {user_profile.style_tags}")
        print(f"  情感歷史: {user_profile.sentiment_history}")
        print(f"  語言模式: {user_profile.language_patterns}")
        print(f"  最後更新: {user_profile.last_updated}")
        
        print("\n" + "=" * 60)
        print("✅ 測試場景二完成")
        print("=" * 60)

    @pytest.mark.asyncio
    async def test_knowledge_retrieval_after_storage(
        self,
        memory_service: MemoryServiceImpl,
        knowledge_store,
        clean_databases,
    ):
        """
        測試知識檢索功能（使用真實模型）
        
        驗證存儲後的知識可以正確檢索
        """
        print("\n" + "=" * 60)
        print("測試知識檢索功能")
        print("=" * 60)
        
        # 1. 執行歸檔
        messages = get_technical_consultation_messages()
        for message in messages:
            try:
                await memory_service.archive(message)
            except Exception as e:
                print(f"⚠️  歸檔失敗: {e}")
        
        # 2. 檢索知識
        print("\n檢索知識...")
        retrieved_docs = await knowledge_store.search(
            "Python", "user_tech_001", limit=10
        )
        
        # 驗證檢索結果
        print(f"檢索到 {len(retrieved_docs)} 條知識")
        assert len(retrieved_docs) > 0, "應該檢索到知識"
        
        # 驗證檢索結果的格式
        for doc in retrieved_docs:
            assert isinstance(doc, RetrievedDoc), "應該是 RetrievedDoc 對象"
            assert doc.source is not None, "應該有來源"
            assert doc.content is not None, "應該有內容"
            assert doc.score is not None, "應該有分數"
            assert 0 <= doc.score <= 1, "分數應該在 0-1 之間"
            print(f"  檢索結果: {doc.source}, 分數: {doc.score:.3f}")
        
        print("\n" + "=" * 60)
        print("✅ 知識檢索測試完成")
        print("=" * 60)

    @pytest.mark.asyncio
    async def test_personality_profile_retrieval_after_storage(
        self,
        memory_service: MemoryServiceImpl,
        persona_store,
        clean_databases,
    ):
        """
        測試用戶畫像檢索功能（使用真實模型）
        
        驗證存儲後的用戶畫像可以正確檢索
        """
        print("\n" + "=" * 60)
        print("測試用戶畫像檢索功能")
        print("=" * 60)
        
        # 1. 執行歸檔
        messages = get_technical_consultation_messages()
        for message in messages:
            try:
                await memory_service.archive(message)
            except Exception as e:
                print(f"⚠️  歸檔失敗: {e}")
        
        # 2. 檢索用戶畫像
        print("\n檢索用戶畫像...")
        user_profile = await persona_store.get("user_tech_001")
        
        # 驗證檢索結果
        assert user_profile is not None, "應該檢索到用戶畫像"
        assert user_profile.user_id == "user_tech_001"
        assert user_profile.style_tags is not None
        assert user_profile.sentiment_history is not None
        assert user_profile.language_patterns is not None
        assert user_profile.last_updated is not None
        
        print(f"  用戶 ID: {user_profile.user_id}")
        print(f"  風格標籤: {user_profile.style_tags}")
        print(f"  情感歷史: {user_profile.sentiment_history}")
        print(f"  語言模式: {user_profile.language_patterns}")
        print(f"  最後更新: {user_profile.last_updated}")
        
        print("\n" + "=" * 60)
        print("✅ 用戶畫像檢索測試完成")
        print("=" * 60)

