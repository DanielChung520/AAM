"""
@purpose: 部署监控服务，提供部署指标收集和状态监控功能
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

import httpx
from sqlalchemy.orm import Session

from src.core.services.docker_service import DockerService
from src.core.services.health_check_service import HealthCheckService, HealthStatus
from src.core.services.metrics_service import MetricsService
from src.models.database import DeploymentRecord, DeploymentStatus
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class DeploymentMonitorService:
    """部署监控服务类"""

    def __init__(self, db: Session, docker_service: DockerService):
        """
        初始化部署监控服务

        Args:
            db: 数据库会话
            docker_service: Docker 服务实例
        """
        self.db = db
        self.docker_service = docker_service
        self.health_check_service = HealthCheckService()
        self.settings = get_settings()

        # 默认阈值配置
        self.default_thresholds = {
            "error_rate": 0.05,  # 5% 错误率
            "response_time": 2000,  # 2000ms 响应时间
            "cpu_usage": 90.0,  # 90% CPU 使用率
            "memory_usage": 90.0,  # 90% 内存使用率
            "health_check_failures": 3,  # 连续3次健康检查失败
        }

    async def collect_metrics(
        self,
        deployment_id: int,
        container_names: Optional[List[str]] = None,
        health_check_urls: Optional[List[str]] = None,
    ) -> Dict:
        """
        收集部署指标

        Args:
            deployment_id: 部署记录 ID
            container_names: 容器名称列表（可选）
            health_check_urls: 健康检查 URL 列表（可选）

        Returns:
            Dict: 部署指标
        """
        try:
            metrics = {
                "deployment_id": deployment_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error_rate": 0.0,
                "response_time": 0.0,
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "request_count": 0,
                "health_check_status": "unknown",
                "health_check_failures": 0,
            }

            # 收集容器资源指标
            if container_names:
                container_metrics = await self._collect_container_metrics(container_names)
                metrics.update(container_metrics)

            # 收集健康检查指标
            if health_check_urls:
                health_metrics = await self._collect_health_metrics(health_check_urls)
                metrics.update(health_metrics)

            # 收集应用指标（错误率、响应时间等）
            # 这里需要从应用监控系统或日志中获取
            # 简化处理，实际应该集成 Prometheus、Datadog 等监控系统
            app_metrics = await self._collect_application_metrics(deployment_id)
            metrics.update(app_metrics)

            return metrics

        except Exception as e:
            logger.error(f"收集部署指标失败: {e}", exc_info=True)
            return {
                "deployment_id": deployment_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    async def _collect_container_metrics(self, container_names: List[str]) -> Dict:
        """
        收集容器资源指标

        Args:
            container_names: 容器名称列表

        Returns:
            Dict: 容器指标
        """
        try:
            total_cpu = 0.0
            total_memory = 0.0
            total_memory_limit = 0.0
            container_count = 0

            for container_name in container_names:
                container_status = self.docker_service.get_container_status(container_name)
                if container_status:
                    total_cpu += container_status.get("cpu_usage", 0.0)
                    # 内存使用需要从容器统计中获取
                    # 这里简化处理
                    container_count += 1

            avg_cpu = total_cpu / container_count if container_count > 0 else 0.0
            avg_memory = total_memory / container_count if container_count > 0 else 0.0

            return {
                "cpu_usage": avg_cpu,
                "memory_usage": avg_memory,
                "container_count": container_count,
            }

        except Exception as e:
            logger.error(f"收集容器指标失败: {e}", exc_info=True)
            return {"cpu_usage": 0.0, "memory_usage": 0.0, "container_count": 0}

    async def _collect_health_metrics(self, health_check_urls: List[str]) -> Dict:
        """
        收集健康检查指标

        Args:
            health_check_urls: 健康检查 URL 列表

        Returns:
            Dict: 健康检查指标
        """
        try:
            healthy_count = 0
            unhealthy_count = 0
            failures = 0

            for url in health_check_urls:
                status = await self.health_check_service.check_health(url, timeout=5, retries=1)
                if status == HealthStatus.HEALTHY:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
                    failures += 1

            total = len(health_check_urls)
            health_status = (
                "healthy" if unhealthy_count == 0 else "unhealthy" if healthy_count == 0 else "degraded"
            )

            return {
                "health_check_status": health_status,
                "health_check_failures": failures,
                "healthy_count": healthy_count,
                "unhealthy_count": unhealthy_count,
                "health_check_total": total,
            }

        except Exception as e:
            logger.error(f"收集健康检查指标失败: {e}", exc_info=True)
            return {
                "health_check_status": "unknown",
                "health_check_failures": 0,
            }

    async def _collect_application_metrics(self, deployment_id: int) -> Dict:
        """
        收集应用指标（错误率、响应时间等）

        Args:
            deployment_id: 部署记录 ID

        Returns:
            Dict: 应用指标
        """
        try:
            # 这里应该从应用监控系统获取指标
            # 例如：Prometheus、Datadog、New Relic 等
            # 简化处理，返回默认值

            # 实际实现应该：
            # 1. 查询 Prometheus API 获取错误率和响应时间
            # 2. 从日志系统分析错误率
            # 3. 从 APM 系统获取性能指标

            return {
                "error_rate": 0.0,  # 从监控系统获取
                "response_time": 0.0,  # 从监控系统获取
                "request_count": 0,  # 从监控系统获取
            }

        except Exception as e:
            logger.error(f"收集应用指标失败: {e}", exc_info=True)
            return {
                "error_rate": 0.0,
                "response_time": 0.0,
                "request_count": 0,
            }

    async def check_thresholds(
        self, metrics: Dict, thresholds: Optional[Dict] = None
    ) -> tuple[bool, List[str]]:
        """
        检查指标是否超过阈值

        Args:
            metrics: 部署指标
            thresholds: 阈值配置（可选，使用默认阈值）

        Returns:
            tuple[bool, List[str]]: (是否超过阈值, 超过阈值的指标列表)
        """
        try:
            thresholds = thresholds or self.default_thresholds
            exceeded = []
            exceeded_thresholds = []

            # 检查错误率
            error_rate = metrics.get("error_rate", 0.0)
            error_threshold = thresholds.get("error_rate", 0.05)
            if error_rate > error_threshold:
                exceeded.append("error_rate")
                exceeded_thresholds.append(
                    f"错误率 {error_rate:.2%} 超过阈值 {error_threshold:.2%}"
                )

            # 检查响应时间
            response_time = metrics.get("response_time", 0.0)
            response_threshold = thresholds.get("response_time", 2000)
            if response_time > response_threshold:
                exceeded.append("response_time")
                exceeded_thresholds.append(
                    f"响应时间 {response_time}ms 超过阈值 {response_threshold}ms"
                )

            # 检查 CPU 使用率
            cpu_usage = metrics.get("cpu_usage", 0.0)
            cpu_threshold = thresholds.get("cpu_usage", 90.0)
            if cpu_usage > cpu_threshold:
                exceeded.append("cpu_usage")
                exceeded_thresholds.append(
                    f"CPU 使用率 {cpu_usage:.1f}% 超过阈值 {cpu_threshold:.1f}%"
                )

            # 检查内存使用率
            memory_usage = metrics.get("memory_usage", 0.0)
            memory_threshold = thresholds.get("memory_usage", 90.0)
            if memory_usage > memory_threshold:
                exceeded.append("memory_usage")
                exceeded_thresholds.append(
                    f"内存使用率 {memory_usage:.1f}% 超过阈值 {memory_threshold:.1f}%"
                )

            # 检查健康检查失败次数
            health_failures = metrics.get("health_check_failures", 0)
            health_threshold = thresholds.get("health_check_failures", 3)
            if health_failures >= health_threshold:
                exceeded.append("health_check_failures")
                exceeded_thresholds.append(
                    f"健康检查失败 {health_failures} 次，超过阈值 {health_threshold} 次"
                )

            return len(exceeded) > 0, exceeded_thresholds

        except Exception as e:
            logger.error(f"检查阈值失败: {e}", exc_info=True)
            return False, []

    async def update_deployment_status(
        self,
        deployment_id: int,
        metrics: Optional[Dict] = None,
        status: Optional[DeploymentStatus] = None,
    ) -> bool:
        """
        更新部署状态

        Args:
            deployment_id: 部署记录 ID
            metrics: 部署指标（可选）
            status: 部署状态（可选，如果不提供则根据指标判断）

        Returns:
            bool: 是否更新成功
        """
        try:
            deployment = (
                self.db.query(DeploymentRecord)
                .filter(DeploymentRecord.id == deployment_id)
                .first()
            )
            if not deployment:
                logger.error(f"部署记录不存在: {deployment_id}")
                return False

            # 如果提供了状态，直接更新
            if status:
                deployment.status = status
                deployment.updated_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"部署 {deployment_id} 状态已更新为: {status.value}")
                return True

            # 如果没有提供状态，根据指标判断
            if metrics:
                # 检查阈值
                exceeded, reasons = await self.check_thresholds(metrics)

                # 如果超过阈值，标记为失败
                if exceeded:
                    deployment.status = DeploymentStatus.FAILED
                    deployment.updated_at = datetime.utcnow()
                    self.db.commit()
                    logger.warning(
                        f"部署 {deployment_id} 指标超过阈值，状态更新为失败: {reasons}"
                    )
                    return True

                # 如果指标正常，检查是否应该标记为成功
                # 这里简化处理，实际应该根据部署策略和监控时长判断
                if deployment.status == DeploymentStatus.IN_PROGRESS:
                    # 如果部署进行中且指标正常，可以保持进行中状态
                    # 或者根据监控时长判断是否完成
                    pass

            return True

        except Exception as e:
            logger.error(f"更新部署状态失败: {e}", exc_info=True)
            return False

    async def determine_deployment_completion(
        self,
        deployment_id: int,
        metrics: Dict,
        monitoring_duration: int = 300,
    ) -> tuple[bool, Optional[str]]:
        """
        判断部署是否完成（成功或失败）

        Args:
            deployment_id: 部署记录 ID
            metrics: 部署指标
            monitoring_duration: 监控持续时间（秒）

        Returns:
            tuple[bool, Optional[str]]: (是否完成, 完成状态说明)
        """
        try:
            deployment = (
                self.db.query(DeploymentRecord)
                .filter(DeploymentRecord.id == deployment_id)
                .first()
            )
            if not deployment:
                return False, None

            # 检查部署开始时间
            deployment_start = deployment.created_at
            if isinstance(deployment_start, str):
                deployment_start = datetime.fromisoformat(deployment_start.replace("Z", "+00:00"))
            elapsed = (datetime.utcnow() - deployment_start).total_seconds()

            # 如果监控时长未到，继续监控
            if elapsed < monitoring_duration:
                return False, f"监控中，已监控 {elapsed:.0f} 秒，还需 {monitoring_duration - elapsed:.0f} 秒"

            # 检查阈值
            exceeded, reasons = await self.check_thresholds(metrics)

            if exceeded:
                return True, f"部署失败: {', '.join(reasons)}"
            else:
                return True, "部署成功，所有指标正常"

        except Exception as e:
            logger.error(f"判断部署完成状态失败: {e}", exc_info=True)
            return False, None

    async def monitor_deployment(
        self,
        deployment_id: int,
        container_names: Optional[List[str]] = None,
        health_check_urls: Optional[List[str]] = None,
        thresholds: Optional[Dict] = None,
        monitoring_duration: int = 300,
        check_interval: int = 10,
        log_callback: Optional[Callable] = None,
    ):
        """
        监控部署（长时间运行的任务）

        Args:
            deployment_id: 部署记录 ID
            container_names: 容器名称列表
            health_check_urls: 健康检查 URL 列表
            thresholds: 阈值配置
            monitoring_duration: 监控持续时间（秒）
            check_interval: 检查间隔（秒）
            log_callback: 日志回调函数
        """
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(seconds=monitoring_duration)

            if log_callback:
                log_callback(
                    f"开始监控部署 {deployment_id}，监控时长: {monitoring_duration}秒"
                )

            while datetime.utcnow() < end_time:
                # 收集指标
                metrics = await self.collect_metrics(
                    deployment_id, container_names, health_check_urls
                )

                if log_callback:
                    log_callback(f"收集指标: {metrics}")

                # 检查阈值
                exceeded, reasons = await self.check_thresholds(metrics, thresholds)
                if exceeded:
                    if log_callback:
                        log_callback(f"指标超过阈值: {reasons}")
                    # 更新状态为失败
                    await self.update_deployment_status(
                        deployment_id, metrics, DeploymentStatus.FAILED
                    )
                    break

                # 更新部署状态
                await self.update_deployment_status(deployment_id, metrics)

                # 判断是否完成
                completed, completion_reason = await self.determine_deployment_completion(
                    deployment_id, metrics, monitoring_duration
                )
                if completed:
                    if log_callback:
                        log_callback(f"部署完成: {completion_reason}")
                    break

                await asyncio.sleep(check_interval)

            if log_callback:
                log_callback(f"监控结束: 部署 {deployment_id}")

        except Exception as e:
            logger.error(f"监控部署失败: {e}", exc_info=True)
            if log_callback:
                log_callback(f"监控失败: {str(e)}")

