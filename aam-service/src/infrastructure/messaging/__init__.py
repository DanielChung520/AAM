"""
@purpose: 消息隊列模塊導出，提供統一的導入接口
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from src.infrastructure.messaging.dialogue_consumer import DialogueArchiveConsumer
from src.infrastructure.messaging.rabbitmq_config import RabbitMQConnection

__all__ = [
    "RabbitMQConnection",
    "DialogueArchiveConsumer",
]

