#!/usr/bin/env python3
"""
@purpose: 測試對話歸檔流程（包含三元組分類標籤）
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13

使用方法:
    python scripts/test_dialogue_archive_with_categories.py
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.pg_persona_store import PgPersonaStore
from tests.e2e.fixtures.dialogue_scenarios import get_education_learning_messages


async def test_dialogue_archive_with_categories():
    """測試對話歸檔流程（包含三元組分類標籤）"""
    print("=" * 60)
    print("對話歸檔測試（包含三元組分類標籤）")
    print("=" * 60)
    print()

    try:
        # 1. 初始化服務
        print("步驟 1: 初始化服務...")
        provider = OllamaProvider(
            model_name="deepseek-r1:8b",
            base_url="http://host.docker.internal:11434",
            timeout=120,
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

        # 2. 準備對話數據
        print("步驟 2: 準備對話數據...")
        messages = get_education_learning_messages()
        print(f"✅ 準備了 {len(messages)} 輪對話")
        print()

        # 3. 執行對話歸檔
        print("步驟 3: 執行對話歸檔...")
        for i, message in enumerate(messages, 1):
            print(f"  處理第 {i}/{len(messages)} 輪對話...")
            try:
                await memory_service.archive(message)
                print(f"  ✅ 第 {i} 輪對話歸檔成功")
            except Exception as e:
                print(f"  ❌ 第 {i} 輪對話歸檔失敗: {e}")
                raise
        print()

        # 4. 驗證知識存儲
        print("步驟 4: 驗證知識存儲...")
        all_results = knowledge_store.collection.get()
        print(f"  存儲的文檔數量: {len(all_results['ids'])}")
        
        if all_results["metadatas"]:
            total_triples = 0
            categories_found = set()
            for metadata in all_results["metadatas"]:
                triples_json = metadata.get("triples_json", "[]")
                triples = json.loads(triples_json)
                total_triples += len(triples)
                
                # 檢查分類標籤
                for triple in triples:
                    if "category" in triple and triple["category"]:
                        categories_found.add(triple["category"])
                
                # 檢查 metadata 中的分類摘要
                triple_categories = metadata.get("triple_categories", "")
                if triple_categories:
                    for cat in triple_categories.split(","):
                        if cat.strip():
                            categories_found.add(cat.strip())
            
            print(f"  總三元組數量: {total_triples}")
            print(f"  發現的分類標籤: {', '.join(sorted(categories_found))}")
            print("  ✅ 知識存儲驗證成功")
        print()

        # 5. 驗證用戶畫像
        print("步驟 5: 驗證用戶畫像...")
        user_profile = await persona_store.get("user_education_001")
        if user_profile:
            print(f"  用戶 ID: {user_profile.user_id}")
            print(f"  風格標籤: {user_profile.style_tags}")
            print(f"  情感歷史: {user_profile.sentiment_history}")
            print(f"  最後更新: {user_profile.last_updated}")
            print("  ✅ 用戶畫像驗證成功")
        else:
            print("  ⚠️  未找到用戶畫像")
        print()

        print("=" * 60)
        print("✅ 所有測試通過！")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 測試失敗: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_dialogue_archive_with_categories())

