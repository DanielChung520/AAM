"""
@purpose: Docker 服务封装，提供容器状态查询和操作服务
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from typing import Dict, List, Optional

import docker
from docker.errors import DockerException, NotFound

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class DockerService:
    """Docker 服务类"""

    def __init__(self):
        """初始化 Docker 服务"""
        self.settings = get_settings()
        self.client = self._create_client()

    def _create_client(self) -> docker.DockerClient:
        """
        创建 Docker 客户端

        Returns:
            docker.DockerClient: Docker 客户端实例
        """
        try:
            if self.settings.docker.docker_base_url:
                client = docker.DockerClient(base_url=self.settings.docker.docker_base_url)
            else:
                client = docker.from_env()
            # 测试连接
            client.ping()
            logger.info("Docker client connected successfully")
            return client
        except DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise

    def get_container_status(self, container_name: str) -> Optional[Dict]:
        """
        获取容器状态

        Args:
            container_name: 容器名称

        Returns:
            Optional[Dict]: 容器状态信息，如果容器不存在返回 None
        """
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)

            return {
                "name": container.name,
                "id": container.id[:12],
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "ports": [
                    f"{p['HostIp']}:{p['HostPort']}->{p['PrivatePort']}/{p['Type']}"
                    for p in container.attrs.get("NetworkSettings", {}).get("Ports", {}).values()
                    if p
                ],
                "cpu_usage": self._calculate_cpu_percent(stats),
                "memory_usage": self._calculate_memory_usage(stats),
                "uptime": self._calculate_uptime(container.attrs),
            }
        except NotFound:
            logger.warning(f"Container not found: {container_name}")
            return None
        except DockerException as e:
            logger.error(f"Error getting container status: {e}")
            raise

    def list_containers(self, all: bool = False) -> List[Dict]:
        """
        列出所有容器

        Args:
            all: 是否包含已停止的容器

        Returns:
            List[Dict]: 容器列表
        """
        try:
            containers = self.client.containers.list(all=all)
            return [
                {
                    "name": c.name,
                    "id": c.id[:12],
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                }
                for c in containers
            ]
        except DockerException as e:
            logger.error(f"Error listing containers: {e}")
            raise

    def start_container(self, container_name: str) -> bool:
        """
        启动容器

        Args:
            container_name: 容器名称

        Returns:
            bool: 是否成功启动
        """
        try:
            container = self.client.containers.get(container_name)
            container.start()
            logger.info(f"Container started: {container_name}")
            return True
        except NotFound:
            logger.error(f"Container not found: {container_name}")
            return False
        except DockerException as e:
            logger.error(f"Error starting container: {e}")
            return False

    def stop_container(self, container_name: str) -> bool:
        """
        停止容器

        Args:
            container_name: 容器名称

        Returns:
            bool: 是否成功停止
        """
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            logger.info(f"Container stopped: {container_name}")
            return True
        except NotFound:
            logger.error(f"Container not found: {container_name}")
            return False
        except DockerException as e:
            logger.error(f"Error stopping container: {e}")
            return False

    def restart_container(self, container_name: str) -> bool:
        """
        重启容器

        Args:
            container_name: 容器名称

        Returns:
            bool: 是否成功重启
        """
        try:
            container = self.client.containers.get(container_name)
            container.restart()
            logger.info(f"Container restarted: {container_name}")
            return True
        except NotFound:
            logger.error(f"Container not found: {container_name}")
            return False
        except DockerException as e:
            logger.error(f"Error restarting container: {e}")
            return False

    def get_container_logs(self, container_name: str, tail: int = 100, follow: bool = False) -> str:
        """
        获取容器日志

        Args:
            container_name: 容器名称
            tail: 返回最后 N 行日志
            follow: 是否持续跟踪日志

        Returns:
            str: 日志内容
        """
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, follow=follow, stream=False)
            return logs.decode("utf-8") if isinstance(logs, bytes) else logs
        except NotFound:
            logger.error(f"Container not found: {container_name}")
            return ""
        except DockerException as e:
            logger.error(f"Error getting container logs: {e}")
            return ""

    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """计算 CPU 使用率"""
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats.get(
                "precpu_stats", {}
            ).get("cpu_usage", {}).get("total_usage", 0)
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats.get(
                "precpu_stats", {}
            ).get("system_cpu_usage", 0)

            if system_delta > 0:
                return (cpu_delta / system_delta) * 100.0
            return 0.0
        except (KeyError, ZeroDivisionError):
            return 0.0

    def _calculate_memory_usage(self, stats: Dict) -> Dict[str, float]:
        """计算内存使用情况"""
        try:
            memory_stats = stats.get("memory_stats", {})
            usage = memory_stats.get("usage", 0)
            limit = memory_stats.get("limit", 1)
            return {
                "used": usage,
                "limit": limit,
                "percent": (usage / limit) * 100.0 if limit > 0 else 0.0,
            }
        except (KeyError, ZeroDivisionError):
            return {"used": 0, "limit": 0, "percent": 0.0}

    def _calculate_uptime(self, attrs: Dict) -> int:
        """计算运行时间（秒）"""
        try:
            started_at = attrs.get("State", {}).get("StartedAt", "")
            if started_at:
                from datetime import datetime

                started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                now = datetime.utcnow().replace(tzinfo=started.tzinfo)
                return int((now - started).total_seconds())
            return 0
        except Exception:
            return 0
