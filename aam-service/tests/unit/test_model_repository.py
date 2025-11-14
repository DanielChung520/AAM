"""
@purpose: 模型版本管理单元测试
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.training.model_repository import ModelRepository


class TestModelRepository:
    """模型版本管理测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def repository(self, temp_dir):
        """创建模型仓库实例"""
        return ModelRepository(base_dir=temp_dir)

    def test_init(self, repository, temp_dir):
        """测试初始化"""
        assert repository.base_dir == Path(temp_dir)
        assert repository.base_dir.exists()

    def test_list_versions_empty(self, repository):
        """测试列出空版本列表"""
        versions = repository.list_versions()
        assert versions == []

    def test_get_latest_version_empty(self, repository):
        """测试获取最新版本（空列表）"""
        latest = repository.get_latest_version()
        assert latest is None

    def test_save_version_metadata(self, repository):
        """测试保存版本元数据"""
        version = "v1"
        base_model = "deepseek-r1:8b"
        training_params = {"r": 8, "lora_alpha": 16, "num_epochs": 3}
        performance_metrics = {"ner_accuracy": 0.85, "kt_accuracy": 0.78}
        data_stats = {"num_samples": 1000}

        result = repository.save_version_metadata(
            version, base_model, training_params, performance_metrics, data_stats
        )

        assert result is True
        metadata_file = repository.base_dir / f"eb-mm-lora-{version}" / "training_metadata.json"
        assert metadata_file.exists()

        # 验证元数据内容
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        assert metadata["version"] == version
        assert metadata["base_model"] == base_model
        assert metadata["training_params"] == training_params
        assert metadata["performance_metrics"] == performance_metrics
        assert metadata["data_stats"] == data_stats

    def test_get_version_metadata(self, repository):
        """测试获取版本元数据"""
        version = "v1"
        base_model = "deepseek-r1:8b"
        training_params = {"r": 8}
        performance_metrics = {"ner_accuracy": 0.85}
        data_stats = {"num_samples": 1000}

        repository.save_version_metadata(
            version, base_model, training_params, performance_metrics, data_stats
        )

        metadata = repository.get_version_metadata(version)
        assert metadata is not None
        assert metadata["version"] == version

    def test_get_version_metadata_not_found(self, repository):
        """测试获取不存在的版本元数据"""
        metadata = repository.get_version_metadata("v999")
        assert metadata is None

    def test_list_versions(self, repository):
        """测试列出所有版本"""
        # 创建多个版本
        for i in range(1, 4):
            version = f"v{i}"
            repository.save_version_metadata(
                version,
                "deepseek-r1:8b",
                {"r": 8},
                {"ner_accuracy": 0.85},
                {"num_samples": 1000},
            )

        versions = repository.list_versions()
        assert len(versions) == 3
        assert "v1" in versions
        assert "v2" in versions
        assert "v3" in versions

    def test_get_latest_version(self, repository):
        """测试获取最新版本"""
        # 创建多个版本
        for i in range(1, 4):
            version = f"v{i}"
            repository.save_version_metadata(
                version,
                "deepseek-r1:8b",
                {"r": 8},
                {"ner_accuracy": 0.85},
                {"num_samples": 1000},
            )

        latest = repository.get_latest_version()
        assert latest == "v3"

    def test_get_adapter_path_not_found(self, repository):
        """测试获取不存在的适配器路径"""
        path = repository.get_adapter_path("v999")
        assert path is None

    def test_get_version_info(self, repository):
        """测试获取版本信息"""
        version = "v1"
        repository.save_version_metadata(
            version,
            "deepseek-r1:8b",
            {"r": 8},
            {"ner_accuracy": 0.85},
            {"num_samples": 1000},
        )

        # 创建适配器文件（模拟）
        adapter_dir = repository.base_dir / f"eb-mm-lora-{version}"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        (adapter_dir / "adapter_config.json").write_text("{}")
        (adapter_dir / "adapter_model.bin").write_bytes(b"dummy")

        info = repository.get_version_info(version)
        assert info is not None
        assert info["version"] == version
        assert "adapter_path" in info
        assert "metadata" in info

    def test_delete_version(self, repository):
        """测试删除版本"""
        version = "v1"
        repository.save_version_metadata(
            version,
            "deepseek-r1:8b",
            {"r": 8},
            {"ner_accuracy": 0.85},
            {"num_samples": 1000},
        )

        adapter_dir = repository.base_dir / f"eb-mm-lora-{version}"
        assert adapter_dir.exists()

        result = repository.delete_version(version)
        assert result is True
        assert not adapter_dir.exists()

    def test_delete_version_not_found(self, repository):
        """测试删除不存在的版本"""
        result = repository.delete_version("v999")
        assert result is False

