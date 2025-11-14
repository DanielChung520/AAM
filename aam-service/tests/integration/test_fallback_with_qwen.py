#!/usr/bin/env python3
"""
@purpose: 降級策略測試腳本（包含 Qwen Provider）
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13

使用方法:
    python scripts/test_fallback_with_qwen.py

環境變量:
    QWEN_API_KEY: Qwen API 密鑰（可選，有默認值）
    QWEN_API_BASE_URL: Qwen API 基礎 URL（可選）
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.interfaces.i_model_provider import ModelProviderType
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.quality_evaluator import QualityEvaluator


async def test_qwen_provider():
    """測試 Qwen Provider"""
    print("\n" + "="*60)
    print("測試 1: Qwen Provider 基礎功能")
    print("="*60)
    
    # 創建 Qwen Provider
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("錯誤: 需要設置QWEN_API_KEY環境變量")
        print("請在.env文件中設置或通過環境變量設置：export QWEN_API_KEY=your-api-key")
        return False
    
    api_base_url = os.getenv(
        "QWEN_API_BASE_URL",
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    )
    
    provider = ModelProviderFactory.create_provider(
        provider_type=ModelProviderType.QWEN,
        model_name="qwen-turbo",
        api_base_url=api_base_url,
        api_key=api_key,
        timeout=120,
    )
    
    print(f"✓ Qwen Provider 創建成功")
    print(f"  - Provider 類型: {provider.provider_type.value}")
    print(f"  - 模型名稱: {provider.model_name}")
    print(f"  - API URL: {provider.api_base_url}")
    
    # 檢查可用性
    print("\n檢查 Qwen Provider 可用性...")
    try:
        is_available = await provider.check_available()
        if is_available:
            print("✓ Qwen Provider 可用")
        else:
            print("⚠ Qwen Provider 不可用（可能是 API Key 無效）")
    except Exception as e:
        print(f"✗ Qwen Provider 可用性檢查失敗: {e}")
        return False
    
    # 測試文本生成
    print("\n測試文本生成...")
    try:
        prompt = "請用一句話介紹 Python 編程語言。"
        result = await provider.generate(prompt, max_tokens=100)
        print(f"✓ 文本生成成功")
        print(f"  提示詞: {prompt}")
        print(f"  響應: {result[:200]}...")
    except Exception as e:
        print(f"✗ 文本生成失敗: {e}")
        return False
    
    return True


async def test_unified_service_with_qwen():
    """測試 UnifiedModelService 使用 Qwen Provider"""
    print("\n" + "="*60)
    print("測試 2: UnifiedModelService 使用 Qwen Provider")
    print("="*60)
    
    # 創建 Qwen Provider
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("錯誤: 需要設置QWEN_API_KEY環境變量")
        return False
    
    provider = ModelProviderFactory.create_provider(
        provider_type=ModelProviderType.QWEN,
        model_name="qwen-turbo",
        api_key=api_key,
    )
    
    # 創建 UnifiedModelService
    unified_service = UnifiedModelService(provider=provider)
    print("✓ UnifiedModelService 創建成功")
    
    # 檢查可用性
    try:
        is_available = await unified_service.check_available()
        if not is_available:
            print("⚠ Qwen API 不可用，跳過知識提取測試")
            return True
    except Exception as e:
        print(f"⚠ 可用性檢查失敗: {e}，跳過知識提取測試")
        return True
    
    # 測試知識提取
    print("\n測試知識提取...")
    try:
        text = "Python 是一種高級編程語言，由 Guido van Rossum 在 1991 年創建。Django 和 Flask 是 Python 的 Web 框架。"
        knowledge = await unified_service.extract_knowledge(
            text=text,
            user_id="test_user",
            session_id="test_session"
        )
        
        print(f"✓ 知識提取成功")
        print(f"  - 實體數量: {len(knowledge.entities)}")
        print(f"  - 實體: {knowledge.entities[:5]}")
        
        import json
        triples = json.loads(knowledge.triples_json)
        print(f"  - 三元組數量: {len(triples)}")
        if triples:
            print(f"  - 第一個三元組: {triples[0]}")
    except Exception as e:
        print(f"✗ 知識提取失敗: {e}")
        return False
    
    return True


async def test_fallback_strategy():
    """測試降級策略"""
    print("\n" + "="*60)
    print("測試 3: 降級策略（EB-mM → Ollama → Qwen）")
    print("="*60)
    
    # 創建 Qwen Provider 作為 LLM 層
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("錯誤: 需要設置QWEN_API_KEY環境變量")
        return False
    
    qwen_provider = ModelProviderFactory.create_provider(
        provider_type=ModelProviderType.QWEN,
        model_name="qwen-turbo",
        api_key=api_key,
    )
    
    llm_service = UnifiedModelService(provider=qwen_provider)
    
    # 創建降級策略模型（只使用 LLM 層）
    quality_evaluator = QualityEvaluator(quality_threshold=0.7)
    fallback_model = FallbackAnalysisModel(
        eb_mm_model=None,
        ollama_local_model=None,
        llm_model=llm_service,
        quality_evaluator=quality_evaluator,
    )
    
    print("✓ 降級策略模型創建成功")
    print("  - EB-mM: 未配置")
    print("  - Ollama 本地模型: 未配置")
    print("  - LLM 抽象層: Qwen Provider")
    
    # 檢查可用性
    try:
        is_available = await fallback_model.check_available()
        if not is_available:
            print("⚠ LLM 層（Qwen）不可用，跳過測試")
            return True
    except Exception as e:
        print(f"⚠ 可用性檢查失敗: {e}，跳過測試")
        return True
    
    # 測試知識提取
    print("\n測試降級策略知識提取...")
    try:
        text = "Python 是一種編程語言，廣泛應用於 Web 開發和數據科學。"
        knowledge = await fallback_model.extract_knowledge(
            text=text,
            user_id="test_user",
            session_id="test_session_fallback"
        )
        
        print(f"✓ 降級策略知識提取成功")
        print(f"  - 實體數量: {len(knowledge.entities)}")
        
        import json
        triples = json.loads(knowledge.triples_json)
        print(f"  - 三元組數量: {len(triples)}")
    except Exception as e:
        print(f"✗ 降級策略知識提取失敗: {e}")
        return False
    
    return True


async def main():
    """主函數"""
    print("\n" + "="*60)
    print("降級策略測試腳本（包含 Qwen Provider）")
    print("="*60)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 測試 1: Qwen Provider
    try:
        result1 = await test_qwen_provider()
        results.append(("Qwen Provider 基礎功能", result1))
    except Exception as e:
        print(f"\n✗ 測試 1 執行失敗: {e}")
        results.append(("Qwen Provider 基礎功能", False))
    
    # 測試 2: UnifiedModelService
    try:
        result2 = await test_unified_service_with_qwen()
        results.append(("UnifiedModelService 使用 Qwen", result2))
    except Exception as e:
        print(f"\n✗ 測試 2 執行失敗: {e}")
        results.append(("UnifiedModelService 使用 Qwen", False))
    
    # 測試 3: 降級策略
    try:
        result3 = await test_fallback_strategy()
        results.append(("降級策略", result3))
    except Exception as e:
        print(f"\n✗ 測試 3 執行失敗: {e}")
        results.append(("降級策略", False))
    
    # 輸出測試結果摘要
    print("\n" + "="*60)
    print("測試結果摘要")
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
    
    print(f"\n總計: {len(results)} 個測試")
    print(f"通過: {passed}")
    print(f"失敗: {failed}")
    
    if failed == 0:
        print("\n✓ 所有測試通過！")
        return 0
    else:
        print(f"\n✗ {failed} 個測試失敗")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

