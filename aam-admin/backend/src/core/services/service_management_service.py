"""
@purpose: 服务管理基础类，提供服务状态查询和操作接口
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.services.docker_service import DockerService

logger = logging.getLogger(__name__)


class ServiceManagementBase(ABC):
    """服务管理抽象基类"""

    def __init__(self, docker_service: DockerService, service_name: str):
        """
        初始化服务管理

        Args:
            docker_service: Docker 服务实例
            service_name: 服务名称（容器名称）
        """
        self.docker_service = docker_service
        self.service_name = service_name

    @abstractmethod
    def get_service_status(self) -> Dict:
        """
        获取服务状态

        Returns:
            Dict: 服务状态信息
        """
        pass

    def start_service(self) -> bool:
        """
        启动服务

        Returns:
            bool: 是否成功启动
        """
        return self.docker_service.start_container(self.service_name)

    def stop_service(self) -> bool:
        """
        停止服务

        Returns:
            bool: 是否成功停止
        """
        return self.docker_service.stop_container(self.service_name)

    def restart_service(self) -> bool:
        """
        重启服务

        Returns:
            bool: 是否成功重启
        """
        return self.docker_service.restart_container(self.service_name)

    def get_service_logs(self, tail: int = 100) -> str:
        """
        获取服务日志

        Args:
            tail: 返回最后 N 行

        Returns:
            str: 日志内容
        """
        return self.docker_service.get_container_logs(self.service_name, tail=tail)


class AAMServiceManager(ServiceManagementBase):
    """AAM 服务管理器"""

    def get_service_status(self) -> Dict:
        """获取 AAM 服务状态"""
        status = self.docker_service.get_container_status(self.service_name)
        if status:
            return {
                "service": "aam-service",
                "status": status.get("status", "unknown"),
                "uptime": status.get("uptime", 0),
                "cpu_usage": status.get("cpu_usage", 0),
                "memory_usage": status.get("memory_usage", {}),
            }
        return {"service": "aam-service", "status": "not_found"}


class ServiceManagerFactory:
    """服务管理器工厂"""

    @staticmethod
    def create_manager(service_type: str, docker_service: DockerService) -> ServiceManagementBase:
        """
        创建服务管理器

        Args:
            service_type: 服务类型（aam-service, chromadb, postgres, rabbitmq）
            docker_service: Docker 服务实例

        Returns:
            ServiceManagementBase: 服务管理器实例
        """
        service_map = {
            "aam-service": ("aam-service-dev", AAMServiceManager),
            "chromadb": ("chromadb-dev", ServiceManagementBase),
            "postgres": ("postgres-dev", ServiceManagementBase),
            "rabbitmq": ("rabbitmq-dev", ServiceManagementBase),
        }

        container_name, manager_class = service_map.get(
            service_type, (service_type, ServiceManagementBase)
        )
        return manager_class(docker_service, container_name)


class ServiceManagementService:
    """服务管理服务类"""

    # 监控的服务列表
    MONITORED_SERVICES = ["aam-service", "chromadb", "postgres", "rabbitmq"]

    def __init__(self, docker_service: DockerService, db: Session):
        """
        初始化服务管理服务

        Args:
            docker_service: Docker 服务实例
            db: 数据库会话
        """
        self.docker_service = docker_service
        self.db = db

    def get_service_list(self) -> List[Dict]:
        """
        获取服务列表

        Returns:
            List[Dict]: 服务列表
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
                    {
                        "name": service_name,
                        "status": status,
                        "version": version,
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory_usage,
                        "uptime": uptime,
                    }
                )
            except Exception as e:
                logger.error(f"Error getting service status for {service_name}: {e}")
                services.append(
                    {
                        "name": service_name,
                        "status": "error",
                        "version": None,
                        "cpu_usage": 0.0,
                        "memory_usage": 0.0,
                        "uptime": None,
                    }
                )
        return services

    def get_service_detail(self, service_name: str) -> Optional[Dict]:
        """
        获取服务详情

        Args:
            service_name: 服务名称

        Returns:
            Optional[Dict]: 服务详情，如果服务不存在返回 None
        """
        if service_name not in self.MONITORED_SERVICES:
            return None

        try:
            manager = ServiceManagerFactory.create_manager(service_name, self.docker_service)
            container_status = self.docker_service.get_container_status(manager.service_name)

            if not container_status:
                return {
                    "name": service_name,
                    "status": "stopped",
                    "version": None,
                    "container_id": None,
                    "image": None,
                    "ports": [],
                    "cpu_usage": 0.0,
                    "memory_usage": {"used": 0, "limit": 0, "percent": 0},
                    "uptime": None,
                    "created_at": None,
                    "updated_at": None,
                }

            # 获取版本信息
            version = None
            image = container_status.get("image", "")
            if ":" in image:
                version = image.split(":")[-1]

            # 获取内存使用情况
            memory_info = container_status.get("memory_usage", {})
            if not isinstance(memory_info, dict):
                memory_info = {"used": 0, "limit": 0, "percent": 0}

            return {
                "name": service_name,
                "status": container_status.get("status", "unknown"),
                "version": version,
                "container_id": container_status.get("id"),
                "image": image,
                "ports": container_status.get("ports", []),
                "cpu_usage": container_status.get("cpu_usage", 0.0),
                "memory_usage": memory_info,
                "uptime": container_status.get("uptime"),
                "created_at": datetime.utcnow(),  # 可以从容器属性获取
                "updated_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"Error getting service detail for {service_name}: {e}")
            return None

    def get_service_stats(self, service_name: str) -> Optional[Dict]:
        """
        获取服务资源统计

        Args:
            service_name: 服务名称

        Returns:
            Optional[Dict]: 服务资源统计，如果服务不存在返回 None
        """
        if service_name not in self.MONITORED_SERVICES:
            return None

        try:
            manager = ServiceManagerFactory.create_manager(service_name, self.docker_service)
            container_status = self.docker_service.get_container_status(manager.service_name)

            if not container_status:
                return None

            memory_info = container_status.get("memory_usage", {})
            if not isinstance(memory_info, dict):
                memory_info = {"used": 0, "limit": 0, "percent": 0}

            return {
                "service_name": service_name,
                "cpu_usage": container_status.get("cpu_usage", 0.0),
                "memory_usage": memory_info,
                "network_io": None,  # 可以从 Docker stats 获取
                "disk_io": None,  # 可以从 Docker stats 获取
                "timestamp": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"Error getting service stats for {service_name}: {e}")
            return None

    def get_service_health(self, service_name: str) -> Dict:
        """
        获取服务健康状态

        Args:
            service_name: 服务名称

        Returns:
            Dict: 服务健康状态
        """
        if service_name not in self.MONITORED_SERVICES:
            return {
                "service_name": service_name,
                "status": "unknown",
                "last_check": datetime.utcnow(),
                "details": {"error": "Service not monitored"},
            }

        try:
            manager = ServiceManagerFactory.create_manager(service_name, self.docker_service)
            container_status = self.docker_service.get_container_status(manager.service_name)

            if not container_status:
                return {
                    "service_name": service_name,
                    "status": "unhealthy",
                    "last_check": datetime.utcnow(),
                    "details": {"error": "Container not found"},
                }

            docker_status = container_status.get("status", "unknown")
            if docker_status == "running":
                health_status = "healthy"
            else:
                health_status = "unhealthy"

            return {
                "service_name": service_name,
                "status": health_status,
                "last_check": datetime.utcnow(),
                "details": {
                    "container_status": docker_status,
                    "cpu_usage": container_status.get("cpu_usage", 0.0),
                    "memory_usage": container_status.get("memory_usage", {}),
                },
            }
        except Exception as e:
            logger.error(f"Error getting service health for {service_name}: {e}")
            return {
                "service_name": service_name,
                "status": "unknown",
                "last_check": datetime.utcnow(),
                "details": {"error": str(e)},
            }

    def operate_service(
        self, service_name: str, operation: str, reason: Optional[str] = None
    ) -> Dict:
        """
        执行服务操作（启动/停止/重启）

        Args:
            service_name: 服务名称
            operation: 操作类型 (start/stop/restart)
            reason: 操作原因

        Returns:
            Dict: 操作结果
        """
        if service_name not in self.MONITORED_SERVICES:
            return {
                "success": False,
                "message": f"服务 {service_name} 不在监控列表中",
                "service_name": service_name,
                "operation": operation,
                "timestamp": datetime.utcnow(),
            }

        try:
            manager = ServiceManagerFactory.create_manager(service_name, self.docker_service)

            success = False
            message = ""

            if operation == "start":
                success = manager.start_service()
                message = f"服务 {service_name} 启动成功" if success else f"服务 {service_name} 启动失败"
            elif operation == "stop":
                success = manager.stop_service()
                message = f"服务 {service_name} 停止成功" if success else f"服务 {service_name} 停止失败"
            elif operation == "restart":
                success = manager.restart_service()
                message = f"服务 {service_name} 重启成功" if success else f"服务 {service_name} 重启失败"
            else:
                return {
                    "success": False,
                    "message": f"不支持的操作类型: {operation}",
                    "service_name": service_name,
                    "operation": operation,
                    "timestamp": datetime.utcnow(),
                }

            # 记录操作日志（可以保存到数据库）
            if reason:
                logger.info(f"Service {operation} operation: {service_name}, reason: {reason}")

            return {
                "success": success,
                "message": message,
                "service_name": service_name,
                "operation": operation,
                "timestamp": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"Error operating service {service_name}: {e}")
            return {
                "success": False,
                "message": f"操作失败: {str(e)}",
                "service_name": service_name,
                "operation": operation,
                "timestamp": datetime.utcnow(),
            }
