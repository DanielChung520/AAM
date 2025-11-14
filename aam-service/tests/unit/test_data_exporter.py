"""
@purpose: 数据导出器单元测试
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.domain.database import KnowledgeAsset
from src.training.data_exporter import DataExporter


class TestDataExporter:
    """数据导出器测试类"""

    @pytest.fixture
    def exporter(self):
        """创建数据导出器实例"""
        return DataExporter(export_days=7, quality_threshold=0.0)

    @pytest.fixture
    def sample_asset(self):
        """创建示例知识资产"""
        return KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1706342400,  # 2024-01-27 00:00:00
            source_type="dialogue",
            entities=["张三", "销售部门", "订单 #12345"],
            triples_json='[{"subject": "张三", "predicate": "属于", "object": "销售部门"}]',
        )

    def test_init(self, exporter):
        """测试初始化"""
        assert exporter.export_days == 7
        assert exporter.quality_threshold == 0.0
        assert exporter.knowledge_store is not None

    def test_filter_high_quality_data(self, exporter, sample_asset):
        """测试高质量数据过滤"""
        # 测试包含实体的数据
        assets_with_entities = [sample_asset]
        filtered = exporter._filter_high_quality_data(assets_with_entities)
        assert len(filtered) == 1

        # 测试包含三元组的数据
        asset_with_triples = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1706342400,
            source_type="dialogue",
            entities=[],
            triples_json='[{"subject": "A", "predicate": "B", "object": "C"}]',
        )
        filtered = exporter._filter_high_quality_data([asset_with_triples])
        assert len(filtered) == 1

        # 测试空数据
        empty_asset = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1706342400,
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        filtered = exporter._filter_high_quality_data([empty_asset])
        assert len(filtered) == 0

    def test_format_ner_sample(self, exporter, sample_asset):
        """测试 NER 样本格式化"""
        text_content = "我想了解订单 #12345 的状态，请联系销售部门的张三。"
        sample = exporter._format_ner_sample(sample_asset, text_content)

        assert sample is not None
        assert "instruction" in sample
        assert "input" in sample
        assert "output" in sample
        assert sample["input"] == text_content

        # 验证输出格式
        output_data = json.loads(sample["output"])
        assert "entities" in output_data
        assert len(output_data["entities"]) > 0

    def test_format_ke_sample(self, exporter, sample_asset):
        """测试 KE 样本格式化"""
        text_content = "我想了解订单 #12345 的状态，请联系销售部门的张三。"
        sample = exporter._format_ke_sample(sample_asset, text_content)

        assert sample is not None
        assert "instruction" in sample
        assert "input" in sample
        assert "output" in sample

        # 验证输出格式
        output_data = json.loads(sample["output"])
        assert "key_points" in output_data

    def test_format_kt_sample(self, exporter, sample_asset):
        """测试 KT 样本格式化"""
        text_content = "我想了解订单 #12345 的状态，请联系销售部门的张三。"
        sample = exporter._format_kt_sample(sample_asset, text_content)

        assert sample is not None
        assert "instruction" in sample
        assert "input" in sample
        assert "output" in sample

        # 验证输出格式
        output_data = json.loads(sample["output"])
        assert isinstance(output_data, list)
        if len(output_data) > 0:
            assert "subject" in output_data[0]
            assert "predicate" in output_data[0]
            assert "object" in output_data[0]

    def test_format_kt_sample_empty_triples(self, exporter):
        """测试空三元组的 KT 样本格式化"""
        empty_asset = KnowledgeAsset(
            user_id="user123",
            session_id="session456",
            timestamp=1706342400,
            source_type="dialogue",
            entities=[],
            triples_json="[]",
        )
        sample = exporter._format_kt_sample(empty_asset, "test text")
        assert sample is None

    def test_format_sample_unknown_task_type(self, exporter, sample_asset):
        """测试未知任务类型"""
        sample = exporter._format_sample(sample_asset, "test text", "unknown")
        assert sample is None

    @pytest.mark.asyncio
    async def test_query_knowledge_assets_empty(self, exporter):
        """测试查询空数据"""
        with patch.object(
            exporter.knowledge_store.collection, "get", return_value={"ids": []}
        ):
            assets = await exporter._query_knowledge_assets(0, 9999999999)
            assert len(assets) == 0

    @pytest.mark.asyncio
    async def test_extract_text_from_asset_fallback(self, exporter, sample_asset):
        """测试从资产提取文本的后备方案"""
        with patch.object(
            exporter.knowledge_store.collection,
            "get",
            side_effect=Exception("Connection error"),
        ):
            text = exporter._extract_text_from_asset(sample_asset)
            # 应该使用后备方案从实体和三元组构建文本
            assert text is not None
            assert "实体" in text or "三元组" in text

