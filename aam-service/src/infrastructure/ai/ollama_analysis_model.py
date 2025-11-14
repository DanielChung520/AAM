"""
@purpose: 使用 Ollama 本地模型進行語義分析（NER, KE, KT 和個性分析）
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
from datetime import datetime
from typing import Optional

import httpx
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.config.settings import AISettings, get_settings
from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.infrastructure.ai.providers.ollama_provider import OllamaProvider
from src.infrastructure.ai.triple_classifier import TripleClassifier
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = logging.getLogger(__name__)


class OllamaAnalysisModel(IAnalysisModel):
    """
    使用 Ollama 本地模型進行語義分析
    
    支持的功能：
    - NER (命名實體識別)
    - KE (知識提取)
    - KT (知識三元組提取)
    - 個性分析
    """

    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        settings: Optional[AISettings] = None,
    ):
        """
        初始化 Ollama 分析模型

        Args:
            model_name: Ollama 模型名稱（如 llama3, mistral, qwen2.5 等）
            base_url: Ollama API 基礎 URL
            timeout: 請求超時時間（秒）
            settings: AI 配置（可選）
        """
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        self.settings = settings or get_settings().ai

        # 检查依赖是否安装
        if Ollama is None:
            raise ImportError(
                "langchain-community 未安装。请运行: pip install langchain-community"
            )

        # 初始化 LangChain Ollama LLM
        try:
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            logger.info(
                "Ollama 模型初始化成功",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                },
            )
        except Exception as e:
            logger.error(
                f"Ollama 模型初始化失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "base_url": self.base_url,
                    "error": str(e),
                },
            )
            raise

        # 初始化 JSON 輸出解析器
        self.json_parser = JsonOutputParser()

        # 創建 OllamaProvider 用於分類服務
        self.ollama_provider = OllamaProvider(
            model_name=self.model_name,
            base_url=self.base_url,
            timeout=self.timeout,
        )
        
        # 初始化三元組分類服務
        self.triple_classifier = TripleClassifier(self.ollama_provider)

        # 定義 Prompt 模板
        self._init_prompts()

    def _init_prompts(self):
        """初始化 Prompt 模板"""
        # NER 提取 Prompt
        self.ner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的命名實體識別系統。請從文本中提取所有命名實體（人名、地名、組織名、產品名、日期、時間等）。",
                ),
                (
                    "human",
                    "請從以下文本中提取命名實體：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"entities\": [\"實體1\", \"實體2\", ...]\n}}",
                ),
            ]
        )

        # KE 提取 Prompt
        self.ke_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的知識提取系統。請從文本中提取關鍵概念、知識點和重要信息。",
                ),
                (
                    "human",
                    "請從以下文本中提取關鍵知識：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"concepts\": [\"概念1\", \"概念2\", ...],\n  \"keywords\": [\"關鍵詞1\", \"關鍵詞2\", ...]\n}}",
                ),
            ]
        )

        # KT 提取 Prompt
        self.kt_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的知識三元組提取系統。請從文本中提取主體-謂詞-客體關係（三元組）。",
                ),
                (
                    "human",
                    "請從以下文本中提取知識三元組：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"triples\": [\n    {{\"subject\": \"主體\", \"predicate\": \"謂詞\", \"object\": \"客體\"}},\n    ...\n  ]\n}}",
                ),
            ]
        )

        # 個性分析 Prompt
        self.personality_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的用戶個性分析系統。請分析文本中的語言風格、情感狀態和個性特徵。",
                ),
                (
                    "human",
                    "請分析以下文本的個性特徵：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"style_tags\": {{\"formal\": 0.8, \"casual\": 0.2, ...}},\n  \"sentiment\": \"positive|negative|neutral\",\n  \"language_patterns\": [\"模式1\", \"模式2\", ...],\n  \"confidence_score\": 0.85\n}}",
                ),
            ]
        )

    async def _check_ollama_available(self) -> bool:
        """
        檢查 Ollama 服務是否可用

        Returns:
            True 如果 Ollama 可用，False 否則
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(
                f"Ollama 服務不可用: {e}",
                extra={"base_url": self.base_url, "error": str(e)},
            )
            return False

    async def extract_knowledge(
        self, text: str, user_id: str, session_id: str
    ) -> KnowledgeAsset:
        """
        提取知識（NER, KE, KT）

        Args:
            text: 輸入文本
            user_id: 用戶 ID
            session_id: 會話 ID

        Returns:
            知識資產對象
        """
        # 檢查 Ollama 是否可用
        if not await self._check_ollama_available():
            logger.error(
                "Ollama 服務不可用，無法提取知識",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                },
            )
            raise RuntimeError("Ollama 服務不可用")

        try:
            # 並行提取 NER, KE, KT
            # 注意：Ollama 不支持真正的並行，這裡順序執行
            entities = await self._extract_ner(text)
            triples = await self._extract_kt(text)

            # 對三元組進行分類
            if triples:
                try:
                    classified_triples = await self.triple_classifier.classify_triples(
                        triples
                    )
                    triples = classified_triples
                    logger.debug(
                        "Ollama 三元組分類完成",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "triple_count": len(triples),
                        },
                    )
                except Exception as e:
                    logger.warning(
                        f"Ollama 三元組分類失敗，使用原始三元組: {e}",
                        extra={
                            "user_id": user_id,
                            "session_id": session_id,
                            "error": str(e),
                        },
                    )
                    # 分類失敗時，繼續使用原始三元組

            # 構建知識資產
            knowledge = KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=int(datetime.utcnow().timestamp()),
                source_type="dialogue",
                entities=entities,
                triples_json=json.dumps(triples, ensure_ascii=False),
            )

            logger.info(
                "知識提取成功",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "entity_count": len(entities),
                    "triple_count": len(triples),
                },
            )

            return knowledge

        except Exception as e:
            logger.error(
                f"知識提取失敗: {e}",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                    "error": str(e),
                },
            )
            raise

    async def _extract_ner(self, text: str) -> list[str]:
        """
        提取命名實體

        Args:
            text: 輸入文本

        Returns:
            實體列表
        """
        try:
            # 構建鏈
            chain = self.ner_prompt | self.llm | self.json_parser

            # 調用模型
            result = await chain.ainvoke({"text": text})

            # 提取實體
            entities = result.get("entities", [])
            if not isinstance(entities, list):
                entities = []

            return entities

        except Exception as e:
            logger.warning(f"NER 提取失敗: {e}，返回空列表")
            return []

    async def _extract_kt(self, text: str) -> list[dict]:
        """
        提取知識三元組

        Args:
            text: 輸入文本

        Returns:
            三元組列表
        """
        try:
            # 構建鏈
            chain = self.kt_prompt | self.llm | self.json_parser

            # 調用模型
            result = await chain.ainvoke({"text": text})

            # 提取三元組
            triples = result.get("triples", [])
            if not isinstance(triples, list):
                triples = []

            # 驗證三元組格式
            validated_triples = []
            for triple in triples:
                if (
                    isinstance(triple, dict)
                    and "subject" in triple
                    and "predicate" in triple
                    and "object" in triple
                ):
                    validated_triples.append(triple)

            return validated_triples

        except Exception as e:
            logger.warning(f"KT 提取失敗: {e}，返回空列表")
            return []

    async def analyze_personality(self, text: str) -> PersonalityInsights:
        """
        分析用戶個性

        Args:
            text: 輸入文本

        Returns:
            個性分析結果
        """
        # 檢查 Ollama 是否可用
        if not await self._check_ollama_available():
            logger.error("Ollama 服務不可用，無法分析個性")
            raise RuntimeError("Ollama 服務不可用")

        try:
            # 構建鏈
            chain = self.personality_prompt | self.llm | self.json_parser

            # 調用模型
            result = await chain.ainvoke({"text": text})

            # 提取個性分析結果
            style_tags = result.get("style_tags", {})
            if not isinstance(style_tags, dict):
                style_tags = {}

            sentiment = result.get("sentiment", "neutral")
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"

            language_patterns = result.get("language_patterns", [])
            if not isinstance(language_patterns, list):
                language_patterns = []

            confidence_score = result.get("confidence_score", 0.5)
            if not isinstance(confidence_score, (int, float)):
                confidence_score = 0.5

            personality = PersonalityInsights(
                style_tags=style_tags,
                sentiment=sentiment,
                language_patterns=language_patterns,
                confidence_score=float(confidence_score),
            )

            logger.info(
                "個性分析成功",
                extra={
                    "sentiment": sentiment,
                    "confidence_score": confidence_score,
                },
            )

            return personality

        except Exception as e:
            logger.error(
                f"個性分析失敗: {e}",
                extra={"error": str(e)},
            )
            raise

