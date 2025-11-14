"""
@purpose: 模型版本管理，实现模型版本化、存储和加载接口
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class ModelRepository:
    """模型版本管理仓库"""

    def __init__(self, base_dir: str = "./models"):
        """
        初始化模型仓库

        Args:
            base_dir: 模型存储基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.info("初始化模型仓库", base_dir=str(self.base_dir))

    def list_versions(self) -> List[str]:
        """
        列出所有可用版本

        Returns:
            版本号列表
        """
        versions = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.startswith("eb-mm-lora-v"):
                version = item.name.replace("eb-mm-lora-", "")
                versions.append(version)

        versions.sort()
        logger.info("列出所有版本", versions=versions)
        return versions

    def get_latest_version(self) -> Optional[str]:
        """
        获取最新版本

        Returns:
            最新版本号，如果没有版本则返回 None
        """
        versions = self.list_versions()
        if not versions:
            return None

        latest = versions[-1]
        logger.info("获取最新版本", latest_version=latest)
        return latest

    def get_version_metadata(self, version: str) -> Optional[Dict]:
        """
        获取版本元数据

        Args:
            version: 版本号

        Returns:
            版本元数据字典，如果版本不存在则返回 None
        """
        adapter_dir = self.base_dir / f"eb-mm-lora-{version}"
        metadata_file = adapter_dir / "training_metadata.json"

        if not metadata_file.exists():
            logger.warning("版本元数据不存在", version=version)
            return None

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        logger.info("获取版本元数据", version=version)
        return metadata

    def get_adapter_path(self, version: str) -> Optional[Path]:
        """
        获取适配器路径

        Args:
            version: 版本号

        Returns:
            适配器目录路径，如果版本不存在则返回 None
        """
        adapter_dir = self.base_dir / f"eb-mm-lora-{version}"

        if not adapter_dir.exists():
            logger.warning("适配器目录不存在", version=version)
            return None

        # 验证适配器文件完整性
        adapter_config = adapter_dir / "adapter_config.json"
        adapter_model = adapter_dir / "adapter_model.bin"

        if not adapter_config.exists() or not adapter_model.exists():
            logger.warning("适配器文件不完整", version=version)
            return None

        logger.info("获取适配器路径", version=version, path=str(adapter_dir))
        return adapter_dir

    def save_version_metadata(
        self,
        version: str,
        base_model: str,
        training_params: Dict,
        performance_metrics: Dict,
        data_stats: Dict,
    ) -> bool:
        """
        保存版本元数据

        Args:
            version: 版本号
            base_model: 基础模型名称
            training_params: 训练参数
            performance_metrics: 性能指标
            data_stats: 数据统计

        Returns:
            是否保存成功
        """
        adapter_dir = self.base_dir / f"eb-mm-lora-{version}"
        adapter_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "version": version,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "base_model": base_model,
            "training_params": training_params,
            "performance_metrics": performance_metrics,
            "data_stats": data_stats,
        }

        metadata_file = adapter_dir / "training_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info("保存版本元数据", version=version)
        return True

    def delete_version(self, version: str) -> bool:
        """
        删除版本（谨慎使用）

        Args:
            version: 版本号

        Returns:
            是否删除成功
        """
        adapter_dir = self.base_dir / f"eb-mm-lora-{version}"

        if not adapter_dir.exists():
            logger.warning("版本不存在", version=version)
            return False

        import shutil

        shutil.rmtree(adapter_dir)
        logger.info("删除版本", version=version)
        return True

    def get_version_info(self, version: str) -> Optional[Dict]:
        """
        获取版本详细信息

        Args:
            version: 版本号

        Returns:
            版本信息字典，包含路径和元数据
        """
        adapter_path = self.get_adapter_path(version)
        if not adapter_path:
            return None

        metadata = self.get_version_metadata(version)

        return {
            "version": version,
            "adapter_path": str(adapter_path),
            "metadata": metadata,
        }

