#!/usr/bin/env python3
"""
@purpose: 簡單的 Gemini Provider 測試
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import asyncio
import argparse
import os
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.infrastructure.ai.providers.gemini_provider import GeminiProvider
    from src.config.settings import get_settings
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確認您在項目根目錄運行此腳本")
    sys.exit(1)


async def test_gemini_provider(
    api_key: str = None,
    model_name: str = "gemini-pro",
    api_base_url: str = None,
):
    """測試 Gemini Provider"""
    print("=" * 60)
    print("測試 Gemini Provider")
    print("=" * 60)
    
    # 從環境變量或參數獲取 API Key
    if not api_key:
        settings = get_settings()
        api_key = settings.model_service.gemini_api_key
    
    if not api_key:
        print("❌ 未找到 Gemini API Key")
        print("請通過以下方式之一設置：")
        print("   1. 環境變量 GEMINI_API_KEY")
        print("   2. .env 文件中的 GEMINI_API_KEY")
        print("   3. 命令行參數 --api-key")
        sys.exit(1)
    
    print(f"模型名稱: {model_name}")
    if api_base_url:
        print(f"API Base URL: {api_base_url}")
    print()
    
    try:
        # 步驟 1: 初始化 Provider
        print("步驟 1: 初始化 Gemini Provider...")
        provider = GeminiProvider(
            model_name=model_name,
            api_base_url=api_base_url,
            api_key=api_key,
            timeout=120,
        )
        print("✅ Gemini Provider 初始化成功")
        print(f"   Provider 類型: {provider.provider_type.value}")
        print(f"   配置: {provider.get_config()}")
        print()
        
        # 步驟 2: 檢查服務可用性（可選，跳過以提高測試速度）
        # print("步驟 2: 檢查 Gemini 服務可用性...")
        # is_available = await provider.check_available()
        # if is_available:
        #     print("✅ Gemini 服務可用")
        # else:
        #     print("⚠️  Gemini 服務可用性檢查失敗，但將繼續測試生成功能")
        # print()
        
        # 步驟 3: 測試文本生成
        print("步驟 3: 測試文本生成...")
        test_prompt = "請用一句話介紹 Python 編程語言。"
        print(f"測試 Prompt: {test_prompt}")
        print("正在生成（這可能需要一些時間）...")
        
        result = await provider.generate(test_prompt, temperature=0.0)  # 使用默认 max_tokens
        print("✅ 文本生成成功")
        print(f"生成結果: {result}")
        print()
        
        # 步驟 4: 測試更複雜的 Prompt
        print("步驟 4: 測試更複雜的 Prompt...")
        complex_prompt = "請解釋什麼是機器學習，並給出一個簡單的例子。"
        print(f"測試 Prompt: {complex_prompt}")
        print("正在生成...")
        
        result2 = await provider.generate(complex_prompt, temperature=0.3)  # 使用默认 max_tokens
        print("✅ 文本生成成功")
        print(f"生成結果: {result2[:200]}...")  # 只顯示前200個字符
        print()
        
        return True
        
    except ValueError as e:
        print(f"❌ 配置錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="簡單的 Gemini Provider 測試")
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Gemini API Key（可選，優先使用環境變量或 .env）",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-pro",
        help="Gemini 模型名稱（默認: gemini-pro）",
    )
    parser.add_argument(
        "--api-base-url",
        type=str,
        default=None,
        help="Gemini API Base URL（可選，使用默認值）",
    )
    
    args = parser.parse_args()
    
    # 運行測試
    success = await test_gemini_provider(
        api_key=args.api_key,
        model_name=args.model,
        api_base_url=args.api_base_url,
    )
    
    if success:
        print("=" * 60)
        print("✅ 所有測試通過！Gemini Provider 可以正常使用。")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

