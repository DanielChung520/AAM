"""
@purpose: 负载均衡器服务，提供Nginx/Traefik配置更新和流量分配功能
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import asyncio
import logging
import os
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import yaml

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class LoadBalancerType(str, Enum):
    """负载均衡器类型枚举"""

    NGINX = "nginx"
    TRAEFIK = "traefik"


class LoadBalancerService:
    """负载均衡器服务类"""

    def __init__(self, lb_type: Optional[str] = None):
        """
        初始化负载均衡器服务

        Args:
            lb_type: 负载均衡器类型（nginx/traefik），如果为None则从环境变量读取
        """
        self.settings = get_settings()
        self.lb_type = LoadBalancerType(
            lb_type or os.getenv("LOAD_BALANCER_TYPE", "nginx").lower()
        )

        # Nginx 配置路径
        self.nginx_config_dir = Path(
            os.getenv("NGINX_CONFIG_DIR", "/etc/nginx/conf.d")
        )
        self.nginx_config_file = self.nginx_config_dir / "aam-upstream.conf"
        self.nginx_backup_dir = Path(
            os.getenv("NGINX_BACKUP_DIR", "/tmp/nginx-backups")
        )

        # Traefik 配置路径
        self.traefik_config_dir = Path(
            os.getenv("TRAEFIK_CONFIG_DIR", "/etc/traefik")
        )
        self.traefik_config_file = self.traefik_config_dir / "aam-upstream.yml"
        self.traefik_backup_dir = Path(
            os.getenv("TRAEFIK_BACKUP_DIR", "/tmp/traefik-backups")
        )

        # 创建备份目录
        self.nginx_backup_dir.mkdir(parents=True, exist_ok=True)
        self.traefik_backup_dir.mkdir(parents=True, exist_ok=True)

    async def add_upstream_server(
        self,
        server_name: str,
        server_address: str,
        weight: int = 100,
        backup: bool = False,
    ) -> bool:
        """
        添加上游服务器

        Args:
            server_name: 服务器名称（用于标识）
            server_address: 服务器地址（host:port）
            weight: 权重（用于流量分配，默认100）
            backup: 是否为备份服务器

        Returns:
            bool: 是否添加成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_add_upstream_server(
                    server_name, server_address, weight, backup
                )
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_add_upstream_server(
                    server_name, server_address, weight, backup
                )
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"添加上游服务器失败: {e}", exc_info=True)
            return False

    async def remove_upstream_server(
        self, server_name: str, server_address: Optional[str] = None
    ) -> bool:
        """
        移除上游服务器

        Args:
            server_name: 服务器名称
            server_address: 服务器地址（可选，如果提供则精确匹配）

        Returns:
            bool: 是否移除成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_remove_upstream_server(
                    server_name, server_address
                )
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_remove_upstream_server(
                    server_name, server_address
                )
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"移除上游服务器失败: {e}", exc_info=True)
            return False

    async def update_traffic_distribution(
        self, servers: List[Dict[str, any]]
    ) -> bool:
        """
        更新流量分配（用于金丝雀部署）

        Args:
            servers: 服务器列表，每个服务器包含：
                - name: 服务器名称
                - address: 服务器地址
                - weight: 权重（0-100，表示流量百分比）
                - backup: 是否为备份服务器

        Returns:
            bool: 是否更新成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_update_traffic_distribution(servers)
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._nginx_update_traffic_distribution(servers)
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"更新流量分配失败: {e}", exc_info=True)
            return False

    async def switch_backend(
        self, primary_servers: List[str], backup_servers: Optional[List[str]] = None
    ) -> bool:
        """
        切换后端（用于蓝绿部署）

        Args:
            primary_servers: 主服务器地址列表
            backup_servers: 备份服务器地址列表（可选）

        Returns:
            bool: 是否切换成功
        """
        try:
            # 备份当前配置
            await self.backup_config()

            # 更新配置为主服务器
            servers = [
                {"name": f"server-{i}", "address": addr, "weight": 100, "backup": False}
                for i, addr in enumerate(primary_servers)
            ]
            if backup_servers:
                servers.extend(
                    [
                        {
                            "name": f"backup-{i}",
                            "address": addr,
                            "weight": 0,
                            "backup": True,
                        }
                        for i, addr in enumerate(backup_servers)
                    ]
                )

            success = await self.update_traffic_distribution(servers)
            if success:
                await self.reload_config()
            return success
        except Exception as e:
            logger.error(f"切换后端失败: {e}", exc_info=True)
            return False

    async def reload_config(self) -> bool:
        """
        重载负载均衡器配置

        Returns:
            bool: 是否重载成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_reload()
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_reload()
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"重载配置失败: {e}", exc_info=True)
            return False

    async def backup_config(self) -> bool:
        """
        备份当前配置

        Returns:
            bool: 是否备份成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_backup()
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_backup()
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"备份配置失败: {e}", exc_info=True)
            return False

    async def restore_config(self, backup_name: Optional[str] = None) -> bool:
        """
        恢复配置

        Args:
            backup_name: 备份文件名（可选，如果不提供则使用最新备份）

        Returns:
            bool: 是否恢复成功
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_restore(backup_name)
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_restore(backup_name)
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return False
        except Exception as e:
            logger.error(f"恢复配置失败: {e}", exc_info=True)
            return False

    async def get_upstream_servers(self) -> List[Dict[str, any]]:
        """
        获取当前上游服务器列表

        Returns:
            List[Dict]: 服务器列表
        """
        try:
            if self.lb_type == LoadBalancerType.NGINX:
                return await self._nginx_get_upstream_servers()
            elif self.lb_type == LoadBalancerType.TRAEFIK:
                return await self._traefik_get_upstream_servers()
            else:
                logger.error(f"不支持的负载均衡器类型: {self.lb_type}")
                return []
        except Exception as e:
            logger.error(f"获取上游服务器列表失败: {e}", exc_info=True)
            return []

    # ========== Nginx 相关方法 ==========

    async def _nginx_add_upstream_server(
        self, server_name: str, server_address: str, weight: int, backup: bool
    ) -> bool:
        """Nginx 添加上游服务器"""
        try:
            # 读取当前配置
            upstream_config = await self._nginx_read_config()

            # 添加上游服务器
            server_line = f"    server {server_address}"
            if weight != 100:
                server_line += f" weight={weight}"
            if backup:
                server_line += " backup"

            # 检查是否已存在
            if server_address in str(upstream_config):
                logger.warning(f"服务器 {server_address} 已存在于配置中")
                return True

            # 添加到配置
            upstream_block = upstream_config.get("upstream", {})
            if "servers" not in upstream_block:
                upstream_block["servers"] = []
            upstream_block["servers"].append(
                {
                    "address": server_address,
                    "weight": weight,
                    "backup": backup,
                }
            )

            # 写入配置
            await self._nginx_write_config(upstream_config)
            return True
        except Exception as e:
            logger.error(f"Nginx 添加上游服务器失败: {e}", exc_info=True)
            return False

    async def _nginx_remove_upstream_server(
        self, server_name: str, server_address: Optional[str]
    ) -> bool:
        """Nginx 移除上游服务器"""
        try:
            upstream_config = await self._nginx_read_config()
            upstream_block = upstream_config.get("upstream", {})
            servers = upstream_block.get("servers", [])

            # 移除服务器
            if server_address:
                servers = [
                    s
                    for s in servers
                    if s.get("address") != server_address
                ]
            else:
                # 根据名称移除（如果名称匹配地址）
                servers = [
                    s
                    for s in servers
                    if not (server_name in s.get("address", ""))
                ]

            upstream_block["servers"] = servers
            await self._nginx_write_config(upstream_config)
            return True
        except Exception as e:
            logger.error(f"Nginx 移除上游服务器失败: {e}", exc_info=True)
            return False

    async def _nginx_update_traffic_distribution(
        self, servers: List[Dict[str, any]]
    ) -> bool:
        """Nginx 更新流量分配"""
        try:
            upstream_config = {
                "upstream": {
                    "name": "aam_backend",
                    "servers": [
                        {
                            "address": s["address"],
                            "weight": s.get("weight", 100),
                            "backup": s.get("backup", False),
                        }
                        for s in servers
                    ],
                }
            }
            await self._nginx_write_config(upstream_config)
            return True
        except Exception as e:
            logger.error(f"Nginx 更新流量分配失败: {e}", exc_info=True)
            return False

    async def _nginx_read_config(self) -> Dict:
        """读取 Nginx 配置"""
        try:
            if not self.nginx_config_file.exists():
                return {"upstream": {"name": "aam_backend", "servers": []}}

            # 读取配置文件（假设是 JSON 格式的元数据）
            # 实际 Nginx 配置是文本格式，这里简化处理
            with open(self.nginx_config_file, "r") as f:
                content = f.read()

            # 解析 Nginx upstream 配置
            # 这里简化处理，实际应该解析 Nginx 配置语法
            config = {"upstream": {"name": "aam_backend", "servers": []}}
            for line in content.split("\n"):
                if "server" in line and not line.strip().startswith("#"):
                    # 解析 server 行
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        address = parts[1]
                        weight = 100
                        backup = False
                        for part in parts[2:]:
                            if "weight=" in part:
                                weight = int(part.split("=")[1])
                            elif part == "backup":
                                backup = True
                        config["upstream"]["servers"].append(
                            {"address": address, "weight": weight, "backup": backup}
                        )

            return config
        except Exception as e:
            logger.error(f"读取 Nginx 配置失败: {e}", exc_info=True)
            return {"upstream": {"name": "aam_backend", "servers": []}}

    async def _nginx_write_config(self, config: Dict) -> bool:
        """写入 Nginx 配置"""
        try:
            upstream_block = config.get("upstream", {})
            servers = upstream_block.get("servers", [])

            # 生成 Nginx upstream 配置
            config_lines = [f"upstream {upstream_block.get('name', 'aam_backend')} {{"]
            for server in servers:
                server_line = f"    server {server['address']}"
                if server.get("weight", 100) != 100:
                    server_line += f" weight={server['weight']}"
                if server.get("backup", False):
                    server_line += " backup"
                config_lines.append(server_line + ";")
            config_lines.append("}")

            # 写入文件
            self.nginx_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.nginx_config_file, "w") as f:
                f.write("\n".join(config_lines))

            logger.info(f"Nginx 配置已更新: {self.nginx_config_file}")
            return True
        except Exception as e:
            logger.error(f"写入 Nginx 配置失败: {e}", exc_info=True)
            return False

    async def _nginx_reload(self) -> bool:
        """重载 Nginx 配置"""
        try:
            # 测试配置
            result = subprocess.run(
                ["nginx", "-t"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                logger.error(f"Nginx 配置测试失败: {result.stderr}")
                return False

            # 重载配置
            result = subprocess.run(
                ["nginx", "-s", "reload"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info("Nginx 配置重载成功")
                return True
            else:
                logger.error(f"Nginx 配置重载失败: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.warning("Nginx 命令未找到，跳过重载（可能是开发环境）")
            return True  # 开发环境可能没有 Nginx
        except Exception as e:
            logger.error(f"Nginx 重载失败: {e}", exc_info=True)
            return False

    async def _nginx_backup(self) -> bool:
        """备份 Nginx 配置"""
        try:
            if not self.nginx_config_file.exists():
                return True

            import datetime

            backup_name = (
                f"nginx-backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.conf"
            )
            backup_path = self.nginx_backup_dir / backup_name
            shutil.copy2(self.nginx_config_file, backup_path)
            logger.info(f"Nginx 配置已备份: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份 Nginx 配置失败: {e}", exc_info=True)
            return False

    async def _nginx_restore(self, backup_name: Optional[str]) -> bool:
        """恢复 Nginx 配置"""
        try:
            if backup_name:
                backup_path = self.nginx_backup_dir / backup_name
            else:
                # 使用最新备份
                backups = sorted(self.nginx_backup_dir.glob("nginx-backup-*.conf"))
                if not backups:
                    logger.error("未找到备份文件")
                    return False
                backup_path = backups[-1]

            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            shutil.copy2(backup_path, self.nginx_config_file)
            logger.info(f"Nginx 配置已恢复: {backup_path}")
            await self._nginx_reload()
            return True
        except Exception as e:
            logger.error(f"恢复 Nginx 配置失败: {e}", exc_info=True)
            return False

    async def _nginx_get_upstream_servers(self) -> List[Dict[str, any]]:
        """获取 Nginx 上游服务器列表"""
        config = await self._nginx_read_config()
        return config.get("upstream", {}).get("servers", [])

    # ========== Traefik 相关方法 ==========

    async def _traefik_add_upstream_server(
        self, server_name: str, server_address: str, weight: int, backup: bool
    ) -> bool:
        """Traefik 添加上游服务器"""
        try:
            config = await self._traefik_read_config()
            if "http" not in config:
                config["http"] = {}
            if "services" not in config["http"]:
                config["http"]["services"] = {}
            if "aam_backend" not in config["http"]["services"]:
                config["http"]["services"]["aam_backend"] = {"loadBalancer": {}}

            service_config = config["http"]["services"]["aam_backend"]
            if "servers" not in service_config["loadBalancer"]:
                service_config["loadBalancer"]["servers"] = []

            # 检查是否已存在
            existing = [
                s
                for s in service_config["loadBalancer"]["servers"]
                if s.get("url") == f"http://{server_address}"
            ]
            if existing:
                logger.warning(f"服务器 {server_address} 已存在于配置中")
                return True

            # 添加服务器
            server_config = {"url": f"http://{server_address}"}
            if weight != 100:
                server_config["weight"] = weight
            service_config["loadBalancer"]["servers"].append(server_config)

            await self._traefik_write_config(config)
            return True
        except Exception as e:
            logger.error(f"Traefik 添加上游服务器失败: {e}", exc_info=True)
            return False

    async def _traefik_remove_upstream_server(
        self, server_name: str, server_address: Optional[str]
    ) -> bool:
        """Traefik 移除上游服务器"""
        try:
            config = await self._traefik_read_config()
            if "http" not in config or "services" not in config["http"]:
                return True

            service_config = config["http"]["services"].get("aam_backend", {})
            if "loadBalancer" not in service_config:
                return True

            servers = service_config["loadBalancer"].get("servers", [])
            if server_address:
                servers = [
                    s
                    for s in servers
                    if s.get("url") != f"http://{server_address}"
                ]
            else:
                servers = [
                    s
                    for s in servers
                    if not (server_name in s.get("url", ""))
                ]

            service_config["loadBalancer"]["servers"] = servers
            await self._traefik_write_config(config)
            return True
        except Exception as e:
            logger.error(f"Traefik 移除上游服务器失败: {e}", exc_info=True)
            return False

    async def _traefik_update_traffic_distribution(
        self, servers: List[Dict[str, any]]
    ) -> bool:
        """Traefik 更新流量分配"""
        try:
            config = {
                "http": {
                    "services": {
                        "aam_backend": {
                            "loadBalancer": {
                                "servers": [
                                    {
                                        "url": f"http://{s['address']}",
                                        "weight": s.get("weight", 100),
                                    }
                                    for s in servers
                                    if not s.get("backup", False)
                                ]
                            }
                        }
                    }
                }
            }
            await self._traefik_write_config(config)
            return True
        except Exception as e:
            logger.error(f"Traefik 更新流量分配失败: {e}", exc_info=True)
            return False

    async def _traefik_read_config(self) -> Dict:
        """读取 Traefik 配置"""
        try:
            if not self.traefik_config_file.exists():
                return {"http": {"services": {}}}

            with open(self.traefik_config_file, "r") as f:
                config = yaml.safe_load(f) or {}

            return config
        except Exception as e:
            logger.error(f"读取 Traefik 配置失败: {e}", exc_info=True)
            return {"http": {"services": {}}}

    async def _traefik_write_config(self, config: Dict) -> bool:
        """写入 Traefik 配置"""
        try:
            self.traefik_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.traefik_config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

            logger.info(f"Traefik 配置已更新: {self.traefik_config_file}")
            return True
        except Exception as e:
            logger.error(f"写入 Traefik 配置失败: {e}", exc_info=True)
            return False

    async def _traefik_reload(self) -> bool:
        """重载 Traefik 配置"""
        try:
            # Traefik 会自动检测配置文件变化并重载
            # 如果需要手动触发，可以通过 API 或信号
            logger.info("Traefik 配置已更新（Traefik 会自动检测变化）")
            return True
        except Exception as e:
            logger.error(f"Traefik 重载失败: {e}", exc_info=True)
            return False

    async def _traefik_backup(self) -> bool:
        """备份 Traefik 配置"""
        try:
            if not self.traefik_config_file.exists():
                return True

            import datetime

            backup_name = (
                f"traefik-backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.yml"
            )
            backup_path = self.traefik_backup_dir / backup_name
            shutil.copy2(self.traefik_config_file, backup_path)
            logger.info(f"Traefik 配置已备份: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份 Traefik 配置失败: {e}", exc_info=True)
            return False

    async def _traefik_restore(self, backup_name: Optional[str]) -> bool:
        """恢复 Traefik 配置"""
        try:
            if backup_name:
                backup_path = self.traefik_backup_dir / backup_name
            else:
                backups = sorted(
                    self.traefik_backup_dir.glob("traefik-backup-*.yml")
                )
                if not backups:
                    logger.error("未找到备份文件")
                    return False
                backup_path = backups[-1]

            if not backup_path.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            shutil.copy2(backup_path, self.traefik_config_file)
            logger.info(f"Traefik 配置已恢复: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复 Traefik 配置失败: {e}", exc_info=True)
            return False

    async def _traefik_get_upstream_servers(self) -> List[Dict[str, any]]:
        """获取 Traefik 上游服务器列表"""
        config = await self._traefik_read_config()
        service_config = (
            config.get("http", {})
            .get("services", {})
            .get("aam_backend", {})
            .get("loadBalancer", {})
        )
        servers = service_config.get("servers", [])
        return [
            {
                "address": s["url"].replace("http://", ""),
                "weight": s.get("weight", 100),
                "backup": False,
            }
            for s in servers
        ]

