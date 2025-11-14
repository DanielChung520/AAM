"""
@purpose: 測試消息隊列集成，驗證端到端的消息處理流程
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import aio_pika
import pytest

from src.core.services.memory_service import MemoryServiceImpl
from src.infrastructure.ai.mock_analysis_model import MockAnalysisModel
from src.infrastructure.database import ChromaKnowledgeStore, PgPersonaStore
from src.infrastructure.messaging import DialogueArchiveConsumer, RabbitMQConnection
from src.models.domain.dialogue import DialogueArchiveMessage
from src.config.settings import RabbitMQSettings, get_settings


@pytest.mark.integration
class TestMessageQueueIntegration:
    """測試消息隊列集成"""

    @pytest.fixture
    def rabbitmq_settings(self):
        """創建測試用的 RabbitMQ 設置"""
        settings = get_settings()
        return RabbitMQSettings(
            rabbitmq_host=settings.rabbitmq.rabbitmq_host,
            rabbitmq_port=settings.rabbitmq.rabbitmq_port,
            rabbitmq_user=settings.rabbitmq.rabbitmq_user,
            rabbitmq_password=settings.rabbitmq.rabbitmq_password,
            rabbitmq_queue="test.dialogue.archive",
            rabbitmq_exchange="test.exchange",
        )

    @pytest.fixture
    def mock_knowledge_store(self):
        """創建模擬的知識庫（避免真實數據庫依賴）"""
        return Mock()

    @pytest.fixture
    def mock_persona_store(self):
        """創建模擬的用戶畫像存儲（避免真實數據庫依賴）"""
        return Mock()

    @pytest.fixture
    def memory_service(self, mock_knowledge_store, mock_persona_store):
        """創建記憶服務實例"""
        analysis_model = MockAnalysisModel()
        return MemoryServiceImpl(
            knowledge_store=mock_knowledge_store,
            persona_store=mock_persona_store,
            analysis_model=analysis_model,
        )

    @pytest.fixture
    def dialogue_message(self):
        """創建測試用的對話歸檔消息"""
        return DialogueArchiveMessage(
            dialog_id="test_dialog_123",
            user_id="test_user_123",
            timestamp=datetime.utcnow(),
            turn=1,
            user_query="What is Python?",
            ai_response="Python is a programming language.",
        )

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要真實的 RabbitMQ 環境，在 CI/CD 中運行")
    async def test_end_to_end_message_processing(
        self,
        rabbitmq_settings,
        memory_service,
        dialogue_message,
        mock_knowledge_store,
        mock_persona_store,
    ):
        """
        測試端到端消息處理流程

        注意：此測試需要真實的 RabbitMQ 環境
        在本地開發環境中可以使用 docker-compose 啟動 RabbitMQ
        """
        # 設置 Mock 返回值
        mock_knowledge_store.save = AsyncMock()
        mock_persona_store.get = AsyncMock(return_value=None)
        mock_persona_store.save_or_update = AsyncMock()

        # 創建 RabbitMQ 連接
        rabbitmq_connection = RabbitMQConnection(rabbitmq_settings)

        try:
            # 連接 RabbitMQ
            await rabbitmq_connection.connect()

            # 設置隊列
            queue = await rabbitmq_connection.setup_queue(
                queue_name=rabbitmq_settings.rabbitmq_queue
            )

            # 創建消費者
            consumer = DialogueArchiveConsumer(
                memory_service=memory_service,
                rabbitmq_connection=rabbitmq_connection,
            )

            # 啟動消費者
            await consumer.start_consuming()

            # 發送測試消息到隊列
            channel = rabbitmq_connection.channel
            message_body = json.dumps(dialogue_message.model_dump(mode="json")).encode(
                "utf-8"
            )
            await channel.default_exchange.publish(
                aio_pika.Message(message_body),
                routing_key=rabbitmq_settings.rabbitmq_queue,
            )

            # 等待消息處理（最多等待 5 秒）
            await asyncio.sleep(2.0)

            # 驗證記憶服務被調用
            mock_knowledge_store.save.assert_called_once()
            mock_persona_store.save_or_update.assert_called_once()

            # 停止消費者
            await consumer.stop_consuming()

        finally:
            # 清理：關閉連接
            await rabbitmq_connection.close()

    @pytest.mark.asyncio
    async def test_message_validation_integration(
        self, rabbitmq_settings, memory_service
    ):
        """
        測試消息驗證集成

        驗證無效消息格式的處理
        """
        # 創建 RabbitMQ 連接
        rabbitmq_connection = RabbitMQConnection(rabbitmq_settings)

        try:
            # 連接 RabbitMQ
            await rabbitmq_connection.connect()

            # 設置隊列
            await rabbitmq_connection.setup_queue(
                queue_name=rabbitmq_settings.rabbitmq_queue
            )

            # 創建消費者
            consumer = DialogueArchiveConsumer(
                memory_service=memory_service,
                rabbitmq_connection=rabbitmq_connection,
            )

            # 創建無效消息
            invalid_message = Mock()
            invalid_message.body = b"invalid json"
            invalid_message.ack = AsyncMock()
            invalid_message.nack = AsyncMock()

            # 處理無效消息
            await consumer._handle_message(invalid_message)

            # 驗證消息被拒絕（不重新入隊）
            invalid_message.nack.assert_called_once_with(requeue=False)
            invalid_message.ack.assert_not_called()

        finally:
            # 清理：關閉連接
            await rabbitmq_connection.close()

    @pytest.mark.asyncio
    async def test_consumer_graceful_shutdown(
        self, rabbitmq_settings, memory_service, dialogue_message
    ):
        """
        測試消費者優雅關閉

        驗證停止消費時正在處理的消息能夠完成
        """
        # 設置 Mock：模擬慢速處理
        async def slow_save(*args, **kwargs):
            await asyncio.sleep(0.5)
            return None

        memory_service.archive = AsyncMock(side_effect=slow_save)

        # 創建 RabbitMQ 連接
        rabbitmq_connection = RabbitMQConnection(rabbitmq_settings)

        try:
            # 連接 RabbitMQ
            await rabbitmq_connection.connect()

            # 設置隊列
            await rabbitmq_connection.setup_queue(
                queue_name=rabbitmq_settings.rabbitmq_queue
            )

            # 創建消費者
            consumer = DialogueArchiveConsumer(
                memory_service=memory_service,
                rabbitmq_connection=rabbitmq_connection,
            )

            # 啟動消費者
            await consumer.start_consuming()

            # 開始處理一個消息（模擬正在處理的消息）
            message_body = json.dumps(dialogue_message.model_dump(mode="json")).encode(
                "utf-8"
            )
            mock_message = Mock()
            mock_message.body = message_body
            mock_message.ack = AsyncMock()

            # 開始處理消息
            task = asyncio.create_task(consumer._handle_message(mock_message))
            consumer._processing_tasks.add(task)

            # 停止消費者（應該等待正在處理的消息完成）
            stop_task = asyncio.create_task(consumer.stop_consuming(timeout=2.0))
            await stop_task

            # 驗證消息處理完成
            assert task.done()
            mock_message.ack.assert_called_once()

        finally:
            # 清理：關閉連接
            await rabbitmq_connection.close()

