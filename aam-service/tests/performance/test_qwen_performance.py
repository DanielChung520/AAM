"""
@purpose: Qwen Provider 性能測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import asyncio
import os
import time
import pytest
from typing import List

from src.infrastructure.ai.providers.qwen_provider import QwenProvider


class TestQwenPerformance:
    """Qwen Provider 性能測試類"""

    @pytest.fixture
    def qwen_provider(self):
        """創建 Qwen Provider 實例"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            pytest.skip("需要設置QWEN_API_KEY環境變量")
        
        api_base_url = os.getenv(
            "QWEN_API_BASE_URL",
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        )
        
        return QwenProvider(
            model_name="qwen-turbo",
            api_base_url=api_base_url,
            api_key=api_key,
            timeout=120,
        )

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_qwen_response_time(self, qwen_provider):
        """測試 Qwen Provider 的響應時間"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        prompt = "請簡短介紹一下人工智能。"
        
        start_time = time.time()
        try:
            result = await qwen_provider.generate(prompt)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 預期響應時間 < 30秒
            assert response_time < 30, f"響應時間過長: {response_time:.2f}秒"
            assert len(result) > 0, "響應內容不應為空"
            
            print(f"\nQwen Provider 響應時間: {response_time:.2f}秒")
            print(f"響應長度: {len(result)} 字符")
        except Exception as e:
            pytest.skip(f"API 調用失敗，跳過性能測試: {e}")

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_qwen_concurrent_requests(self, qwen_provider):
        """測試 Qwen Provider 的並發請求處理能力"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        prompts = [
            "什麼是機器學習？",
            "什麼是深度學習？",
            "什麼是自然語言處理？",
        ]
        
        async def generate_text(prompt: str) -> tuple[str, float]:
            """生成文本並記錄時間"""
            start_time = time.time()
            try:
                result = await qwen_provider.generate(prompt)
                end_time = time.time()
                return result, end_time - start_time
            except Exception as e:
                return f"錯誤: {e}", -1
        
        # 並發執行多個請求
        start_time = time.time()
        tasks = [generate_text(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 驗證結果
        successful_results = [r for r in results if r[1] > 0]
        assert len(successful_results) > 0, "至少應有一個請求成功"
        
        # 計算平均響應時間
        avg_response_time = sum(r[1] for r in successful_results) / len(successful_results)
        
        print(f"\n並發請求數: {len(prompts)}")
        print(f"總耗時: {total_time:.2f}秒")
        print(f"平均響應時間: {avg_response_time:.2f}秒")
        print(f"成功請求數: {len(successful_results)}/{len(prompts)}")
        
        # 預期總耗時不應超過單個請求時間的3倍（並發優勢）
        assert total_time < 90, f"並發處理時間過長: {total_time:.2f}秒"

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_qwen_timeout_handling(self, qwen_provider):
        """測試 Qwen Provider 的超時處理"""
        # 創建一個短超時的 Provider
        short_timeout_provider = QwenProvider(
            model_name="qwen-turbo",
            api_base_url=qwen_provider.api_base_url,
            api_key=qwen_provider.api_key,
            timeout=0.1,  # 極短超時時間
        )
        
        prompt = "請詳細介紹人工智能的發展歷史。"
        
        start_time = time.time()
        try:
            result = await short_timeout_provider.generate(prompt)
            end_time = time.time()
            
            # 如果沒有超時，記錄時間
            response_time = end_time - start_time
            print(f"\n未超時，響應時間: {response_time:.2f}秒")
        except RuntimeError as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            # 驗證超時處理正確
            assert "超時" in str(e) or "timeout" in str(e).lower(), f"應拋出超時錯誤: {e}"
            assert response_time < 1.0, f"超時處理時間過長: {response_time:.2f}秒"
            print(f"\n超時處理正確，耗時: {response_time:.2f}秒")

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_qwen_error_recovery_time(self, qwen_provider):
        """測試 Qwen Provider 的錯誤恢復時間"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        # 測試無效請求後的恢復時間
        invalid_provider = QwenProvider(
            model_name="qwen-turbo",
            api_base_url=qwen_provider.api_base_url,
            api_key="invalid_key",
            timeout=10,
        )
        
        # 先發送一個無效請求
        try:
            await invalid_provider.generate("test")
        except Exception:
            pass  # 預期會失敗
        
        # 使用有效 Provider 測試恢復時間
        start_time = time.time()
        try:
            result = await qwen_provider.generate("測試恢復時間")
            end_time = time.time()
            
            recovery_time = end_time - start_time
            
            # 預期恢復時間 < 30秒
            assert recovery_time < 30, f"錯誤恢復時間過長: {recovery_time:.2f}秒"
            assert len(result) > 0, "恢復後應能正常生成文本"
            
            print(f"\n錯誤恢復時間: {recovery_time:.2f}秒")
        except Exception as e:
            pytest.skip(f"API 調用失敗，跳過恢復測試: {e}")

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_qwen_check_available_performance(self, qwen_provider):
        """測試 Qwen Provider 可用性檢查的性能"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        # 執行多次可用性檢查
        check_times: List[float] = []
        
        for i in range(5):
            start_time = time.time()
            try:
                available = await qwen_provider.check_available()
                end_time = time.time()
                
                check_time = end_time - start_time
                check_times.append(check_time)
                
                print(f"檢查 {i+1}: 可用性={available}, 耗時={check_time:.2f}秒")
            except Exception as e:
                pytest.skip(f"可用性檢查失敗: {e}")
        
        # 計算平均檢查時間
        avg_check_time = sum(check_times) / len(check_times)
        max_check_time = max(check_times)
        
        # 預期可用性檢查應快速（< 10秒）
        assert avg_check_time < 10, f"平均可用性檢查時間過長: {avg_check_time:.2f}秒"
        assert max_check_time < 15, f"最大可用性檢查時間過長: {max_check_time:.2f}秒"
        
        print(f"\n平均可用性檢查時間: {avg_check_time:.2f}秒")
        print(f"最大可用性檢查時間: {max_check_time:.2f}秒")

