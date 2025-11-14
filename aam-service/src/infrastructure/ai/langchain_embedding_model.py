"""
@purpose: 使用 LangChain LLM 進行語義分析（NER, KE, KT 和個性分析），作為降級策略的優先級 2
@author: DanielChung and AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional

import structlog
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.config.settings import AISettings, get_settings
from src.core.interfaces.i_analysis_model import IAnalysisModel
from src.models.domain.database import KnowledgeAsset
from src.models.domain.personality import PersonalityInsights

logger = structlog.get_logger(__name__)


class LangChainEmbeddingModel(IAnalysisModel):
    """
    使用 LangChain LLM 進行語義分析
    
    支持的功能：
    - NER (命名實體識別)
    - KE (知識提取)
    - KT (知識三元組提取)
    - 個性分析
    
    使用 LCEL (LangChain Expression Language) 構建提取鏈
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 120,
        settings: Optional[AISettings] = None,
    ):
        """
        初始化 LangChain Embedding 模型

        Args:
            model_name: LLM 模型名稱（如 gpt-3.5-turbo, gpt-4 等）
            api_key: API 密鑰（如果為 None，則從環境變量獲取）
            base_url: API 基礎 URL（如果為 None，則使用默認值）
            timeout: 請求超時時間（秒）
            settings: AI 配置（可選）
        """
        self.model_name = model_name
        self.timeout = timeout
        self.settings = settings or get_settings().ai

        # 獲取 API 密鑰
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning(
                "未提供 OpenAI API 密鑰，將嘗試從環境變量獲取"
            )

        # 初始化 LangChain OpenAI ChatModel
        try:
            llm_kwargs = {
                "model": self.model_name,
                "temperature": 0.0,  # 使用低溫度以獲得一致輸出
                "timeout": self.timeout,
            }
            
            if self.api_key:
                llm_kwargs["api_key"] = self.api_key
            
            if base_url:
                llm_kwargs["base_url"] = base_url

            self.llm = ChatOpenAI(**llm_kwargs)
            
            logger.info(
                "LangChain Embedding 模型初始化成功",
                extra={
                    "model_name": self.model_name,
                    "base_url": base_url or "default",
                },
            )
        except Exception as e:
            logger.error(
                f"LangChain Embedding 模型初始化失敗: {e}",
                extra={
                    "model_name": self.model_name,
                    "error": str(e),
                },
            )
            raise

        # 初始化 JSON 輸出解析器
        self.json_parser = JsonOutputParser()

        # 定義 Prompt 模板
        self._init_prompts()

    def _init_prompts(self):
        """初始化 Prompt 模板"""
        # NER 提取 Prompt
        self.ner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的命名實體識別系統。請從文本中提取所有命名實體（人名、地名、組織名、產品名、時間、地點等）。",
                ),
                (
                    "human",
                    "請從以下文本中提取命名實體：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"entities\": [\"實體1\", \"實體2\", ...],\n  \"entity_types\": {{\n    \"實體1\": \"類型1\",\n    \"實體2\": \"類型2\"\n  }}\n}}",
                ),
            ]
        )

        # KE 提取 Prompt
        self.ke_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一個專業的知識提取系統。請從文本中提取關鍵知識（重要概念、事實、觀點等）。",
                ),
                (
                    "human",
                    "請從以下文本中提取關鍵知識：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"key_points\": [\"知識點1\", \"知識點2\", ...],\n  \"concepts\": [\"概念1\", \"概念2\", ...]\n}}",
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
                    "請分析以下文本的個性特徵：\n\n文本：{text}\n\n請以 JSON 格式返回，格式如下：\n{{\n  \"style_tags\": [\"formal\", \"technical\", ...],\n  \"emotion\": \"positive|negative|neutral\",\n  \"language_patterns\": [\"簡潔\", \"詳細\", ...],\n  \"tone\": \"專業|友好|正式|隨意\",\n  \"confidence_score\": 0.85\n}}",
                ),
            ]
        )

    async def check_available(self) -> bool:
        """
        檢查 LangChain Embedding 模型服務是否可用

        Returns:
            True 如果服務可用，False 否則
        """
        try:
            # 嘗試調用模型進行簡單測試
            from langchain_core.prompts import ChatPromptTemplate
            test_prompt = ChatPromptTemplate.from_messages([
                ("human", "請回答：OK")
            ])
            test_chain = test_prompt | self.llm
            
            result = await test_chain.ainvoke({})
            return result is not None and len(str(result.content)) > 0
        except Exception as e:
            logger.warning(
                f"LangChain Embedding 服務不可用: {e}",
                extra={"error": str(e)},
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
        if not text or not text.strip():
            logger.warning(
                "輸入文本為空，返回空知識資產",
                extra={
                    "user_id": user_id,
                    "session_id": session_id,
                },
            )
            return KnowledgeAsset(
                user_id=user_id,
                session_id=session_id,
                timestamp=int(datetime.utcnow().timestamp()),
                source_type="dialogue",
                entities=[],
                triples_json="[]",
            )

        try:
            # 提取 NER 和 KT
            entities = await self._extract_ner(text)
            triples = await self._extract_kt(text)

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
            # 使用 LCEL 構建鏈
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
            # 使用 LCEL 構建鏈
            chain = self.kt_prompt | self.llm | self.json_parser

            # 調用模型
            result = await chain.ainvoke({"text": text})

            # 提取三元組
            triples = result.get("triples", [])
            if not isinstance(triples, list):
                triples = []

            # 驗證三元組格式（確保 subject, predicate, object 完整）
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
        if not text or not text.strip():
            logger.warning("輸入文本為空，返回默認個性分析結果")
            return PersonalityInsights(
                style_tags={},
                sentiment="neutral",
                language_patterns=[],
                confidence_score=0.0,
            )

        try:
            # 使用 LCEL 構建鏈
            chain = self.personality_prompt | self.llm | self.json_parser

            # 調用模型
            result = await chain.ainvoke({"text": text})

            # 提取個性分析結果
            style_tags_list = result.get("style_tags", [])
            if isinstance(style_tags_list, list):
                # 將列表轉換為字典格式（每個標籤計數為 1）
                style_tags = {tag: 1 for tag in style_tags_list if isinstance(tag, str)}
            elif isinstance(style_tags_list, dict):
                style_tags = style_tags_list
            else:
                style_tags = {}

            sentiment = result.get("emotion", result.get("sentiment", "neutral"))
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"

            language_patterns = result.get("language_patterns", [])
            if not isinstance(language_patterns, list):
                language_patterns = []

            confidence_score = result.get("confidence_score", 0.5)
            if not isinstance(confidence_score, (int, float)):
                confidence_score = 0.5
            confidence_score = float(max(0.0, min(1.0, confidence_score)))

            personality = PersonalityInsights(
                style_tags=style_tags,
                sentiment=sentiment,
                language_patterns=language_patterns,
                confidence_score=confidence_score,
            )

            logger.info(
                "個性分析成功",
                extra={
                    "sentiment": sentiment,
                    "confidence_score": confidence_score,
                    "style_tags_count": len(style_tags),
                },
            )

            return personality

        except Exception as e:
            logger.error(
                f"個性分析失敗: {e}",
                extra={"error": str(e)},
            )
            raise

