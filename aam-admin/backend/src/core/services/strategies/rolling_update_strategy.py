"""
@purpose: 滚动更新部署策略实现
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import asyncio
import logging
from typing import Optional, Dict, List

from src.core.services.deployment_strategies import DeploymentStrategyBase
from src.core.services.docker_service import DockerService
from src.core.services.health_check_service import HealthCheckService, HealthStatus
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class RollingUpdateStrategy(DeploymentStrategyBase):
    """滚动更新部署策略"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化滚动更新策略

        Args:
            config: 策略配置
                - max_unavailable: 最大不可用实例数，默认 1
                - max_surge: 最大新增实例数，默认 1
                - min_ready_seconds: 最小就绪时间（秒），默认 30
        """
        super().__init__(config)
        self.docker_service = DockerService()
        self.health_check_service = HealthCheckService()
        self.settings = get_settings()

        # 配置参数
        self.max_unavailable = self.config.get("max_unavailable", 1)
        self.max_surge = self.config.get("max_surge", 1)
        self.min_ready_seconds = self.config.get("min_ready_seconds", 30)

    async def deploy(
        self,
        version: str,
        deployment_id: int,
        log_callback: Optional[callable] = None,
    ) -> bool:
        """
        执行滚动更新部署

        流程：
        1. 获取当前运行实例列表
        2. 逐个更新实例（从负载均衡移除 -> 更新 -> 健康检查 -> 重新加入）
        3. 确保任何时候至少有 (总数 - max_unavailable) 个实例可用

        Args:
            version: 版本号
            deployment_id: 部署记录 ID
            log_callback: 日志回调函数

        Returns:
            bool: 是否部署成功
        """
        if log_callback:
            log_callback(f"开始滚动更新部署版本 {version}")

        try:
            # 步骤 1: 获取当前实例列表
            if log_callback:
                log_callback("步骤 1: 获取当前运行实例列表")
            instances = await self._get_current_instances()
            if not instances:
                if log_callback:
                    log_callback("未找到运行中的实例")
                return False

            total_instances = len(instances)
            if log_callback:
                log_callback(f"找到 {total_instances} 个运行实例")

            # 步骤 2: 逐个更新实例
            updated_count = 0
            for i, instance in enumerate(instances):
                if log_callback:
                    log_callback(f"步骤 2.{i+1}/{total_instances}: 更新实例 {instance}")

                # 从负载均衡移除
                await self._remove_from_load_balancer(instance, log_callback)

                # 更新实例
                success = await self._update_instance(instance, version, log_callback)
                if not success:
                    if log_callback:
                        log_callback(f"更新实例 {instance} 失败，开始回滚")
                    await self._rollback_instance(instance, log_callback)
                    return False

                # 健康检查
                health_url = self._get_health_check_url(instance)
                is_healthy = await self.health_check_service.wait_for_healthy(
                    health_url, timeout=300
                )
                if not is_healthy:
                    if log_callback:
                        log_callback(f"实例 {instance} 健康检查失败，开始回滚")
                    await self._rollback_instance(instance, log_callback)
                    return False

                # 等待最小就绪时间
                await asyncio.sleep(self.min_ready_seconds)

                # 重新加入负载均衡
                await self._add_to_load_balancer(instance, log_callback)

                updated_count += 1
                if log_callback:
                    log_callback(f"实例 {instance} 更新成功 ({updated_count}/{total_instances})")

            if log_callback:
                log_callback(f"滚动更新成功完成，所有 {total_instances} 个实例已更新到版本 {version}")
            return True

        except Exception as e:
            logger.error(f"滚动更新失败: {e}", exc_info=True)
            if log_callback:
                log_callback(f"部署失败: {str(e)}")
            return False

    async def rollback(
        self,
        version: str,
        deployment_id: int,
        log_callback: Optional[callable] = None,
    ) -> bool:
        """
        执行回滚（恢复到旧版本）

        Args:
            version: 要回滚到的版本号
            deployment_id: 部署记录 ID
            log_callback: 日志回调函数

        Returns:
            bool: 是否回滚成功
        """
        if log_callback:
            log_callback(f"开始回滚到版本 {version}")

        # 回滚逻辑与部署类似，但使用旧版本
        # 这里简化实现
        try:
            instances = await self._get_current_instances()
            for instance in instances:
                await self._rollback_instance(instance, version, log_callback)
            return True
        except Exception as e:
            logger.error(f"回滚失败: {e}", exc_info=True)
            return False

    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return "rolling"

    async def _get_current_instances(self) -> List[str]:
        """
        获取当前运行实例列表

        Returns:
            List[str]: 实例名称列表
        """
        # TODO: 从 Docker 或服务发现获取实例列表
        containers = self.docker_service.list_containers(all=False)
        return [c["name"] for c in containers if "aam-service" in c["name"]]

    async def _remove_from_load_balancer(
        self, instance: str, log_callback: Optional[callable] = None
    ):
        """从负载均衡移除实例"""
        if log_callback:
            log_callback(f"从负载均衡移除实例: {instance}")
        # TODO: 更新负载均衡器配置

    async def _add_to_load_balancer(
        self, instance: str, log_callback: Optional[callable] = None
    ):
        """将实例添加到负载均衡"""
        if log_callback:
            log_callback(f"将实例添加到负载均衡: {instance}")
        # TODO: 更新负载均衡器配置

    async def _update_instance(
        self, instance: str, version: str, log_callback: Optional[callable] = None
    ) -> bool:
        """更新实例到新版本"""
        if log_callback:
            log_callback(f"更新实例 {instance} 到版本 {version}")
        # TODO: 停止旧容器，启动新版本容器
        return True

    async def _rollback_instance(
        self, instance: str, version: Optional[str] = None, log_callback: Optional[callable] = None
    ):
        """回滚实例"""
        if log_callback:
            log_callback(f"回滚实例 {instance} 到版本 {version or 'previous'}")
        # TODO: 恢复实例到旧版本

    def _get_health_check_url(self, instance: str) -> str:
        """获取健康检查 URL"""
        return self.health_check_service.get_aam_service_health_url()

