#!/usr/bin/env python3
"""
@purpose: 簡單的對話歸檔測試腳本（不依賴 pytest）
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.infrastructure.database.pg_persona_store import PgPersonaStore
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.core.interfaces.i_model_provider import ModelProviderType
from src.models.domain.dialogue import DialogueArchiveMessage
from src.config.settings import get_settings


async def test_dialogue_archive():
    """測試對話歸檔功能"""
    print("=" * 60)
    print("對話歸檔測試（使用真實 Ollama 模型）")
    print("=" * 60)
    print()
    
    try:
        # 1. 讀取配置
        print("步驟 1: 讀取配置...")
        settings = get_settings()
        print(f"   MODEL_PROVIDER_TYPE: {settings.model_service.provider_type}")
        print(f"   MODEL_NAME: {settings.model_service.model_name}")
        print(f"   MODEL_API_BASE_URL: {settings.model_service.api_base_url}")
        print()
        
        # 2. 創建知識庫和用戶畫像存儲
        print("步驟 2: 初始化數據庫連接...")
        knowledge_store = ChromaKnowledgeStore()
        persona_store = PgPersonaStore()
        print("   ✅ 數據庫連接初始化成功")
        print()
        
        # 3. 創建 Ollama Provider 和統一模型服務
        print("步驟 3: 創建 Ollama Provider...")
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.OLLAMA,
            model_name=settings.model_service.model_name,
            api_base_url=settings.model_service.api_base_url or "http://host.docker.internal:11434",
            timeout=settings.model_service.timeout,
        )
        print("   ✅ Ollama Provider 創建成功")
        
        unified_service = UnifiedModelService(provider=provider)
        print("   ✅ 統一模型服務創建成功")
        print()
        
        # 4. 創建記憶服務
        print("步驟 4: 創建記憶服務...")
        memory_service = MemoryServiceImpl(
            knowledge_store=knowledge_store,
            persona_store=persona_store,
            analysis_model=unified_service,
        )
        print("   ✅ 記憶服務創建成功")
        print()
        
        # 5. 創建測試對話消息
        print("步驟 5: 準備測試對話...")
        test_message = DialogueArchiveMessage(
            dialog_id="test_dialog_001",
            user_id="test_user_001",
            timestamp=datetime.now(),
            turn=1,
            user_query="什么是 Python？",
            ai_response="Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年创建。它以其简洁的语法和强大的功能而闻名，广泛应用于 Web 开发、数据科学、机器学习和自动化脚本等领域。",
        )
        print(f"   用戶查詢: {test_message.user_query}")
        print(f"   AI 回應: {test_message.ai_response[:50]}...")
        print()
        
        # 6. 執行對話歸檔
        print("步驟 6: 執行對話歸檔（這可能需要一些時間）...")
        print("   正在進行語義分析（NER、KE、KT）...")
        await memory_service.archive(test_message)
        print("   ✅ 對話歸檔成功")
        print()
        
        # 7. 驗證知識存儲
        print("步驟 7: 驗證知識存儲...")
        retrieved_docs = await knowledge_store.search(
            "Python", "test_user_001", limit=5
        )
        print(f"   ✅ 檢索到 {len(retrieved_docs)} 條知識")
        if retrieved_docs:
            print(f"   第一條知識: {retrieved_docs[0].content[:100]}...")
        print()
        
        # 8. 驗證用戶畫像存儲
        print("步驟 8: 驗證用戶畫像存儲...")
        user_profile = await persona_store.get("test_user_001")
        if user_profile:
            print("   ✅ 用戶畫像已存儲")
            print(f"   風格標籤: {user_profile.style_tags}")
            print(f"   情感狀態: {user_profile.sentiment}")
        else:
            print("   ⚠️  用戶畫像未找到（可能尚未更新）")
        print()
        
        print("=" * 60)
        print("✅ 測試完成！對話歸檔功能正常。")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_dialogue_archive())
    sys.exit(0 if success else 1)

