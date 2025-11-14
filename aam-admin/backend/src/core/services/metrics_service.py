"""
@purpose: 系统指标服务，收集和统计系统资源使用情况
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.core.services.docker_service import DockerService
from src.core.services.service_management_service import ServiceManagerFactory
from src.models.database import AuditLog, AuditAction
from src.models.schemas.dashboard import (
    DashboardStats,
    ServiceStatus,
    SystemMetrics,
    RecentOperation,
)

logger = logging.getLogger(__name__)


class MetricsService:
    """指标服务类"""

    # 定义需要监控的服务列表
    MONITORED_SERVICES = [
        "aam-service",
        "chromadb",
        "postgres",
        "rabbitmq",
    ]

    def __init__(self, docker_service: DockerService, db: Session):
        """
        初始化指标服务

        Args:
            docker_service: Docker 服务实例
            db: 数据库会话
        """
        self.docker_service = docker_service
        self.db = db

    def get_system_metrics(self) -> SystemMetrics:
        """
        获取系统资源指标

        Returns:
            SystemMetrics: 系统资源指标
        """
        try:
            # CPU 使用率
            cpu_usage = psutil.cpu_percent(interval=1)

            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_total = memory.total / (1024 * 1024)  # 转换为 MB
            memory_used = memory.used / (1024 * 1024)  # 转换为 MB

            # 磁盘使用情况
            disk = psutil.disk_usage("/")
            disk_usage = disk.percent
            disk_total = disk.total / (1024 * 1024 * 1024)  # 转换为 GB
            disk_used = disk.used / (1024 * 1024 * 1024)  # 转换为 GB

            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_total=memory_total,
                memory_used=memory_used,
                disk_usage=disk_usage,
                disk_total=disk_total,
                disk_used=disk_used,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            # 返回默认值
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                memory_total=0.0,
                memory_used=0.0,
                disk_usage=0.0,
                disk_total=0.0,
                disk_used=0.0,
                timestamp=datetime.utcnow(),
            )

    def get_service_statuses(self) -> List[ServiceStatus]:
        """
        获取所有服务的状态

        Returns:
            List[ServiceStatus]: 服务状态列表
        """
        services = []
        for service_name in self.MONITORED_SERVICES:
            try:
                manager = ServiceManagerFactory.create_manager(service_name, self.docker_service)
                status_info = manager.get_service_status()

                # 获取容器状态以获取更多信息
                container_status = self.docker_service.get_container_status(
                    manager.service_name
                )

                # 确定服务状态
                if container_status:
                    docker_status = container_status.get("status", "unknown")
                    if docker_status == "running":
                        status = "running"
                    elif docker_status == "exited":
                        status = "stopped"
                    else:
                        status = "error"
                else:
                    status = "stopped"

                # 获取版本信息（从容器镜像标签）
                version = None
                if container_status:
                    image = container_status.get("image", "")
                    if ":" in image:
                        version = image.split(":")[-1]

                # 获取资源使用情况
                cpu_usage = 0.0
                memory_usage = 0.0
                uptime = None

                if container_status:
                    cpu_usage = container_status.get("cpu_usage", 0.0)
                    memory_info = container_status.get("memory_usage", {})
                    if isinstance(memory_info, dict):
                        memory_usage = memory_info.get("percent", 0.0)
                    uptime = container_status.get("uptime")

                services.append(
                    ServiceStatus(
                        name=service_name,
                        status=status,
                        version=version,
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        uptime=uptime,
                    )
                )
            except Exception as e:
                logger.error(f"Error getting status for service {service_name}: {e}")
                # 添加错误状态的服务
                services.append(
                    ServiceStatus(
                        name=service_name,
                        status="error",
                        version=None,
                        cpu_usage=0.0,
                        memory_usage=0.0,
                        uptime=None,
                    )
                )

        return services

    def get_dashboard_stats(self) -> DashboardStats:
        """
        获取仪表盘统计概览

        Returns:
            DashboardStats: 统计概览
        """
        # 获取服务状态
        services = self.get_service_statuses()
        total_services = len(services)
        running_services = sum(1 for s in services if s.status == "running")

        # TODO: 从配置文件或数据库获取 LLM Provider 信息
        # 目前返回默认值
        total_providers = 0
        active_providers = 0

        # TODO: 从部署记录获取当前版本
        # 目前返回默认值
        current_version = None

        # 计算系统负载（使用 CPU 使用率）
        metrics = self.get_system_metrics()
        system_load = metrics.cpu_usage

        return DashboardStats(
            total_services=total_services,
            running_services=running_services,
            total_providers=total_providers,
            active_providers=active_providers,
            current_version=current_version,
            system_load=system_load,
        )

    def get_recent_operations(
        self, limit: int = 10, hours: int = 24
    ) -> List[RecentOperation]:
        """
        获取最近操作记录

        Args:
            limit: 返回记录数限制
            hours: 查询时间范围（小时）

        Returns:
            List[RecentOperation]: 最近操作记录列表
        """
        try:
            # 计算时间范围
            since_time = datetime.utcnow() - timedelta(hours=hours)

            # 查询审计日志
            audit_logs = (
                self.db.query(AuditLog)
                .filter(AuditLog.created_at >= since_time)
                .order_by(desc(AuditLog.created_at))
                .limit(limit)
                .all()
            )

            operations = []
            for log in audit_logs:
                # 获取操作者用户名
                operator = "系统"
                if log.user_id:
                    # 延迟加载用户关系
                    if hasattr(log, "user") and log.user:
                        operator = log.user.username
                    else:
                        # 如果关系未加载，查询用户
                        from src.models.database import User
                        user = self.db.query(User).filter(User.id == log.user_id).first()
                        if user:
                            operator = user.username

                operations.append(
                    RecentOperation(
                        id=log.id,
                        action=log.action.value,
                        resource_type=log.resource_type,
                        resource_id=log.resource_id,
                        description=log.description,
                        operator=operator,
                        status=log.status or "success",
                        created_at=log.created_at,
                    )
                )

            return operations
        except Exception as e:
            logger.error(f"Error getting recent operations: {e}")
            return []

