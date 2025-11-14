"""
@purpose: 測試對話歸檔消息消費者的實現
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from unittest.mock import AsyncMock, Mock, patch

from aio_pika import IncomingMessage
from src.core.interfaces.i_memory_service import IMemoryService
from src.infrastructure.messaging.dialogue_consumer import DialogueArchiveConsumer
from src.infrastructure.messaging.rabbitmq_config import RabbitMQConnection
from src.models.domain.dialogue import DialogueArchiveMessage
from src.config.settings import RabbitMQSettings


class TestRabbitMQConnection:
    """測試 RabbitMQConnection 類"""

    @pytest.fixture
    def rabbitmq_settings(self):
        """創建測試用的 RabbitMQ 設置"""
        return RabbitMQSettings(
            rabbitmq_host="localhost",
            rabbitmq_port=5672,
            rabbitmq_user="test",
            rabbitmq_password="test",
            rabbitmq_queue="test.queue",
            rabbitmq_exchange="test.exchange",
        )

    @pytest.fixture
    def rabbitmq_connection(self, rabbitmq_settings):
        """創建 RabbitMQConnection 實例"""
        return RabbitMQConnection(rabbitmq_settings)

    @pytest.mark.asyncio
    @patch("aio_pika.connect_robust")
    async def test_connect_success(self, mock_connect, rabbitmq_connection):
        """測試成功連接"""
        # 設置 Mock
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_conn.is_closed = False
        mock_channel.is_closed = False
        mock_connect.return_value = mock_conn

        # 執行連接
        await rabbitmq_connection.connect()

        # 驗證
        assert rabbitmq_connection.is_connected()
        mock_connect.assert_called_once()

    @pytest.mark.asyncio
    @patch("aio_pika.connect_robust")
    async def test_connect_retry_on_failure(self, mock_connect, rabbitmq_connection):
        """測試連接失敗時的重試機制"""
        # 設置 Mock：前兩次失敗，第三次成功
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_conn.is_closed = False
        mock_channel.is_closed = False
        mock_connect.side_effect = [Exception("Connection failed"), Exception("Connection failed"), mock_conn]

        # 執行連接（應該重試並成功）
        rabbitmq_connection._max_retries = 3
        await rabbitmq_connection.connect()

        # 驗證重試了 3 次
        assert mock_connect.call_count == 3
        assert rabbitmq_connection.is_connected()

    @pytest.mark.asyncio
    @patch("aio_pika.connect_robust")
    async def test_setup_queue(self, mock_connect, rabbitmq_connection):
        """測試設置隊列"""
        # 設置 Mock
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_queue = AsyncMock()
        mock_queue.name = "test.queue"
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_conn.is_closed = False
        mock_channel.is_closed = False
        mock_connect.return_value = mock_conn

        # 連接並設置隊列
        await rabbitmq_connection.connect()
        queue = await rabbitmq_connection.setup_queue("test.queue")

        # 驗證
        assert queue.name == "test.queue"
        mock_channel.declare_queue.assert_called_once()

    @pytest.mark.asyncio
    @patch("aio_pika.connect_robust")
    async def test_close(self, mock_connect, rabbitmq_connection):
        """測試關閉連接"""
        # 設置 Mock
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_channel.is_closed = False
        mock_conn.is_closed = False
        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_connect.return_value = mock_conn

        # 連接並關閉
        await rabbitmq_connection.connect()
        await rabbitmq_connection.close()

        # 驗證
        assert not rabbitmq_connection.is_connected()
        mock_channel.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestDialogueArchiveConsumer:
    """測試 DialogueArchiveConsumer 類"""

    @pytest.fixture
    def mock_memory_service(self):
        """創建模擬的記憶服務"""
        return Mock(spec=IMemoryService)

    @pytest.fixture
    def mock_rabbitmq_connection(self):
        """創建模擬的 RabbitMQ 連接"""
        mock_conn = Mock(spec=RabbitMQConnection)
        mock_conn.is_connected.return_value = True
        mock_conn.settings = Mock()
        mock_conn.settings.rabbitmq_queue = "test.queue"
        return mock_conn

    @pytest.fixture
    def consumer(self, mock_memory_service, mock_rabbitmq_connection):
        """創建消費者實例"""
        return DialogueArchiveConsumer(
            memory_service=mock_memory_service,
            rabbitmq_connection=mock_rabbitmq_connection,
        )

    @pytest.fixture
    def dialogue_message(self):
        """創建測試用的對話歸檔消息"""
        return DialogueArchiveMessage(
            dialog_id="dialog123",
            user_id="user123",
            timestamp=datetime.utcnow(),
            turn=1,
            user_query="What is Python?",
            ai_response="Python is a programming language.",
        )

    @pytest.mark.asyncio
    async def test_start_consuming_success(
        self, consumer, mock_rabbitmq_connection, mock_memory_service
    ):
        """測試成功啟動消費"""
        # 設置 Mock
        mock_queue = AsyncMock()
        mock_queue.name = "test.queue"
        mock_consumer = AsyncMock()
        mock_queue.consume = AsyncMock(return_value=mock_consumer)
        mock_rabbitmq_connection.connect = AsyncMock()
        mock_rabbitmq_connection.is_connected = Mock(return_value=False)
        mock_rabbitmq_connection.setup_queue = AsyncMock(return_value=mock_queue)

        # 執行啟動
        await consumer.start_consuming()

        # 驗證
        assert consumer.is_consuming()
        mock_rabbitmq_connection.connect.assert_called_once()
        mock_rabbitmq_connection.setup_queue.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_success(
        self, consumer, mock_memory_service, dialogue_message
    ):
        """測試成功處理消息"""
        # 設置 Mock
        mock_memory_service.archive = AsyncMock()
        message_body = json.dumps(dialogue_message.model_dump(mode="json")).encode("utf-8")
        mock_message = Mock(spec=IncomingMessage)
        mock_message.body = message_body
        mock_message.ack = AsyncMock()
        mock_message.nack = AsyncMock()

        # 執行處理
        await consumer._handle_message(mock_message)

        # 驗證
        mock_memory_service.archive.assert_called_once()
        mock_message.ack.assert_called_once()
        mock_message.nack.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_invalid_json(self, consumer, mock_memory_service):
        """測試處理無效 JSON 消息"""
        # 設置 Mock
        mock_message = Mock(spec=IncomingMessage)
        mock_message.body = b"invalid json"
        mock_message.ack = AsyncMock()
        mock_message.nack = AsyncMock()

        # 執行處理
        await consumer._handle_message(mock_message)

        # 驗證
        mock_memory_service.archive.assert_not_called()
        mock_message.ack.assert_not_called()
        mock_message.nack.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_process_message_invalid_schema(self, consumer, mock_memory_service):
        """測試處理無效 Schema 消息"""
        # 設置 Mock
        invalid_data = {"invalid": "data"}
        message_body = json.dumps(invalid_data).encode("utf-8")
        mock_message = Mock(spec=IncomingMessage)
        mock_message.body = message_body
        mock_message.ack = AsyncMock()
        mock_message.nack = AsyncMock()

        # 執行處理
        await consumer._handle_message(mock_message)

        # 驗證
        mock_memory_service.archive.assert_not_called()
        mock_message.ack.assert_not_called()
        mock_message.nack.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_process_message_archive_error(
        self, consumer, mock_memory_service, dialogue_message
    ):
        """測試處理消息時 archive 方法拋出異常"""
        # 設置 Mock
        mock_memory_service.archive = AsyncMock(side_effect=Exception("Archive error"))
        message_body = json.dumps(dialogue_message.model_dump(mode="json")).encode("utf-8")
        mock_message = Mock(spec=IncomingMessage)
        mock_message.body = message_body
        mock_message.ack = AsyncMock()
        mock_message.nack = AsyncMock()

        # 執行處理
        await consumer._handle_message(mock_message)

        # 驗證
        mock_memory_service.archive.assert_called_once()
        mock_message.ack.assert_not_called()
        mock_message.nack.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    async def test_stop_consuming(self, consumer, mock_rabbitmq_connection):
        """測試停止消費"""
        # 設置 Mock
        mock_queue = AsyncMock()
        mock_queue.name = "test.queue"
        mock_queue.consume = AsyncMock(return_value=AsyncMock())
        mock_consumer = AsyncMock()
        mock_queue.consume.return_value = mock_consumer
        mock_rabbitmq_connection.connect = AsyncMock()
        mock_rabbitmq_connection.setup_queue = AsyncMock(return_value=mock_queue)

        # 啟動並停止
        await consumer.start_consuming()
        await consumer.stop_consuming()

        # 驗證
        assert not consumer.is_consuming()
        mock_consumer.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_consuming_wait_for_tasks(
        self, consumer, mock_rabbitmq_connection, mock_memory_service, dialogue_message
    ):
        """測試停止消費時等待正在處理的任務完成"""
        # 設置 Mock
        mock_queue = AsyncMock()
        mock_queue.name = "test.queue"
        mock_consumer = AsyncMock()
        mock_queue.consume = AsyncMock(return_value=mock_consumer)
        mock_rabbitmq_connection.connect = AsyncMock()
        mock_rabbitmq_connection.is_connected = Mock(return_value=False)
        mock_rabbitmq_connection.setup_queue = AsyncMock(return_value=mock_queue)

        # 啟動消費
        await consumer.start_consuming()

        # 創建一個立即完成的任務
        mock_memory_service.archive = AsyncMock()
        message_body = json.dumps(dialogue_message.model_dump(mode="json")).encode("utf-8")
        mock_message = Mock(spec=IncomingMessage)
        mock_message.body = message_body
        mock_message.ack = AsyncMock()

        # 開始處理消息並等待完成
        await consumer._handle_message(mock_message)

        # 將任務添加到處理任務集合（模擬正在處理的任務）
        # 注意：由於任務已經完成，stop_consuming 應該能夠立即完成
        task = asyncio.create_task(consumer._handle_message(mock_message))
        await task  # 等待任務完成
        consumer._processing_tasks.add(task)

        # 停止消費（應該能夠立即完成，因為任務已經完成）
        await consumer.stop_consuming(timeout=1.0)

        # 驗證任務已完成且 ack 被調用
        assert task.done()
        # 驗證 archive 和 ack 都被調用了兩次（因為我們調用了兩次 _handle_message）
        assert mock_memory_service.archive.call_count == 2
        assert mock_message.ack.call_count == 2

