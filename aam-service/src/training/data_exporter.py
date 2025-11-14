"""
@purpose: 从 ChromaDB 和 PostgreSQL 导出训练数据，清洗和格式化为 Instruction JSONL 格式
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import structlog

from src.config.settings import ChromaDBSettings, get_settings
from src.infrastructure.database.chroma_knowledge_store import ChromaKnowledgeStore
from src.models.domain.database import KnowledgeAsset

logger = structlog.get_logger(__name__)


class DataExporter:
    """数据导出器，从 ChromaDB 导出训练数据并格式化为 JSONL"""

    def __init__(
        self,
        chromadb_settings: Optional[ChromaDBSettings] = None,
        export_days: int = 7,
        quality_threshold: float = 0.0,
    ):
        """
        初始化数据导出器

        Args:
            chromadb_settings: ChromaDB 配置设置，如果为 None 则从全局配置加载
            export_days: 导出过去 N 天的数据，默认 7 天
            quality_threshold: 数据质量阈值，默认 0.0（不过滤）
        """
        self.settings = chromadb_settings or get_settings().chromadb
        self.export_days = export_days
        self.quality_threshold = quality_threshold
        self.knowledge_store = ChromaKnowledgeStore(chromadb_settings=self.settings)

    async def export_training_data(
        self,
        output_path: str,
        task_types: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        导出训练数据到 JSONL 文件

        Args:
            output_path: 输出文件路径
            task_types: 任务类型列表，可选值：["ner", "ke", "kt", "personality"]
                        如果为 None，则导出所有任务类型

        Returns:
            统计信息字典，包含各任务类型的样本数量
        """
        if task_types is None:
            task_types = ["ner", "ke", "kt"]

        logger.info(
            "开始导出训练数据",
            output_path=output_path,
            export_days=self.export_days,
            quality_threshold=self.quality_threshold,
            task_types=task_types,
        )

        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=self.export_days)
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        # 从 ChromaDB 查询数据
        knowledge_assets = await self._query_knowledge_assets(
            start_timestamp, end_timestamp
        )

        # 过滤高质量数据
        filtered_assets = self._filter_high_quality_data(knowledge_assets)

        logger.info(
            "数据查询完成",
            total_count=len(knowledge_assets),
            filtered_count=len(filtered_assets),
        )

        # 格式化为 JSONL
        training_samples = []
        stats = {task_type: 0 for task_type in task_types}

        for asset in filtered_assets:
            # 需要从 ChromaDB 获取原始文本内容
            # 这里暂时使用 metadata 中的信息，实际应该查询文档内容
            text_content = self._extract_text_from_asset(asset)

            if not text_content:
                continue

            # 为每个任务类型生成训练样本
            for task_type in task_types:
                sample = self._format_sample(asset, text_content, task_type)
                if sample:
                    training_samples.append(sample)
                    stats[task_type] += 1

        # 保存为 JSONL 文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            for sample in training_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        logger.info(
            "训练数据导出完成",
            output_path=str(output_file),
            total_samples=len(training_samples),
            stats=stats,
        )

        return stats

    async def _query_knowledge_assets(
        self, start_timestamp: int, end_timestamp: int
    ) -> List[KnowledgeAsset]:
        """
        从 ChromaDB 查询知识资产

        Args:
            start_timestamp: 开始时间戳
            end_timestamp: 结束时间戳

        Returns:
            知识资产列表
        """
        logger.info(
            "查询知识资产",
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

        knowledge_assets = []
        collection = self.knowledge_store.collection

        # 获取所有数据（ChromaDB 没有直接的时间范围查询，需要获取后过滤）
        # 注意：如果数据量很大，这可能会很慢，后续可以优化
        try:
            # 使用 get 方法获取所有数据，然后过滤
            all_data = collection.get()
            
            if not all_data or not all_data.get("ids"):
                logger.info("ChromaDB 中没有数据")
                return []

            # 遍历所有数据，过滤时间范围
            for i, doc_id in enumerate(all_data["ids"]):
                metadata = all_data["metadatas"][i] if all_data.get("metadatas") else {}
                timestamp = metadata.get("timestamp", 0)

                # 检查时间戳是否在范围内
                if isinstance(timestamp, str):
                    try:
                        timestamp = int(timestamp)
                    except ValueError:
                        logger.warning("无效的时间戳格式", doc_id=doc_id, timestamp=timestamp)
                        continue

                if start_timestamp <= timestamp <= end_timestamp:
                    try:
                        asset = KnowledgeAsset.from_chromadb_metadata(metadata)
                        knowledge_assets.append(asset)
                    except Exception as e:
                        logger.warning(
                            "解析知识资产失败",
                            doc_id=doc_id,
                            error=str(e),
                        )
                        continue

            logger.info(
                "查询完成",
                total_found=len(all_data["ids"]),
                filtered_count=len(knowledge_assets),
            )

        except Exception as e:
            logger.error("查询 ChromaDB 失败", error=str(e), exc_info=True)
            return []

        return knowledge_assets

    def _filter_high_quality_data(
        self, knowledge_assets: List[KnowledgeAsset]
    ) -> List[KnowledgeAsset]:
        """
        过滤高质量数据

        Args:
            knowledge_assets: 知识资产列表

        Returns:
            过滤后的知识资产列表
        """
        filtered = []
        for asset in knowledge_assets:
            # 过滤空文本或无效数据
            if not asset.entities and not asset.triples_json:
                continue

            # 保留包含实体或三元组的数据（高质量数据）
            if asset.entities or (
                asset.triples_json and asset.triples_json != "[]"
            ):
                filtered.append(asset)

        return filtered

    def _extract_text_from_asset(self, asset: KnowledgeAsset) -> Optional[str]:
        """
        从知识资产中提取文本内容

        Args:
            asset: 知识资产

        Returns:
            文本内容，如果无法提取则返回 None
        """
        # 从 ChromaDB 查询文档内容
        try:
            collection = self.knowledge_store.collection
            doc_id = f"{asset.session_id}_{asset.timestamp}"

            # 尝试获取文档
            results = collection.get(ids=[doc_id])
            if results and results.get("documents") and len(results["documents"]) > 0:
                return results["documents"][0]

            # 如果直接获取失败，尝试通过 metadata 查询
            # 构建查询条件
            where_clause = {
                "user_id": asset.user_id,
                "session_id": asset.session_id,
                "timestamp": asset.timestamp,
            }

            results = collection.get(where=where_clause)
            if results and results.get("documents") and len(results["documents"]) > 0:
                return results["documents"][0]

        except Exception as e:
            logger.warning("提取文本内容失败", error=str(e), asset=asset)

        # 如果无法从 ChromaDB 获取，尝试从实体和三元组构建文本
        # 这是一个后备方案
        text_parts = []
        if asset.entities:
            text_parts.append(f"实体: {', '.join(asset.entities)}")
        if asset.triples_json and asset.triples_json != "[]":
            try:
                triples = json.loads(asset.triples_json)
                if triples:
                    triple_texts = [
                        f"{t.get('subject', '')} - {t.get('predicate', '')} - {t.get('object', '')}"
                        for t in triples
                    ]
                    text_parts.append(f"三元组: {'; '.join(triple_texts)}")
            except json.JSONDecodeError:
                pass

        if text_parts:
            return " | ".join(text_parts)

        return None

    def _format_sample(
        self, asset: KnowledgeAsset, text_content: str, task_type: str
    ) -> Optional[Dict[str, str]]:
        """
        格式化为训练样本

        Args:
            asset: 知识资产
            text_content: 文本内容
            task_type: 任务类型（"ner", "ke", "kt", "personality"）

        Returns:
            训练样本字典，如果无法生成则返回 None
        """
        if task_type == "ner":
            return self._format_ner_sample(asset, text_content)
        elif task_type == "ke":
            return self._format_ke_sample(asset, text_content)
        elif task_type == "kt":
            return self._format_kt_sample(asset, text_content)
        elif task_type == "personality":
            return self._format_personality_sample(asset, text_content)
        else:
            logger.warning("未知任务类型", task_type=task_type)
            return None

    def _format_ner_sample(
        self, asset: KnowledgeAsset, text_content: str
    ) -> Optional[Dict[str, str]]:
        """格式化 NER 任务样本"""
        if not asset.entities:
            return None

        instruction = "请从以下文本中提取命名实体（人名、地名、组织名、产品名等）。"
        output = json.dumps(
            {"entities": asset.entities, "entity_types": {}}, ensure_ascii=False
        )

        return {
            "instruction": instruction,
            "input": text_content,
            "output": output,
        }

    def _format_ke_sample(
        self, asset: KnowledgeAsset, text_content: str
    ) -> Optional[Dict[str, str]]:
        """格式化 KE 任务样本"""
        # KE 任务需要从实体中提取关键知识
        # 暂时使用实体作为关键知识点
        if not asset.entities:
            return None

        instruction = "请从以下文本中提取关键知识（重要概念、关键事实、核心观点等）。"
        output = json.dumps(
            {"key_points": asset.entities, "concepts": [], "facts": []},
            ensure_ascii=False,
        )

        return {
            "instruction": instruction,
            "input": text_content,
            "output": output,
        }

    def _format_kt_sample(
        self, asset: KnowledgeAsset, text_content: str
    ) -> Optional[Dict[str, str]]:
        """格式化 KT 任务样本"""
        if not asset.triples_json or asset.triples_json == "[]":
            return None

        instruction = "请从以下文本中提取知识三元组（主体-谓词-客体关系）。"
        output = asset.triples_json

        return {
            "instruction": instruction,
            "input": text_content,
            "output": output,
        }

    def _format_personality_sample(
        self, asset: KnowledgeAsset, text_content: str
    ) -> Optional[Dict[str, str]]:
        """格式化个性分析任务样本"""
        # 个性分析任务需要用户画像数据，暂时不实现
        return None

