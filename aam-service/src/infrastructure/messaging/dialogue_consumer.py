"""
@purpose: 對話歸檔消息消費者，監聽 RabbitMQ 隊列並處理對話歸檔消息
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import json
import logging
from typing import Optional

import aio_pika
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractQueue

from src.core.interfaces.i_memory_service import IMemoryService
from src.infrastructure.messaging.rabbitmq_config import RabbitMQConnection
from src.models.domain.dialogue import DialogueArchiveMessage

# 配置日志
logger = logging.getLogger(__name__)


class DialogueArchiveConsumer:
    """對話歸檔消息消費者"""

    def __init__(
        self,
        memory_service: IMemoryService,
        rabbitmq_connection: RabbitMQConnection,
    ):
        """
        初始化對話歸檔消費者

        Args:
            memory_service: 記憶服務接口實現
            rabbitmq_connection: RabbitMQ 連接管理實例
        """
        self.memory_service = memory_service
        self.rabbitmq = rabbitmq_connection
        self.queue: Optional[AbstractQueue] = None
        self._is_consuming = False
        self._consumer_tag: Optional[str] = None  # consumer tag (字符串) 而不是 consumer 对象
        self._processing_tasks: set[asyncio.Task] = set()

    async def start_consuming(self) -> None:
        """
        開始消費消息

        建立連接，設置隊列，開始消費循環

        Raises:
            RuntimeError: 連接未建立或消費已啟動
        """
        if self._is_consuming:
            raise RuntimeError("消費者已經在運行中")

        if not self.rabbitmq.is_connected():
            await self.rabbitmq.connect()

        # 設置隊列
        self.queue = await self.rabbitmq.setup_queue(
            queue_name=self.rabbitmq.settings.rabbitmq_queue
        )

        # 開始消費消息
        self._is_consuming = True
        logger.info(
            f"開始消費對話歸檔消息 - queue_name={self.queue.name}"
        )

        # 註冊消息處理回調
        # queue.consume() 返回 consumer tag (字符串)
        consumer = await self.queue.consume(
            self._process_message, no_ack=False
        )
        # 保存 consumer tag 以便后续取消消费
        self._consumer_tag = consumer.tag if hasattr(consumer, 'tag') else str(consumer)

        logger.info(
            f"對話歸檔消費者已啟動 - queue_name={self.queue.name}, consumer_tag={self._consumer_tag}"
        )

    async def stop_consuming(self, timeout: float = 30.0) -> None:
        """
        停止消費消息（優雅關閉）

        Args:
            timeout: 等待正在處理的消息完成的超時時間（秒）

        Raises:
            RuntimeError: 消費者未運行
        """
        if not self._is_consuming:
            logger.warning("嘗試停止未運行的消費者")
            return

        logger.info("正在停止對話歸檔消費者...")

        # 停止接收新消息
        self._is_consuming = False

        # 取消消息消費
        if self._consumer_tag and self.queue:
            try:
                # 使用 queue.cancel(consumer_tag) 来取消消费
                await self.queue.cancel(self._consumer_tag)
                logger.debug(f"已取消消息消費 - consumer_tag={self._consumer_tag}")
                self._consumer_tag = None
            except Exception as e:
                logger.warning(
                    f"取消消息消費時發生錯誤 - consumer_tag={self._consumer_tag}",
                    exc_info=e
                )

        # 等待正在處理的消息完成
        if self._processing_tasks:
            logger.info(
                f"等待 {len(self._processing_tasks)} 個正在處理的消息完成...",
            )
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._processing_tasks, return_exceptions=True),
                    timeout=timeout,
                )
                logger.info("所有正在處理的消息已完成")
            except asyncio.TimeoutError:
                logger.warning(
                    f"等待消息處理超時（{timeout}秒），強制停止",
                )
                # 取消未完成的任務
                for task in self._processing_tasks:
                    if not task.done():
                        task.cancel()

        self._processing_tasks.clear()
        logger.info("對話歸檔消費者已停止")

    async def _process_message(self, message: IncomingMessage) -> None:
        """
        處理接收到的消息（私有方法）

        Args:
            message: 接收到的消息對象
        """
        # 創建處理任務，避免阻塞消息消費循環
        task = asyncio.create_task(self._handle_message(message))
        self._processing_tasks.add(task)
        task.add_done_callback(self._processing_tasks.discard)

    async def _handle_message(self, message: IncomingMessage) -> None:
        """
        實際處理消息的邏輯

        Args:
            message: 接收到的消息對象
        """
        user_id = None
        dialog_id = None
        turn = None

        try:
            # 解析消息體
            try:
                body_str = message.body.decode("utf-8")
                body_dict = json.loads(body_str)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                logger.error(
                    f"消息格式錯誤：無法解析 JSON - error={str(e)}",
                    exc_info=e,
                )
                await message.nack(requeue=False)  # 不重新入隊，避免無限重試
                return

            # 使用 Pydantic 驗證消息
            try:
                archive_message = DialogueArchiveMessage(**body_dict)
                user_id = archive_message.user_id
                dialog_id = archive_message.dialog_id
                turn = archive_message.turn
            except Exception as e:
                body_preview = body_str[:200] if len(body_str) > 200 else body_str
                logger.error(
                    f"消息驗證失敗：Pydantic 驗證錯誤 - error={str(e)}, body_preview={body_preview}",
                    exc_info=e,
                )
                await message.nack(requeue=False)  # 不重新入隊，避免無限重試
                return

            logger.info(
                f"開始處理對話歸檔消息 - user_id={user_id}, dialog_id={dialog_id}, turn={turn}"
            )

            # 調用記憶服務的 archive 方法
            await self.memory_service.archive(archive_message)

            # 處理成功，發送 ACK
            await message.ack()

            logger.info(
                f"對話歸檔消息處理成功 - user_id={user_id}, dialog_id={dialog_id}, turn={turn}"
            )

        except Exception as e:
            # 處理失敗，記錄錯誤並發送 NACK（不重新入隊）
            logger.error(
                f"處理對話歸檔消息時發生錯誤 - user_id={user_id}, dialog_id={dialog_id}, turn={turn}, error={str(e)}",
                exc_info=e,
            )

            try:
                await message.nack(requeue=False)  # 不重新入隊，避免無限重試
            except Exception as nack_error:
                logger.error(
                    f"發送 NACK 時發生錯誤 - error={str(nack_error)}",
                    exc_info=nack_error,
                )

    def is_consuming(self) -> bool:
        """
        檢查消費者是否正在運行

        Returns:
            如果消費者正在運行，返回 True
        """
        return self._is_consuming

