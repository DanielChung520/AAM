#!/usr/bin/env python3
"""
@purpose: 對話歸檔流程端到端測試 - 使用真實 Ollama 模型（測試計劃 A 新版）
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.pg_persona_store import PgPersonaStore
from src.config.settings import get_settings
from src.core.interfaces.i_model_provider import ModelProviderType
from tests.e2e.fixtures.dialogue_scenarios import (
    get_education_learning_messages,
    get_technical_consultation_messages,
)


async def clean_databases(knowledge_store, persona_store):
    """清理測試數據庫"""
    print("清理測試數據庫...")
    
    # 清理 ChromaDB
    try:
        results = knowledge_store.collection.get()
        if results and results["ids"]:
            knowledge_store.collection.delete(ids=results["ids"])
            print(f"  ✅ 刪除了 {len(results['ids'])} 條 ChromaDB 文檔")
    except Exception as e:
        print(f"  ⚠️  ChromaDB 清理失敗: {e}")
    
    # 清理 PostgreSQL
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import text
        async with AsyncSession(persona_store.engine) as session:
            result = await session.execute(
                text("DELETE FROM user_profiles WHERE user_id LIKE 'user_%' OR user_id LIKE 'test_%'")
            )
            await session.commit()
            print(f"  ✅ 刪除了 {result.rowcount} 條 PostgreSQL 用戶畫像")
    except Exception as e:
        print(f"  ⚠️  PostgreSQL 清理失敗: {e}")
    print()


async def test_technical_consultation_dialogue_flow():
    """測試場景一：技術諮詢對話的完整歸檔流程（使用真實 Ollama 模型）"""
    print("=" * 60)
    print("測試場景一：技術諮詢對話（使用真實模型）")
    print("=" * 60)
    print()
    
    settings = get_settings()
    
    try:
        # 初始化服務
        print("步驟 1: 初始化服務...")
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.OLLAMA,
            model_name=settings.model_service.model_name or "deepseek-r1:8b",
            api_base_url=settings.model_service.api_base_url or "http://host.docker.internal:11434",
            timeout=settings.model_service.timeout or 120,
        )
        unified_model = UnifiedModelService(provider)
        analysis_model = FallbackAnalysisModel(unified_model)
        knowledge_store = ChromaKnowledgeStore()
        persona_store = PgPersonaStore()
        memory_service = MemoryServiceImpl(
            knowledge_store=knowledge_store,
            persona_store=persona_store,
            analysis_model=analysis_model,
        )
        print("✅ 服務初始化成功")
        print()
        
        # 清理數據庫
        await clean_databases(knowledge_store, persona_store)
        
        # 準備對話數據
        print("步驟 2: 準備對話數據...")
        messages = get_technical_consultation_messages()
        print(f"✅ 準備了 {len(messages)} 輪對話")
        print()
        
        # 執行歸檔
        print("步驟 3: 執行對話歸檔（使用真實模型）...")
        print("注意：這可能需要較長時間（模型響應時間）...")
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
        elapsed_time = time.time() - start_time
        print(f"\n總執行時間: {elapsed_time:.2f} 秒")
        print()
        
        # 驗證知識存儲
        print("步驟 4: 驗證知識存儲...")
        all_results = knowledge_store.collection.get()
        assert all_results is not None, "ChromaDB 查詢結果不應為 None"
        
        stored_count = len(all_results["ids"])
        print(f"存儲的文檔數量: {stored_count} (預期: {len(messages)})")
        
        if all_results["metadatas"]:
            total_entities = 0
            total_triples = 0
            categories_found = set()
            
            for metadata in all_results["metadatas"]:
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
                    assert "category" in triple, "三元組應該有 category 字段"
                    assert "ai_category" in triple, "三元組應該有 ai_category 字段"
                    if triple.get("category"):
                        categories_found.add(triple["category"])
            
            print(f"總實體數量: {total_entities}")
            print(f"總三元組數量: {total_triples}")
            print(f"發現的分類標籤: {', '.join(sorted(categories_found))}")
            print("✅ 知識存儲驗證成功")
        print()
        
        # 驗證用戶畫像
        print("步驟 5: 驗證用戶畫像...")
        user_profile = await persona_store.get("user_tech_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        print(f"  用戶 ID: {user_profile.user_id}")
        print(f"  風格標籤: {user_profile.style_tags}")
        print(f"  情感歷史: {user_profile.sentiment_history}")
        print(f"  語言模式: {user_profile.language_patterns}")
        print("✅ 用戶畫像驗證成功")
        print()
        
        print("=" * 60)
        print("✅ 測試場景一完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 測試失敗: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


async def test_education_learning_dialogue_flow():
    """測試場景二：教育學習諮詢對話的完整歸檔流程（使用真實模型，驗證分類標籤）"""
    print("=" * 60)
    print("測試場景二：教育學習諮詢對話（使用真實模型）")
    print("=" * 60)
    print()
    
    settings = get_settings()
    
    try:
        # 初始化服務
        print("步驟 1: 初始化服務...")
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.OLLAMA,
            model_name=settings.model_service.model_name or "deepseek-r1:8b",
            api_base_url=settings.model_service.api_base_url or "http://host.docker.internal:11434",
            timeout=settings.model_service.timeout or 120,
        )
        unified_model = UnifiedModelService(provider)
        analysis_model = FallbackAnalysisModel(unified_model)
        knowledge_store = ChromaKnowledgeStore()
        persona_store = PgPersonaStore()
        memory_service = MemoryServiceImpl(
            knowledge_store=knowledge_store,
            persona_store=persona_store,
            analysis_model=analysis_model,
        )
        print("✅ 服務初始化成功")
        print()
        
        # 清理數據庫
        await clean_databases(knowledge_store, persona_store)
        
        # 準備對話數據
        print("步驟 2: 準備對話數據...")
        messages = get_education_learning_messages()
        print(f"✅ 準備了 {len(messages)} 輪對話")
        print()
        
        # 執行歸檔
        print("步驟 3: 執行對話歸檔（使用真實模型）...")
        print("注意：這可能需要較長時間（模型響應時間）...")
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
        elapsed_time = time.time() - start_time
        print(f"\n總執行時間: {elapsed_time:.2f} 秒")
        print()
        
        # 驗證知識存儲
        print("步驟 4: 驗證知識存儲（包含分類標籤）...")
        all_results = knowledge_store.collection.get()
        assert all_results is not None, "ChromaDB 查詢結果不應為 None"
        
        stored_count = len(all_results["ids"])
        print(f"存儲的文檔數量: {stored_count} (預期: {len(messages)})")
        
        if all_results["metadatas"]:
            total_entities = 0
            total_triples = 0
            categories_found = set()
            
            for metadata in all_results["metadatas"]:
                # 驗證實體
                entities = json.loads(metadata.get("entities", "[]"))
                total_entities += len(entities)
                
                # 驗證三元組
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                total_triples += len(triples)
                
                # 驗證三元組分類標籤
                for triple in triples:
                    assert "category" in triple, "三元組應該有 category 字段"
                    assert "ai_category" in triple, "三元組應該有 ai_category 字段"
                    if triple.get("category"):
                        categories_found.add(triple["category"])
            
            print(f"總實體數量: {total_entities}")
            print(f"總三元組數量: {total_triples}")
            print(f"發現的分類標籤: {', '.join(sorted(categories_found))}")
            assert len(categories_found) > 0, "應該有至少一個分類標籤"
            print("✅ 知識存儲驗證成功（包含分類標籤）")
        print()
        
        # 驗證用戶畫像
        print("步驟 5: 驗證用戶畫像...")
        user_profile = await persona_store.get("user_education_001")
        assert user_profile is not None, "應該存儲了用戶畫像"
        print(f"  用戶 ID: {user_profile.user_id}")
        print(f"  風格標籤: {user_profile.style_tags}")
        print(f"  情感歷史: {user_profile.sentiment_history}")
        print("✅ 用戶畫像驗證成功")
        print()
        
        print("=" * 60)
        print("✅ 測試場景二完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 測試失敗: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函數"""
    print("=" * 60)
    print("對話歸檔流程端到端測試（使用真實 Ollama 模型）")
    print("=" * 60)
    print()
    
    results = []
    
    # 執行測試場景一
    result1 = await test_technical_consultation_dialogue_flow()
    results.append(("技術諮詢對話", result1))
    
    print("\n" + "=" * 60)
    print("等待 5 秒後執行下一個測試...")
    print("=" * 60)
    await asyncio.sleep(5)
    
    # 執行測試場景二
    result2 = await test_education_learning_dialogue_flow()
    results.append(("教育學習諮詢對話", result2))
    
    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("✅ 所有測試通過！")
    else:
        print("❌ 部分測試失敗")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

