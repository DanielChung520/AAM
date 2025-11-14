"""
@purpose: 健康检查服务，提供服务健康检查功能
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Optional, Dict, List
import httpx

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckService:
    """健康检查服务类"""

    def __init__(self):
        """初始化健康检查服务"""
        self.settings = get_settings()
        self.default_timeout = 10
        self.default_retries = 3
        self.default_retry_interval = 5  # 秒

    async def check_health(
        self,
        url: str,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        retry_interval: Optional[int] = None,
    ) -> HealthStatus:
        """
        检查服务健康状态

        Args:
            url: 健康检查 URL（通常是 /health 端点）
            timeout: 超时时间（秒）
            retries: 重试次数
            retry_interval: 重试间隔（秒）

        Returns:
            HealthStatus: 健康状态
        """
        timeout = timeout or self.default_timeout
        retries = retries or self.default_retries
        retry_interval = retry_interval or self.default_retry_interval

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        logger.debug(f"健康检查成功: {url} (尝试 {attempt + 1}/{retries})")
                        return HealthStatus.HEALTHY
                    else:
                        logger.warning(
                            f"健康检查返回非200状态码: {url}, status={response.status_code} (尝试 {attempt + 1}/{retries})"
                        )
            except httpx.TimeoutException:
                logger.warning(
                    f"健康检查超时: {url} (尝试 {attempt + 1}/{retries})"
                )
            except Exception as e:
                logger.warning(
                    f"健康检查失败: {url}, error={e} (尝试 {attempt + 1}/{retries})"
                )

            # 如果不是最后一次尝试，等待后重试
            if attempt < retries - 1:
                await asyncio.sleep(retry_interval)

        logger.error(f"健康检查最终失败: {url} (已重试 {retries} 次)")
        return HealthStatus.UNHEALTHY

    async def wait_for_healthy(
        self,
        url: str,
        timeout: int = 300,
        check_interval: int = 5,
    ) -> bool:
        """
        等待服务变为健康状态

        Args:
            url: 健康检查 URL
            timeout: 总超时时间（秒）
            check_interval: 检查间隔（秒）

        Returns:
            bool: 是否在超时前变为健康
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = await self.check_health(url, timeout=check_interval, retries=1)
            if status == HealthStatus.HEALTHY:
                logger.info(f"服务已变为健康状态: {url}")
                return True
            await asyncio.sleep(check_interval)

        logger.error(f"等待服务健康超时: {url} (超时时间: {timeout}秒)")
        return False

    async def check_multiple_endpoints(
        self, endpoints: List[str], timeout: Optional[int] = None
    ) -> Dict[str, HealthStatus]:
        """
        检查多个端点的健康状态

        Args:
            endpoints: 端点 URL 列表
            timeout: 超时时间（秒）

        Returns:
            Dict[str, HealthStatus]: 端点健康状态字典
        """
        results = {}
        for endpoint in endpoints:
            results[endpoint] = await self.check_health(endpoint, timeout=timeout)
        return results

    def get_aam_service_health_url(self) -> str:
        """
        获取 AAM 服务的健康检查 URL

        Returns:
            str: 健康检查 URL
        """
        aam_url = self.settings.aam_service_url or "http://aam-service:8000"
        return f"{aam_url}/health"

