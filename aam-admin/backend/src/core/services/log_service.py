"""
@purpose: 日志服务，提供容器日志流和过滤功能
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import csv
import io
import json
import logging
import re
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from src.core.services.docker_service import DockerService

logger = logging.getLogger(__name__)


class LogService:
    """日志服务类"""

    def __init__(self, docker_service: DockerService):
        """
        初始化日志服务

        Args:
            docker_service: Docker 服务实例
        """
        self.docker_service = docker_service

    async def stream_logs(
        self,
        container_name: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        filter_level: Optional[str] = None,
        filter_text: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式获取容器日志

        Args:
            container_name: 容器名称
            since: 开始时间（ISO 格式）
            until: 结束时间（ISO 格式）
            filter_level: 日志级别过滤（INFO, WARNING, ERROR 等）
            filter_text: 文本过滤

        Yields:
            str: 日志行
        """
        try:
            container = self.docker_service.client.containers.get(container_name)
            logs = container.logs(
                follow=True,
                stream=True,
                since=since,
                until=until,
                tail=0,
            )

            for log_line in logs:
                log_text = log_line.decode("utf-8").strip()
                if not log_text:
                    continue

                # 应用过滤
                if filter_level and not self._match_level(log_text, filter_level):
                    continue

                if filter_text and filter_text.lower() not in log_text.lower():
                    continue

                yield log_text

        except Exception as e:
            logger.error(f"Error streaming logs: {e}")
            yield f"Error: {str(e)}"

    def get_logs(
        self,
        container_name: str,
        tail: int = 100,
        since: Optional[str] = None,
        until: Optional[str] = None,
        filter_level: Optional[str] = None,
        filter_text: Optional[str] = None,
    ) -> list[str]:
        """
        获取容器日志（非流式）

        Args:
            container_name: 容器名称
            tail: 返回最后 N 行
            since: 开始时间
            until: 结束时间
            filter_level: 日志级别过滤
            filter_text: 文本过滤

        Returns:
            list[str]: 日志行列表
        """
        logs = self.docker_service.get_container_logs(container_name, tail=tail)
        log_lines = logs.split("\n")

        # 应用过滤
        filtered_logs = []
        for line in log_lines:
            if filter_level and not self._match_level(line, filter_level):
                continue
            if filter_text and filter_text.lower() not in line.lower():
                continue
            filtered_logs.append(line)

        return filtered_logs

    def _match_level(self, log_line: str, level: str) -> bool:
        """
        检查日志行是否匹配指定级别

        Args:
            log_line: 日志行
            level: 日志级别

        Returns:
            bool: 是否匹配
        """
        level_patterns = {
            "ERROR": r"(?i)\b(error|exception|failed|failure)\b",
            "WARNING": r"(?i)\b(warning|warn|caution)\b",
            "INFO": r"(?i)\b(info|information)\b",
            "DEBUG": r"(?i)\b(debug|trace)\b",
        }

        pattern = level_patterns.get(level.upper())
        if pattern:
            return bool(re.search(pattern, log_line))
        return True

    def _parse_log_line(self, log_line: str, service_name: str) -> Dict:
        """
        解析日志行，提取时间戳、级别等信息

        Args:
            log_line: 日志行
            service_name: 服务名称

        Returns:
            Dict: 解析后的日志条目
        """
        # 尝试解析时间戳（多种格式）
        timestamp = datetime.utcnow()
        level = "INFO"
        message = log_line

        # 尝试匹配常见的时间戳格式
        timestamp_patterns = [
            r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)",  # ISO 格式
            r"(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})",  # 日期/时间格式
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # 尝试解析时间戳
                    if "T" in timestamp_str or "Z" in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    else:
                        timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
                    message = log_line[match.end():].strip()
                    break
                except Exception:
                    pass

        # 检测日志级别
        level_patterns = {
            "ERROR": r"(?i)\b(error|exception|failed|failure|fatal)\b",
            "WARNING": r"(?i)\b(warning|warn|caution)\b",
            "DEBUG": r"(?i)\b(debug|trace)\b",
            "INFO": r"(?i)\b(info|information)\b",
        }

        for log_level, pattern in level_patterns.items():
            if re.search(pattern, log_line):
                level = log_level
                break

        return {
            "timestamp": timestamp,
            "level": level,
            "service": service_name,
            "message": message,
            "raw": log_line,
        }

    def search_logs(
        self,
        service: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Tuple[List[Dict], int]:
        """
        搜索日志

        Args:
            service: 服务名称
            level: 日志级别
            start_time: 开始时间
            end_time: 结束时间
            keyword: 关键词
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[List[Dict], int]: (日志条目列表, 总记录数)
        """
        # 监控的服务列表
        monitored_services = ["aam-service-dev", "chromadb-dev", "postgres-dev", "rabbitmq-dev"]
        service_map = {
            "aam-service": "aam-service-dev",
            "chromadb": "chromadb-dev",
            "postgres": "postgres-dev",
            "rabbitmq": "rabbitmq-dev",
        }

        all_logs = []

        # 确定要查询的服务
        services_to_query = []
        if service:
            container_name = service_map.get(service, service)
            services_to_query = [container_name]
        else:
            services_to_query = monitored_services

        # 从每个服务获取日志
        for container_name in services_to_query:
            try:
                logs = self.get_logs(
                    container_name=container_name,
                    tail=1000,  # 获取更多日志用于搜索
                    filter_level=level,
                    filter_text=keyword,
                )

                service_name = service or container_name.replace("-dev", "")
                for log_line in logs:
                    log_entry = self._parse_log_line(log_line, service_name)

                    # 时间过滤
                    if start_time and log_entry["timestamp"] < start_time:
                        continue
                    if end_time and log_entry["timestamp"] > end_time:
                        continue

                    all_logs.append(log_entry)
            except Exception as e:
                logger.error(f"Error getting logs from {container_name}: {e}")

        # 按时间戳排序（最新的在前）
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        # 分页
        total = len(all_logs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_logs = all_logs[start:end]

        return paginated_logs, total

    def export_logs(
        self,
        service: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None,
        format: str = "json",
    ) -> bytes:
        """
        导出日志

        Args:
            service: 服务名称
            level: 日志级别
            start_time: 开始时间
            end_time: 结束时间
            keyword: 关键词
            format: 导出格式 (json/csv)

        Returns:
            bytes: 导出的日志数据
        """
        logs, _ = self.search_logs(
            service=service,
            level=level,
            start_time=start_time,
            end_time=end_time,
            keyword=keyword,
            page=1,
            page_size=10000,  # 导出时获取更多数据
        )

        if format.lower() == "csv":
            # CSV 格式
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=["timestamp", "level", "service", "message"],
                extrasaction="ignore",
            )
            writer.writeheader()
            for log in logs:
                writer.writerow(
                    {
                        "timestamp": log["timestamp"].isoformat(),
                        "level": log["level"],
                        "service": log["service"],
                        "message": log["message"],
                    }
                )
            return output.getvalue().encode("utf-8")
        else:
            # JSON 格式
            log_data = [
                {
                    "timestamp": log["timestamp"].isoformat(),
                    "level": log["level"],
                    "service": log["service"],
                    "message": log["message"],
                }
                for log in logs
            ]
            return json.dumps(log_data, indent=2, ensure_ascii=False).encode("utf-8")
