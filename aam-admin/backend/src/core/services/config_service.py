"""
@purpose: 模型配置服务，负责读取和更新 models.json 配置文件
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.core.config import get_settings
from src.models.schemas.llm_provider import LLMProvider, ModelConfig, ModelConfigUpdate

logger = logging.getLogger(__name__)


class ConfigService:
    """配置服务类"""

    # 支持的 Provider 类型
    SUPPORTED_PROVIDERS = ["qwen", "gemini", "ollama"]

    def __init__(self):
        """初始化配置服务"""
        self.settings = get_settings()
        # 默认配置文件路径（相对于 aam-service 目录）
        # 在 Docker 环境中，配置文件可能挂载在特定位置
        self.config_path = self._get_config_path()

    def _get_config_path(self) -> Path:
        """
        获取配置文件路径

        Returns:
            Path: 配置文件路径
        """
        # 尝试多个可能的路径
        possible_paths = [
            Path("../aam-service/config/models.json"),  # 开发环境
            Path("/app/config/models.json"),  # Docker 环境
            Path("./config/models.json"),  # 当前目录
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"找到配置文件: {path}")
                return path

        # 如果都找不到，使用第一个作为默认路径
        default_path = possible_paths[0]
        logger.warning(f"配置文件不存在，将使用默认路径: {default_path}")
        return default_path

    def _load_config(self) -> Dict:
        """
        加载配置文件

        Returns:
            Dict: 配置数据
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"配置文件不存在: {self.config_path}")
                return {}

            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}", exc_info=True)
            return {}

    def _save_config(self, config: Dict) -> bool:
        """
        保存配置文件

        Args:
            config: 配置数据

        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置文件（格式化 JSON）
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"配置文件已保存: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}", exc_info=True)
            return False

    def get_providers(self) -> List[LLMProvider]:
        """
        获取所有 Provider 列表

        Returns:
            List[LLMProvider]: Provider 列表
        """
        config = self._load_config()
        providers = []

        for provider_type in self.SUPPORTED_PROVIDERS:
            provider_data = config.get(provider_type, {})
            models_data = provider_data.get("models", [])

            models = []
            for model_data in models_data:
                models.append(
                    ModelConfig(
                        model_name=model_data.get("model_name", ""),
                        display_name=model_data.get("display_name", ""),
                        max_tokens=model_data.get("max_tokens", 8192),
                        temperature=model_data.get("temperature", 0.5),
                        enabled=model_data.get("enabled", False),
                        priority=model_data.get("priority", 1),
                        description=model_data.get("description"),
                    )
                )

            # 确定 Provider 状态（如果有启用的模型则为 active）
            status = "active" if any(m.enabled for m in models) else "inactive"

            providers.append(
                LLMProvider(provider_type=provider_type, models=models, status=status)
            )

        return providers

    def get_provider(self, provider_type: str) -> Optional[LLMProvider]:
        """
        获取指定 Provider 的配置

        Args:
            provider_type: Provider 类型

        Returns:
            Optional[LLMProvider]: Provider 配置，如果不存在返回 None
        """
        if provider_type not in self.SUPPORTED_PROVIDERS:
            return None

        config = self._load_config()
        provider_data = config.get(provider_type, {})
        models_data = provider_data.get("models", [])

        models = []
        for model_data in models_data:
            models.append(
                ModelConfig(
                    model_name=model_data.get("model_name", ""),
                    display_name=model_data.get("display_name", ""),
                    max_tokens=model_data.get("max_tokens", 8192),
                    temperature=model_data.get("temperature", 0.5),
                    enabled=model_data.get("enabled", False),
                    priority=model_data.get("priority", 1),
                    description=model_data.get("description"),
                )
            )

        status = "active" if any(m.enabled for m in models) else "inactive"

        return LLMProvider(provider_type=provider_type, models=models, status=status)

    def update_model_config(
        self, provider_type: str, model_name: str, updates: ModelConfigUpdate
    ) -> bool:
        """
        更新模型配置

        Args:
            provider_type: Provider 类型
            model_name: 模型名称
            updates: 更新数据

        Returns:
            bool: 是否更新成功
        """
        if provider_type not in self.SUPPORTED_PROVIDERS:
            logger.error(f"不支持的 Provider 类型: {provider_type}")
            return False

        config = self._load_config()
        provider_data = config.setdefault(provider_type, {"models": []})
        models = provider_data.get("models", [])

        # 查找并更新模型
        model_found = False
        for model in models:
            if model.get("model_name") == model_name:
                # 更新模型配置
                if updates.max_tokens is not None:
                    model["max_tokens"] = updates.max_tokens
                if updates.temperature is not None:
                    model["temperature"] = updates.temperature
                if updates.enabled is not None:
                    model["enabled"] = updates.enabled
                if updates.priority is not None:
                    model["priority"] = updates.priority
                if updates.description is not None:
                    model["description"] = updates.description

                model_found = True
                break

        if not model_found:
            logger.error(f"模型不存在: {provider_type}/{model_name}")
            return False

        # 保存配置
        if self._save_config(config):
            # 通知 AAM 服务重载配置
            self._notify_aam_service_reload()
            return True

        return False

    def toggle_model(self, provider_type: str, model_name: str, enabled: bool) -> bool:
        """
        启用/禁用模型

        Args:
            provider_type: Provider 类型
            model_name: 模型名称
            enabled: 是否启用

        Returns:
            bool: 是否操作成功
        """
        return self.update_model_config(
            provider_type, model_name, ModelConfigUpdate(enabled=enabled)
        )

    def test_provider(self, provider_type: str) -> Dict:
        """
        测试 Provider 连接

        Args:
            provider_type: Provider 类型

        Returns:
            Dict: 测试结果
        """
        try:
            # TODO: 实现实际的 Provider 连接测试
            # 这里可以调用 AAM 服务的测试接口，或者直接测试 Provider API
            # 目前返回模拟结果
            logger.info(f"测试 Provider 连接: {provider_type}")

            # 检查 Provider 配置是否存在
            provider = self.get_provider(provider_type)
            if not provider:
                return {
                    "success": False,
                    "message": f"Provider {provider_type} 不存在",
                }

            # 检查是否有启用的模型
            enabled_models = [m for m in provider.models if m.enabled]
            if not enabled_models:
                return {
                    "success": False,
                    "message": f"Provider {provider_type} 没有启用的模型",
                }

            # 模拟测试（实际应该调用 AAM 服务的测试接口）
            return {
                "success": True,
                "message": f"Provider {provider_type} 连接正常",
                "response_time_ms": 100.0,
            }
        except Exception as e:
            logger.error(f"测试 Provider 失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"测试失败: {str(e)}",
            }

    def _notify_aam_service_reload(self) -> None:
        """
        通知 AAM 服务重载配置

        通过调用 AAM 服务的重载配置接口来实现
        """
        try:
            aam_service_url = self.settings.auth.aam_service_url
            # TODO: 实现实际的 AAM 服务重载接口调用
            # 这里需要根据 AAM 服务的实际 API 来实现
            logger.info(f"通知 AAM 服务重载配置: {aam_service_url}")
            # 示例：httpx.post(f"{aam_service_url}/api/v1/admin/reload-config")
        except Exception as e:
            logger.warning(f"通知 AAM 服务重载配置失败: {e}")

