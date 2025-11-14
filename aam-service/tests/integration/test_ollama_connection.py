#!/usr/bin/env python3
"""
@purpose: 測試 Ollama 連接和調用
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12

使用方法:
    python scripts/test_ollama_connection.py
    # 或指定模型名稱
    python scripts/test_ollama_connection.py --model deepseek-r1:8b
"""
import asyncio
import argparse
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.ai.providers.ollama_provider import OllamaProvider


async def test_ollama_connection(model_name: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434"):
    """
    測試 Ollama 連接和調用
    
    Args:
        model_name: Ollama 模型名稱
        base_url: Ollama API 基礎 URL
    """
    print("=" * 60)
    print("Ollama 連接測試")
    print("=" * 60)
    print(f"模型名稱: {model_name}")
    print(f"API URL: {base_url}")
    print()
    
    try:
        # 1. 創建 Ollama Provider
        print("步驟 1: 創建 Ollama Provider...")
        provider = OllamaProvider(
            model_name=model_name,
            base_url=base_url,
            timeout=120,
        )
        print("✅ Ollama Provider 創建成功")
        print()
        
        # 2. 檢查服務可用性
        print("步驟 2: 檢查 Ollama 服務可用性...")
        is_available = await provider.check_available()
        if is_available:
            print("✅ Ollama 服務可用")
        else:
            print("❌ Ollama 服務不可用")
            print("   請確認:")
            print("   1. Ollama 服務是否運行: ollama serve")
            print("   2. 模型是否已下載: ollama pull " + model_name)
            print("   3. API URL 是否正確: " + base_url)
            return False
        print()
        
        # 3. 測試簡單文本生成
        print("步驟 3: 測試文本生成...")
        test_prompt = "請用一句話介紹 Python 編程語言。"
        print(f"測試 Prompt: {test_prompt}")
        print("正在生成...")
        
        result = await provider.generate(test_prompt)
        print("✅ 文本生成成功")
        print(f"生成結果: {result[:200]}...")  # 只顯示前 200 個字符
        print()
        
        # 4. 測試配置信息
        print("步驟 4: 檢查配置信息...")
        config = provider.get_config()
        print("✅ 配置信息:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        print()
        
        print("=" * 60)
        print("✅ 所有測試通過！Ollama 可以正常使用。")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print("❌ 依賴缺失:")
        print(f"   {e}")
        print()
        print("請安裝依賴:")
        print("   pip install langchain-community")
        return False
        
    except Exception as e:
        print("❌ 測試失敗:")
        print(f"   錯誤類型: {type(e).__name__}")
        print(f"   錯誤信息: {str(e)}")
        print()
        print("可能的原因:")
        print("   1. Ollama 服務未運行")
        print("   2. 模型名稱不正確（您有: deepseek-r1:8b, deepseek-r1:14b）")
        print("   3. API URL 不正確（默認: http://localhost:11434）")
        print("   4. 網絡連接問題")
        import traceback
        traceback.print_exc()
        return False


async def test_unified_service(model_name: str = "deepseek-r1:8b"):
    """
    測試通過統一模型服務調用 Ollama
    
    Args:
        model_name: Ollama 模型名稱
    """
    print("=" * 60)
    print("統一模型服務 - Ollama 測試")
    print("=" * 60)
    print(f"模型名稱: {model_name}")
    print()
    
    try:
        from src.infrastructure.ai.unified_model_service import UnifiedModelService
        from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
        from src.core.interfaces.i_model_provider import ModelProviderType
        
        # 1. 創建 Provider
        print("步驟 1: 創建 Ollama Provider...")
        provider = ModelProviderFactory.create_provider(
            provider_type=ModelProviderType.OLLAMA,
            model_name=model_name,
            api_base_url="http://localhost:11434",
            timeout=120,
        )
        print("✅ Provider 創建成功")
        print()
        
        # 2. 創建統一模型服務
        print("步驟 2: 創建統一模型服務...")
        unified_service = UnifiedModelService(provider=provider)
        print("✅ 統一模型服務創建成功")
        print()
        
        # 3. 測試知識提取
        print("步驟 3: 測試知識提取（NER, KE, KT）...")
        test_text = "Python 是一種由 Guido van Rossum 在 1991 年創建的編程語言。它廣泛用於 Web 開發、數據科學和機器學習。"
        print(f"測試文本: {test_text}")
        print("正在提取知識...")
        
        knowledge = await unified_service.extract_knowledge(
            text=test_text,
            user_id="test_user",
            session_id="test_session",
        )
        
        print("✅ 知識提取成功")
        print(f"   實體數量: {len(knowledge.entities)}")
        print(f"   實體列表: {knowledge.entities[:5]}...")  # 顯示前 5 個
        
        # 解析三元組
        import json
        triples = json.loads(knowledge.triples_json)
        print(f"   三元組數量: {len(triples)}")
        if triples:
            print(f"   第一個三元組: {triples[0]}")
        print()
        
        # 4. 測試個性分析
        print("步驟 4: 測試個性分析...")
        personality = await unified_service.analyze_personality(test_text)
        print("✅ 個性分析成功")
        print(f"   風格標籤: {personality.style_tags}")
        print(f"   情感狀態: {personality.sentiment}")
        print(f"   語言模式: {personality.language_patterns}")
        print()
        
        print("=" * 60)
        print("✅ 統一模型服務測試通過！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("❌ 測試失敗:")
        print(f"   錯誤類型: {type(e).__name__}")
        print(f"   錯誤信息: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="測試 Ollama 連接和調用")
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-r1:8b",
        help="Ollama 模型名稱（默認: deepseek-r1:8b）",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL（默認: http://localhost:11434）",
    )
    parser.add_argument(
        "--unified",
        action="store_true",
        help="測試統一模型服務（包含知識提取和個性分析）",
    )
    
    args = parser.parse_args()
    
    # 運行測試
    if args.unified:
        success = asyncio.run(test_unified_service(args.model))
    else:
        success = asyncio.run(test_ollama_connection(args.model, args.url))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

