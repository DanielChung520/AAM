"""
@purpose: RabbitMQ 連接配置管理，封裝連接建立、隊列聲明和連接重試機制
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import logging
from typing import Optional

import aio_pika
from aio_pika import Connection, Channel, Queue
from aio_pika.abc import AbstractConnection, AbstractChannel

from src.config.settings import RabbitMQSettings

# 配置日志
logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """RabbitMQ 連接管理類"""

    def __init__(self, settings: RabbitMQSettings):
        """
        初始化 RabbitMQ 連接

        Args:
            settings: RabbitMQ 配置設置
        """
        self.settings = settings
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self._is_connected = False
        self._max_retries = 5
        self._retry_delay = 1.0  # 初始重試延遲（秒）

    async def connect(self) -> None:
        """
        建立 RabbitMQ 連接，實現重試機制（指數退避）

        Raises:
            ConnectionError: 連接失敗超過最大重試次數
        """
        retry_count = 0
        last_exception = None

        while retry_count < self._max_retries:
            try:
                logger.info(
                    f"嘗試連接 RabbitMQ (嘗試 {retry_count + 1}/{self._max_retries}) - "
                    f"host={self.settings.rabbitmq_host}, port={self.settings.rabbitmq_port}"
                )

                # 建立連接
                self.connection = await aio_pika.connect_robust(
                    self.settings.rabbitmq_url,
                    client_properties={
                        "connection_name": "aam-service-consumer",
                    },
                )

                # 創建通道
                self.channel = await self.connection.channel()
                self._is_connected = True

                logger.info(
                    f"成功連接到 RabbitMQ - "
                    f"host={self.settings.rabbitmq_host}, port={self.settings.rabbitmq_port}"
                )
                return

            except Exception as e:
                last_exception = e
                retry_count += 1
                delay = self._retry_delay * (2 ** (retry_count - 1))  # 指數退避

                logger.warning(
                    f"連接 RabbitMQ 失敗 (嘗試 {retry_count}/{self._max_retries}) - "
                    f"error={str(e)}, next_retry_in={delay}秒",
                    exc_info=e,
                )

                if retry_count < self._max_retries:
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"連接 RabbitMQ 失敗，已達到最大重試次數 (max_retries={self._max_retries})",
                        exc_info=e,
                    )
                    raise ConnectionError(
                        f"無法連接到 RabbitMQ 服務器 "
                        f"({self.settings.rabbitmq_host}:{self.settings.rabbitmq_port})"
                    ) from e

    async def setup_queue(
        self, queue_name: Optional[str] = None, durable: bool = True
    ) -> Queue:
        """
        聲明並設置隊列

        Args:
            queue_name: 隊列名稱，如果為 None 則使用配置中的默認值
            durable: 是否持久化隊列

        Returns:
            聲明的隊列對象

        Raises:
            RuntimeError: 連接未建立
        """
        if not self._is_connected or self.channel is None:
            raise RuntimeError("RabbitMQ 連接未建立，請先調用 connect()")

        queue_name = queue_name or self.settings.rabbitmq_queue

        logger.info(
            f"聲明隊列 - queue_name={queue_name}, durable={durable}"
        )

        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            auto_delete=False,  # 非自動刪除
        )

        logger.info(
            f"隊列聲明成功 - queue_name={queue_name}, durable={durable}"
        )

        return queue

    async def setup_exchange(
        self, exchange_name: Optional[str] = None, exchange_type: str = "direct"
    ) -> aio_pika.Exchange:
        """
        聲明並設置交換機（可選）

        Args:
            exchange_name: 交換機名稱，如果為 None 則使用配置中的默認值
            exchange_type: 交換機類型（direct, topic, fanout, headers）

        Returns:
            聲明的交換機對象

        Raises:
            RuntimeError: 連接未建立
        """
        if not self._is_connected or self.channel is None:
            raise RuntimeError("RabbitMQ 連接未建立，請先調用 connect()")

        exchange_name = exchange_name or self.settings.rabbitmq_exchange

        logger.info(
            f"聲明交換機 - exchange_name={exchange_name}, exchange_type={exchange_type}"
        )

        exchange = await self.channel.declare_exchange(
            exchange_name,
            type=exchange_type,
            durable=True,
        )

        logger.info(
            f"交換機聲明成功 - exchange_name={exchange_name}, exchange_type={exchange_type}"
        )

        return exchange

    async def bind_queue_to_exchange(
        self, queue: Queue, exchange: aio_pika.Exchange, routing_key: str = ""
    ) -> None:
        """
        將隊列綁定到交換機

        Args:
            queue: 隊列對象
            exchange: 交換機對象
            routing_key: 路由鍵

        Raises:
            RuntimeError: 連接未建立
        """
        if not self._is_connected:
            raise RuntimeError("RabbitMQ 連接未建立，請先調用 connect()")

        await queue.bind(exchange, routing_key=routing_key)

        logger.info(
            f"隊列綁定到交換機成功 - "
            f"queue_name={queue.name}, exchange_name={exchange.name}, routing_key={routing_key}"
        )

    async def close(self) -> None:
        """
        優雅關閉連接

        關閉通道和連接，確保資源正確釋放
        """
        if self.channel and not self.channel.is_closed:
            try:
                await self.channel.close()
                logger.debug("RabbitMQ 通道已關閉")
            except Exception as e:
                logger.warning("關閉 RabbitMQ 通道時發生錯誤", exc_info=e)

        if self.connection and not self.connection.is_closed:
            try:
                await self.connection.close()
                logger.debug("RabbitMQ 連接已關閉")
            except Exception as e:
                logger.warning("關閉 RabbitMQ 連接時發生錯誤", exc_info=e)

        self._is_connected = False
        logger.info("RabbitMQ 連接已關閉")

    def is_connected(self) -> bool:
        """
        檢查連接狀態

        Returns:
            如果連接已建立且未關閉，返回 True
        """
        return (
            self._is_connected
            and self.connection is not None
            and not self.connection.is_closed
            and self.channel is not None
            and not self.channel.is_closed
        )

    async def health_check(self) -> bool:
        """
        執行連接健康檢查

        Returns:
            如果連接健康，返回 True

        Raises:
            RuntimeError: 連接未建立或已關閉
        """
        if not self.is_connected():
            raise RuntimeError("RabbitMQ 連接未建立或已關閉")

        try:
            # 嘗試發送一個簡單的 ping 消息來驗證連接
            # 這裡我們只是檢查連接和通道是否仍然打開
            if self.connection and self.channel:
                return True
            return False
        except Exception as e:
            logger.warning("RabbitMQ 健康檢查失敗", exc_info=e)
            return False

