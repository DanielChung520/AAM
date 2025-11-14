#!/usr/bin/env python3
"""
@purpose: 簡單的 Ollama 連接測試（不依賴項目其他模組）
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import argparse
import httpx
import sys

try:
    from langchain_community.llms import Ollama
except ImportError:
    print("❌ 缺少依賴: langchain-community")
    print("請安裝: pip install langchain-community")
    sys.exit(1)


async def test_ollama_api(base_url: str = "http://localhost:11434"):
    """測試 Ollama API 是否可訪問"""
    print("=" * 60)
    print("測試 Ollama API 連接")
    print("=" * 60)
    print(f"API URL: {base_url}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print("✅ Ollama API 可訪問")
                print(f"   找到 {len(models)} 個模型:")
                for model in models:
                    print(f"   - {model.get('name', 'unknown')}")
                print()
                return True
            else:
                print(f"❌ Ollama API 返回錯誤: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 無法連接到 Ollama API: {e}")
        print()
        print("請確認:")
        print("   1. Ollama 服務是否運行")
        print("   2. API URL 是否正確: http://localhost:11434")
        return False


async def test_ollama_generate(model_name: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434"):
    """測試 Ollama 文本生成"""
    print("=" * 60)
    print("測試 Ollama 文本生成")
    print("=" * 60)
    print(f"模型名稱: {model_name}")
    print(f"API URL: {base_url}")
    print()
    
    try:
        # 創建 Ollama LLM
        print("步驟 1: 初始化 Ollama LLM...")
        llm = Ollama(
            model=model_name,
            base_url=base_url,
            timeout=120,
        )
        print("✅ Ollama LLM 初始化成功")
        print()
        
        # 測試生成
        print("步驟 2: 測試文本生成...")
        test_prompt = "請用一句話介紹 Python 編程語言。"
        print(f"測試 Prompt: {test_prompt}")
        print("正在生成（這可能需要一些時間）...")
        
        result = await llm.ainvoke(test_prompt)
        print("✅ 文本生成成功")
        print(f"生成結果: {result}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        print()
        print("可能的原因:")
        print("   1. 模型名稱不正確")
        print("   2. 模型未下載（運行: ollama pull " + model_name + "）")
        print("   3. 網絡連接問題")
        print("   4. 超時（大模型需要更長時間）")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="簡單的 Ollama 連接測試")
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
        "--api-only",
        action="store_true",
        help="只測試 API 連接，不測試文本生成",
    )
    
    args = parser.parse_args()
    
    # 測試 API 連接
    api_ok = await test_ollama_api(args.url)
    if not api_ok:
        sys.exit(1)
    
    # 如果只測試 API，則退出
    if args.api_only:
        print("=" * 60)
        print("✅ API 連接測試通過！")
        print("=" * 60)
        sys.exit(0)
    
    # 測試文本生成
    generate_ok = await test_ollama_generate(args.model, args.url)
    
    if generate_ok:
        print("=" * 60)
        print("✅ 所有測試通過！Ollama 可以正常使用。")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

