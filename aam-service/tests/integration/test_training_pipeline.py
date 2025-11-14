"""
@purpose: 训练管道集成测试
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.training.data_exporter import DataExporter
from src.training.model_repository import ModelRepository


class TestTrainingPipeline:
    """训练管道集成测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def exporter(self):
        """创建数据导出器实例"""
        return DataExporter(export_days=7, quality_threshold=0.0)

    @pytest.fixture
    def repository(self, temp_dir):
        """创建模型仓库实例"""
        return ModelRepository(base_dir=temp_dir)

    @pytest.mark.asyncio
    async def test_export_and_version_management(self, exporter, repository, temp_dir):
        """测试数据导出和版本管理集成"""
        # 模拟 ChromaDB 数据
        sample_assets = [
            {
                "ids": ["doc1"],
                "metadatas": [
                    {
                        "user_id": "user123",
                        "session_id": "session456",
                        "timestamp": 1706342400,
                        "source_type": "dialogue",
                        "entities": "张三,销售部门",
                        "triples_json": '[{"subject": "张三", "predicate": "属于", "object": "销售部门"}]',
                    }
                ],
                "documents": ["我想了解订单 #12345 的状态，请联系销售部门的张三。"],
            }
        ]

        with patch.object(
            exporter.knowledge_store.collection, "get", return_value=sample_assets[0]
        ):
            # 导出训练数据
            output_path = str(Path(temp_dir) / "training_data.jsonl")
            stats = await exporter.export_training_data(
                output_path, task_types=["ner", "kt"]
            )

            # 验证导出结果
            assert "ner" in stats
            assert "kt" in stats
            assert Path(output_path).exists()

            # 验证 JSONL 文件格式
            with open(output_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                assert len(lines) > 0

                for line in lines:
                    sample = json.loads(line.strip())
                    assert "instruction" in sample
                    assert "input" in sample
                    assert "output" in sample

            # 保存版本元数据
            version = "v1"
            result = repository.save_version_metadata(
                version,
                "deepseek-r1:8b",
                {"r": 8, "lora_alpha": 16},
                {"ner_accuracy": 0.85, "kt_accuracy": 0.78},
                {"num_samples": stats["ner"] + stats["kt"]},
            )

            assert result is True

            # 验证版本信息
            metadata = repository.get_version_metadata(version)
            assert metadata is not None
            assert metadata["version"] == version

