#!/usr/bin/env python3
"""
@purpose: ChromaDB 連接測試腳本
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
@usage: python3 scripts/test_chromadb_connection.py
"""
import sys
import traceback
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError as e:
    print(f"❌ 導入 chromadb 失敗: {e}")
    print("請確保已安裝 chromadb: pip install chromadb")
    sys.exit(1)

try:
    from src.config.settings import get_settings
except ImportError as e:
    print(f"❌ 導入設置模塊失敗: {e}")
    print("請確保在項目根目錄運行此腳本，且 PYTHONPATH 已正確設置")
    sys.exit(1)


def test_chromadb_connection(
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: int = 10,
) -> bool:
    """
    測試 ChromaDB 連接
    
    Args:
        host: ChromaDB 主機地址，如果為 None 則從配置讀取
        port: ChromaDB 端口，如果為 None 則從配置讀取
        timeout: 連接超時時間（秒）
        
    Returns:
        如果連接成功返回 True，否則返回 False
    """
    try:
        # 獲取配置
        settings = get_settings()
        chromadb_settings = settings.chromadb
        
        # 使用提供的參數或從配置讀取
        test_host = host or chromadb_settings.chromadb_host
        test_port = port or chromadb_settings.chromadb_port
        
        print(f"\n{'='*60}")
        print("ChromaDB 連接測試")
        print(f"{'='*60}")
        print(f"主機: {test_host}")
        print(f"端口: {test_port}")
        print(f"URL: http://{test_host}:{test_port}")
        print(f"集合名稱: {chromadb_settings.chromadb_collection_name}")
        print(f"{'='*60}\n")
        
        # 創建客戶端
        print("1. 正在創建 ChromaDB 客戶端...")
        client = chromadb.HttpClient(
            host=test_host,
            port=test_port,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        print("   ✅ 客戶端創建成功")
        
        # 測試連接（獲取用戶身份）
        print("\n2. 正在測試連接...")
        identity = client.get_user_identity()
        print("   ✅ 連接成功")
        print(f"   - Tenant: {identity.tenant}")
        print(f"   - Databases: {identity.databases}")
        
        # 列出所有集合
        print("\n3. 正在列出集合...")
        collections = client.list_collections()
        print(f"   ✅ 找到 {len(collections)} 個集合:")
        for col in collections:
            count = col.count()
            print(f"      - {col.name} (ID: {col.id}, 文檔數: {count})")
        
        # 檢查目標集合是否存在
        print(f"\n4. 正在檢查目標集合 '{chromadb_settings.chromadb_collection_name}'...")
        target_collection = None
        for col in collections:
            if col.name == chromadb_settings.chromadb_collection_name:
                target_collection = col
                break
        
        if target_collection:
            print(f"   ✅ 目標集合存在")
            print(f"      - 文檔數: {target_collection.count()}")
        else:
            print(f"   ⚠️  目標集合不存在（將在首次使用時自動創建）")
        
        # 測試基本操作（如果集合存在）
        if target_collection:
            print(f"\n5. 正在測試基本操作...")
            try:
                # 嘗試獲取一些文檔（如果有的話）
                results = target_collection.get(limit=1)
                if results and results.get("ids"):
                    print(f"   ✅ 可以讀取文檔（找到 {len(results['ids'])} 個文檔）")
                else:
                    print(f"   ✅ 集合為空（正常，如果尚未存儲數據）")
            except Exception as e:
                print(f"   ⚠️  讀取文檔時發生錯誤: {e}")
        
        print(f"\n{'='*60}")
        print("✅ ChromaDB 連接測試通過")
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("❌ ChromaDB 連接測試失敗")
        print(f"{'='*60}")
        print(f"錯誤類型: {type(e).__name__}")
        print(f"錯誤信息: {str(e)}")
        print(f"\n完整堆棧跟踪:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return False


def test_network_connectivity(host: str, port: int) -> bool:
    """
    測試網絡連接性（不使用 ChromaDB 客戶端）
    
    Args:
        host: 主機地址
        port: 端口
        
    Returns:
        如果連接成功返回 True，否則返回 False
    """
    import socket
    
    print(f"\n測試網絡連接性: {host}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((host, port))
        s.close()
        
        if result == 0:
            print(f"   ✅ 網絡連接成功")
            return True
        else:
            print(f"   ❌ 網絡連接失敗 (錯誤碼: {result})")
            return False
    except Exception as e:
        print(f"   ❌ 網絡連接異常: {e}")
        return False


def main():
    """主函數"""
    print("\n" + "="*60)
    print("ChromaDB 連接測試工具")
    print("="*60)
    
    # 獲取配置
    try:
        settings = get_settings()
        chromadb_settings = settings.chromadb
        host = chromadb_settings.chromadb_host
        port = chromadb_settings.chromadb_port
    except Exception as e:
        print(f"❌ 無法讀取配置: {e}")
        sys.exit(1)
    
    # 測試網絡連接性
    print("\n步驟 0: 測試網絡連接性")
    network_ok = test_network_connectivity(host, port)
    
    if not network_ok:
        print("\n⚠️  網絡連接失敗，但繼續嘗試 ChromaDB 連接（可能是防火牆問題）")
    
    # 測試 ChromaDB 連接
    success = test_chromadb_connection(host=host, port=port)
    
    if success:
        print("✅ 所有測試通過")
        sys.exit(0)
    else:
        print("❌ 測試失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()

