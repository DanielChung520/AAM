#!/usr/bin/env python3
"""
@purpose: Qwen Provider 數據驗證腳本
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13

使用方法:
    python scripts/verify_qwen_data.py

功能:
    - 檢查使用 Qwen Provider 提取的知識資產
    - 驗證 ChromaDB 中的元數據
    - 驗證 PostgreSQL 中的用戶畫像
    - 驗證數據一致性
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import get_settings
from src.infrastructure.database import (
    create_chromadb_client,
    create_postgres_engine,
    ChromaKnowledgeStore,
    PgPersonaStore,
)


async def verify_chromadb_data():
    """驗證 ChromaDB 中的數據"""
    print("\n" + "="*60)
    print("驗證 ChromaDB 數據")
    print("="*60)
    
    try:
        settings = get_settings()
        
        # 創建 ChromaDB 客戶端
        chroma_client = create_chromadb_client(
            host=settings.chromadb.host,
            port=settings.chromadb.port,
        )
        
        # 創建知識存儲
        knowledge_store = ChromaKnowledgeStore(
            client=chroma_client,
            collection_name=settings.chromadb.collection_name,
        )
        
        # 獲取所有文檔
        results = knowledge_store.collection.get()
        
        if not results or not results.get("ids"):
            print("⚠ ChromaDB 中沒有數據")
            return True
        
        ids = results["ids"]
        metadatas = results.get("metadatas", [])
        documents = results.get("documents", [])
        
        print(f"✓ 找到 {len(ids)} 個文檔")
        
        # 檢查使用 Qwen Provider 的數據
        qwen_count = 0
        for i, metadata in enumerate(metadatas):
            if metadata:
                # 檢查是否有 provider_type 標記（如果有的話）
                # 或者檢查 user_id 是否包含 qwen 關鍵字
                user_id = metadata.get("user_id", "")
                if "qwen" in user_id.lower():
                    qwen_count += 1
                    print(f"\n文檔 {i+1}:")
                    print(f"  - ID: {ids[i]}")
                    print(f"  - User ID: {user_id}")
                    print(f"  - Session ID: {metadata.get('session_id', 'N/A')}")
                    
                    # 檢查三元組
                    triples_json = metadata.get("triples_json", "[]")
                    try:
                        triples = json.loads(triples_json)
                        print(f"  - 三元組數量: {len(triples)}")
                        if triples:
                            print(f"  - 第一個三元組: {triples[0]}")
                    except:
                        pass
        
        if qwen_count > 0:
            print(f"\n✓ 找到 {qwen_count} 個使用 Qwen Provider 的文檔")
        else:
            print("\n⚠ 沒有找到使用 Qwen Provider 的文檔")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB 數據驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_postgres_data():
    """驗證 PostgreSQL 中的數據"""
    print("\n" + "="*60)
    print("驗證 PostgreSQL 數據")
    print("="*60)
    
    try:
        settings = get_settings()
        
        # 創建 PostgreSQL 引擎
        engine = create_postgres_engine(
            host=settings.postgres.host,
            port=settings.postgres.port,
            user=settings.postgres.user,
            password=settings.postgres.password,
            database=settings.postgres.database,
        )
        
        # 創建用戶畫像存儲
        persona_store = PgPersonaStore(engine=engine)
        
        # 查詢包含 qwen 的用戶 ID
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import text
        
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT user_id, style_tags, sentiment_history FROM user_profiles WHERE user_id LIKE '%qwen%'")
            )
            rows = result.fetchall()
        
        if not rows:
            print("⚠ PostgreSQL 中沒有找到使用 Qwen Provider 的用戶畫像")
            return True
        
        print(f"✓ 找到 {len(rows)} 個用戶畫像")
        
        for row in rows:
            user_id, style_tags, sentiment_history = row
            print(f"\n用戶: {user_id}")
            if style_tags:
                print(f"  - 風格標籤: {style_tags}")
            if sentiment_history:
                print(f"  - 情感歷史: {sentiment_history}")
        
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL 數據驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_data_consistency():
    """驗證數據一致性"""
    print("\n" + "="*60)
    print("驗證數據一致性")
    print("="*60)
    
    try:
        settings = get_settings()
        
        # 創建 ChromaDB 客戶端
        chroma_client = create_chromadb_client(
            host=settings.chromadb.host,
            port=settings.chromadb.port,
        )
        
        knowledge_store = ChromaKnowledgeStore(
            client=chroma_client,
            collection_name=settings.chromadb.collection_name,
        )
        
        # 獲取所有文檔
        results = knowledge_store.collection.get()
        
        if not results or not results.get("ids"):
            print("⚠ 沒有數據可驗證")
            return True
        
        metadatas = results.get("metadatas", [])
        
        # 檢查數據完整性
        issues = []
        for i, metadata in enumerate(metadatas):
            if metadata:
                user_id = metadata.get("user_id")
                session_id = metadata.get("session_id")
                triples_json = metadata.get("triples_json", "[]")
                
                # 檢查必需字段
                if not user_id:
                    issues.append(f"文檔 {i+1}: 缺少 user_id")
                if not session_id:
                    issues.append(f"文檔 {i+1}: 缺少 session_id")
                
                # 檢查三元組 JSON 格式
                try:
                    triples = json.loads(triples_json)
                    if not isinstance(triples, list):
                        issues.append(f"文檔 {i+1}: triples_json 不是列表")
                except:
                    issues.append(f"文檔 {i+1}: triples_json 格式錯誤")
        
        if issues:
            print(f"⚠ 發現 {len(issues)} 個數據一致性问题:")
            for issue in issues[:10]:  # 只顯示前 10 個
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... 還有 {len(issues) - 10} 個問題")
        else:
            print("✓ 數據一致性檢查通過")
        
        return True
        
    except Exception as e:
        print(f"✗ 數據一致性驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函數"""
    print("\n" + "="*60)
    print("Qwen Provider 數據驗證腳本")
    print("="*60)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 驗證 ChromaDB
    try:
        result1 = await verify_chromadb_data()
        results.append(("ChromaDB 數據驗證", result1))
    except Exception as e:
        print(f"\n✗ ChromaDB 驗證執行失敗: {e}")
        results.append(("ChromaDB 數據驗證", False))
    
    # 驗證 PostgreSQL
    try:
        result2 = await verify_postgres_data()
        results.append(("PostgreSQL 數據驗證", result2))
    except Exception as e:
        print(f"\n✗ PostgreSQL 驗證執行失敗: {e}")
        results.append(("PostgreSQL 數據驗證", False))
    
    # 驗證數據一致性
    try:
        result3 = await verify_data_consistency()
        results.append(("數據一致性驗證", result3))
    except Exception as e:
        print(f"\n✗ 數據一致性驗證執行失敗: {e}")
        results.append(("數據一致性驗證", False))
    
    # 輸出驗證結果摘要
    print("\n" + "="*60)
    print("驗證結果摘要")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n總計: {len(results)} 個驗證")
    print(f"通過: {passed}")
    print(f"失敗: {failed}")
    
    if failed == 0:
        print("\n✓ 所有驗證通過！")
        return 0
    else:
        print(f"\n✗ {failed} 個驗證失敗")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

