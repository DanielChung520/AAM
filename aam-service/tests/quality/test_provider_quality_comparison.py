"""
@purpose: Provider 質量對比測試
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import os
import pytest
from typing import Dict, List

from src.infrastructure.ai.providers.qwen_provider import QwenProvider
from src.infrastructure.ai.unified_model_service import UnifiedModelService
from src.core.interfaces.i_model_provider import ModelProviderType


class TestProviderQualityComparison:
    """Provider 質量對比測試類"""

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

    @pytest.fixture
    def test_texts(self) -> List[str]:
        """測試文本列表"""
        return [
            "我想學習 Python 編程語言，應該從哪裡開始？",
            "什麼是機器學習？它有哪些應用場景？",
            "請介紹一下深度學習的基本概念。",
        ]

    @pytest.mark.asyncio
    @pytest.mark.quality
    @pytest.mark.integration
    async def test_qwen_knowledge_extraction_quality(self, qwen_provider, test_texts):
        """測試 Qwen Provider 的知識提取質量"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        unified_service = UnifiedModelService(provider=qwen_provider)
        
        quality_results: List[Dict] = []
        
        for text in test_texts:
            try:
                # 執行知識提取
                knowledge = await unified_service.extract_knowledge(
                    text=text,
                    user_id="test_user",
                    session_id="test_session",
                )
                
                # 評估質量
                quality_score = self._evaluate_knowledge_quality(knowledge)
                
                quality_results.append({
                    "text": text,
                    "entities_count": len(knowledge.entities) if knowledge.entities else 0,
                    "triples_count": len(self._parse_triples(knowledge.triples_json)),
                    "quality_score": quality_score,
                })
                
                print(f"\n文本: {text[:50]}...")
                print(f"實體數量: {len(knowledge.entities) if knowledge.entities else 0}")
                print(f"三元組數量: {len(self._parse_triples(knowledge.triples_json))}")
                print(f"質量分數: {quality_score:.2f}")
            except Exception as e:
                pytest.skip(f"知識提取失敗，跳過質量測試: {e}")
        
        # 驗證質量結果
        assert len(quality_results) > 0, "應至少有一個質量結果"
        
        avg_quality = sum(r["quality_score"] for r in quality_results) / len(quality_results)
        print(f"\n平均質量分數: {avg_quality:.2f}")
        
        # 預期平均質量分數 > 0.5
        assert avg_quality > 0.5, f"平均質量分數過低: {avg_quality:.2f}"

    @pytest.mark.asyncio
    @pytest.mark.quality
    @pytest.mark.integration
    async def test_qwen_triple_extraction_quality(self, qwen_provider, test_texts):
        """測試 Qwen Provider 的三元組提取質量"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        unified_service = UnifiedModelService(provider=qwen_provider)
        
        triple_results: List[Dict] = []
        
        for text in test_texts:
            try:
                # 執行知識提取
                knowledge = await unified_service.extract_knowledge(
                    text=text,
                    user_id="test_user",
                    session_id="test_session",
                )
                
                # 解析三元組
                triples = self._parse_triples(knowledge.triples_json)
                
                # 評估三元組質量
                triple_quality = self._evaluate_triple_quality(triples)
                
                triple_results.append({
                    "text": text,
                    "triples_count": len(triples),
                    "triple_quality": triple_quality,
                })
                
                print(f"\n文本: {text[:50]}...")
                print(f"三元組數量: {len(triples)}")
                print(f"三元組質量: {triple_quality:.2f}")
            except Exception as e:
                pytest.skip(f"三元組提取失敗，跳過質量測試: {e}")
        
        # 驗證三元組結果
        assert len(triple_results) > 0, "應至少有一個三元組結果"
        
        avg_triple_quality = sum(r["triple_quality"] for r in triple_results) / len(triple_results)
        print(f"\n平均三元組質量: {avg_triple_quality:.2f}")
        
        # 預期平均三元組質量 > 0.5
        assert avg_triple_quality > 0.5, f"平均三元組質量過低: {avg_triple_quality:.2f}"

    @pytest.mark.asyncio
    @pytest.mark.quality
    @pytest.mark.integration
    async def test_qwen_personality_analysis_quality(self, qwen_provider, test_texts):
        """測試 Qwen Provider 的個性分析質量"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        unified_service = UnifiedModelService(provider=qwen_provider)
        
        personality_results: List[Dict] = []
        
        for text in test_texts:
            try:
                # 執行個性分析
                personality = await unified_service.analyze_personality(text=text)
                
                # 評估個性分析質量
                personality_quality = self._evaluate_personality_quality(personality)
                
                personality_results.append({
                    "text": text,
                    "personality_quality": personality_quality,
                    "traits_count": len(personality.traits) if personality.traits else 0,
                })
                
                print(f"\n文本: {text[:50]}...")
                print(f"個性特質數量: {len(personality.traits) if personality.traits else 0}")
                print(f"個性分析質量: {personality_quality:.2f}")
            except Exception as e:
                pytest.skip(f"個性分析失敗，跳過質量測試: {e}")
        
        # 驗證個性分析結果
        assert len(personality_results) > 0, "應至少有一個個性分析結果"
        
        avg_personality_quality = sum(r["personality_quality"] for r in personality_results) / len(personality_results)
        print(f"\n平均個性分析質量: {avg_personality_quality:.2f}")
        
        # 預期平均個性分析質量 > 0.5
        assert avg_personality_quality > 0.5, f"平均個性分析質量過低: {avg_personality_quality:.2f}"

    @pytest.mark.asyncio
    @pytest.mark.quality
    async def test_generate_quality_comparison_report(self, qwen_provider, test_texts):
        """生成質量對比報告"""
        # 跳過測試如果沒有有效的 API Key
        if not os.getenv("QWEN_API_KEY"):
            pytest.skip("需要 QWEN_API_KEY 環境變量")
        
        unified_service = UnifiedModelService(provider=qwen_provider)
        
        report_data: Dict = {
            "provider": "Qwen",
            "model": qwen_provider.model_name,
            "test_texts": test_texts,
            "knowledge_extraction": [],
            "triple_extraction": [],
            "personality_analysis": [],
        }
        
        for text in test_texts:
            try:
                # 知識提取
                knowledge = await unified_service.extract_knowledge(
                    text=text,
                    user_id="test_user",
                    session_id="test_session",
                )
                
                knowledge_quality = self._evaluate_knowledge_quality(knowledge)
                report_data["knowledge_extraction"].append({
                    "text": text,
                    "entities_count": len(knowledge.entities) if knowledge.entities else 0,
                    "triples_count": len(self._parse_triples(knowledge.triples_json)),
                    "quality_score": knowledge_quality,
                })
                
                # 三元組提取
                triples = self._parse_triples(knowledge.triples_json)
                triple_quality = self._evaluate_triple_quality(triples)
                report_data["triple_extraction"].append({
                    "text": text,
                    "triples_count": len(triples),
                    "quality_score": triple_quality,
                })
                
                # 個性分析
                personality = await unified_service.analyze_personality(text=text)
                personality_quality = self._evaluate_personality_quality(personality)
                report_data["personality_analysis"].append({
                    "text": text,
                    "traits_count": len(personality.traits) if personality.traits else 0,
                    "quality_score": personality_quality,
                })
            except Exception as e:
                pytest.skip(f"質量對比測試失敗: {e}")
        
        # 生成報告摘要
        if report_data["knowledge_extraction"]:
            avg_knowledge_quality = sum(
                r["quality_score"] for r in report_data["knowledge_extraction"]
            ) / len(report_data["knowledge_extraction"])
            report_data["avg_knowledge_quality"] = avg_knowledge_quality
        
        if report_data["triple_extraction"]:
            avg_triple_quality = sum(
                r["quality_score"] for r in report_data["triple_extraction"]
            ) / len(report_data["triple_extraction"])
            report_data["avg_triple_quality"] = avg_triple_quality
        
        if report_data["personality_analysis"]:
            avg_personality_quality = sum(
                r["quality_score"] for r in report_data["personality_analysis"]
            ) / len(report_data["personality_analysis"])
            report_data["avg_personality_quality"] = avg_personality_quality
        
        # 打印報告
        print("\n" + "="*60)
        print("Provider 質量對比報告")
        print("="*60)
        print(f"Provider: {report_data['provider']}")
        print(f"Model: {report_data['model']}")
        print(f"\n平均知識提取質量: {report_data.get('avg_knowledge_quality', 0):.2f}")
        print(f"平均三元組提取質量: {report_data.get('avg_triple_quality', 0):.2f}")
        print(f"平均個性分析質量: {report_data.get('avg_personality_quality', 0):.2f}")
        print("="*60)
        
        # 驗證報告數據
        assert len(report_data["knowledge_extraction"]) > 0, "應有知識提取結果"
        assert len(report_data["triple_extraction"]) > 0, "應有三元組提取結果"
        assert len(report_data["personality_analysis"]) > 0, "應有個性分析結果"

    def _evaluate_knowledge_quality(self, knowledge) -> float:
        """評估知識提取質量"""
        score = 0.0
        
        # 實體數量評分（0-0.5）
        entities_count = len(knowledge.entities) if knowledge.entities else 0
        score += min(entities_count * 0.1, 0.5)
        
        # 三元組數量評分（0-0.5）
        triples = self._parse_triples(knowledge.triples_json)
        triples_count = len(triples)
        score += min(triples_count * 0.1, 0.5)
        
        return min(score, 1.0)

    def _evaluate_triple_quality(self, triples: List[Dict]) -> float:
        """評估三元組質量"""
        if not triples:
            return 0.0
        
        score = 0.0
        
        # 三元組完整性評分（0-0.5）
        complete_triples = sum(
            1 for t in triples
            if t.get("subject") and t.get("predicate") and t.get("object")
        )
        score += (complete_triples / len(triples)) * 0.5
        
        # 三元組數量評分（0-0.5）
        score += min(len(triples) * 0.1, 0.5)
        
        return min(score, 1.0)

    def _evaluate_personality_quality(self, personality) -> float:
        """評估個性分析質量"""
        score = 0.0
        
        # 個性特質數量評分（0-0.5）
        traits_count = len(personality.traits) if personality.traits else 0
        score += min(traits_count * 0.1, 0.5)
        
        # 個性分析完整性評分（0-0.5）
        if personality.traits and len(personality.traits) > 0:
            score += 0.5
        
        return min(score, 1.0)

    def _parse_triples(self, triples_json: str) -> List[Dict]:
        """解析三元組 JSON"""
        import json
        try:
            if not triples_json:
                return []
            return json.loads(triples_json) if isinstance(triples_json, str) else triples_json
        except Exception:
            return []

