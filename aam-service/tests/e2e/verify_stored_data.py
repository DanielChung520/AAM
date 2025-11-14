#!/usr/bin/env python3
"""
@purpose: 驗證 ChromaDB 和 PostgreSQL 中存儲的數據
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13

使用方法:
    python scripts/verify_stored_data.py
"""
import json
import sys
from pathlib import Path
from collections import Counter

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.pg_persona_store import PgPersonaStore


def verify_chromadb_data():
    """驗證 ChromaDB 中的知識資產"""
    print("=" * 60)
    print("ChromaDB 數據驗證")
    print("=" * 60)
    print()

    try:
        knowledge_store = ChromaKnowledgeStore()
        all_results = knowledge_store.collection.get()

        if not all_results or not all_results["ids"]:
            print("⚠️  ChromaDB 中沒有數據")
            return

        doc_count = len(all_results["ids"])
        print(f"文檔數量: {doc_count}")
        print()

        # 統計信息
        total_entities = 0
        total_triples = 0
        categories_counter = Counter()
        user_ids = set()
        session_ids = set()

        if all_results["metadatas"]:
            for i, metadata in enumerate(all_results["metadatas"], 1):
                print(f"文檔 {i}:")
                print(f"  ID: {all_results['ids'][i-1]}")
                print(f"  用戶 ID: {metadata.get('user_id', 'N/A')}")
                print(f"  會話 ID: {metadata.get('session_id', 'N/A')}")
                print(f"  來源類型: {metadata.get('source_type', 'N/A')}")
                
                user_ids.add(metadata.get('user_id', ''))
                session_ids.add(metadata.get('session_id', ''))

                # 實體統計
                entities_str = metadata.get("entities", "")
                if entities_str:
                    entities = entities_str.split(",")
                    total_entities += len(entities)
                    print(f"  實體數量: {len(entities)}")
                    if len(entities) <= 5:
                        print(f"  實體列表: {', '.join(entities)}")
                    else:
                        print(f"  實體列表（前5個）: {', '.join(entities[:5])}...")

                # 三元組統計
                triples_json = metadata.get("triples_json", "[]")
                if triples_json and triples_json != "[]":
                    try:
                        triples = json.loads(triples_json)
                        total_triples += len(triples)
                        print(f"  三元組數量: {len(triples)}")

                        # 分類標籤統計
                        for triple in triples:
                            if isinstance(triple, dict):
                                category = triple.get("category")
                                if category:
                                    categories_counter[category] += 1
                        
                        # 顯示前3個三元組
                        if len(triples) > 0:
                            print("  三元組示例（前3個）:")
                            for j, triple in enumerate(triples[:3], 1):
                                subject = triple.get("subject", "N/A")
                                predicate = triple.get("predicate", "N/A")
                                object_val = triple.get("object", "N/A")
                                category = triple.get("category", "N/A")
                                print(f"    [{j}] ({subject}, {predicate}, {object_val}) [分類: {category}]")

                        # 分類摘要
                        triple_categories = metadata.get("triple_categories", "")
                        if triple_categories:
                            print(f"  分類摘要: {triple_categories}")
                    except json.JSONDecodeError:
                        print("  ⚠️  三元組 JSON 解析失敗")

                print()

        # 總體統計
        print("總體統計:")
        print(f"  文檔總數: {doc_count}")
        print(f"  實體總數: {total_entities}")
        print(f"  三元組總數: {total_triples}")
        print(f"  用戶數量: {len(user_ids)}")
        print(f"  會話數量: {len(session_ids)}")
        
        if categories_counter:
            print(f"  分類標籤分布:")
            for category, count in categories_counter.most_common():
                print(f"    {category}: {count}")

        print()
        print("✅ ChromaDB 數據驗證完成")

    except Exception as e:
        print(f"❌ ChromaDB 數據驗證失敗: {e}")
        import traceback
        traceback.print_exc()


async def verify_postgresql_data():
    """驗證 PostgreSQL 中的用戶畫像"""
    print("=" * 60)
    print("PostgreSQL 數據驗證")
    print("=" * 60)
    print()

    try:
        persona_store = PgPersonaStore()

        # 檢查測試用戶
        test_user_ids = [
            "user_tech_001",
            "user_business_001",
            "user_casual_001",
            "user_education_001",
        ]

        found_users = []
        for user_id in test_user_ids:
            user_profile = await persona_store.get(user_id)
            if user_profile:
                found_users.append(user_id)
                print(f"用戶: {user_id}")
                print(f"  風格標籤: {user_profile.style_tags}")
                print(f"  情感歷史: {user_profile.sentiment_history}")
                print(f"  最後更新: {user_profile.last_updated}")
                print()

        if found_users:
            print(f"✅ 找到 {len(found_users)} 個用戶畫像")
            print(f"  用戶列表: {', '.join(found_users)}")
        else:
            print("⚠️  未找到任何用戶畫像")

        print()
        print("✅ PostgreSQL 數據驗證完成")

    except Exception as e:
        print(f"❌ PostgreSQL 數據驗證失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函數"""
    print()
    verify_chromadb_data()
    print()
    
    import asyncio
    asyncio.run(verify_postgresql_data())
    
    print()
    print("=" * 60)
    print("✅ 所有數據驗證完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

