"""
RabbitMQ асинхронный клиент для очередей сообщений
"""
import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
import aio_pika
from aio_pika import Connection, Channel, Queue, Message
from aio_pika.abc import AbstractRobustConnection
from config import (RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER,
                   RABBITMQ_PASSWORD, RABBITMQ_VHOST)

logger = logging.getLogger(__name__)


class QueueClient:
    """Асинхронный клиент для работы с RabbitMQ"""
    
    def __init__(self):
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[Channel] = None
        self.queue_name = "llm_requests"
        self.response_queue = "llm_responses"
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            logger.info(f"🔗 Подключаемся к RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            logger.info(f"📊 RabbitMQ конфигурация: user={RABBITMQ_USER}, vhost={RABBITMQ_VHOST}")
            
            # Создаем URL подключения
            rabbitmq_url = (
                f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}"
                f"@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
            )
            
            # Подключаемся к RabbitMQ с robust connection (автоматическое переподключение)
            self.connection = await aio_pika.connect_robust(
                rabbitmq_url,
                timeout=30,
                heartbeat=600
            )
            
            # Создаем канал
            self.channel = await self.connection.channel()
            
            # Объявляем очереди
            await self.channel.declare_queue(self.queue_name, durable=True)
            await self.channel.declare_queue(self.response_queue, durable=True)
            
            logger.info("✅ RabbitMQ подключение установлено успешно!")
            logger.info(f"📋 Созданы очереди: {self.queue_name}, {self.response_queue}")
            
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Соединение с RabbitMQ закрыто")
        except Exception as e:
            logger.error(f"Ошибка отключения от RabbitMQ: {e}")
    
    async def publish_message(self, message: Dict[str, Any]) -> None:
        """Отправить сообщение в очередь"""
        try:
            if not self.channel or self.channel.is_closed:
                raise Exception("Канал RabbitMQ не открыт")
            
            # Создаем сообщение
            message_body = json.dumps(message).encode()
            aio_message = Message(
                message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            # Отправляем сообщение в очередь
            await self.channel.default_exchange.publish(
                aio_message,
                routing_key=self.queue_name
            )
            
            logger.info(f"Сообщение отправлено в очередь: {message.get('user_id')}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в очередь: {e}")
            raise
    
    async def consume_requests(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Прослушивать запросы из очереди"""
        try:
            if not self.channel or self.channel.is_closed:
                raise Exception("Канал RabbitMQ не открыт")
            
            # Получаем очередь
            queue: Queue = await self.channel.get_queue(self.queue_name)
            
            async def on_message(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        # Декодируем сообщение
                        body = json.loads(message.body.decode())
                        
                        # Вызываем callback
                        if asyncio.iscoroutinefunction(callback):
                            await callback(body)
                        else:
                            callback(body)
                            
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения: {e}")
            
            # Настраиваем потребление сообщений
            await self.channel.set_qos(prefetch_count=1)
            await queue.consume(on_message)
            
            logger.info("Начинаем прослушивание запросов...")
            
        except Exception as e:
            logger.error(f"Ошибка потребления сообщений: {e}")
            raise
    
    async def stop_consuming(self):
        """Остановить потребление сообщений"""
        try:
            if self.channel and not self.channel.is_closed:
                # В aio-pika остановка происходит через отмену задач или закрытие канала
                logger.info("Потребление сообщений остановлено")
        except Exception as e:
            logger.error(f"Ошибка остановки потребления: {e}")


# Глобальный экземпляр клиента очередей
queue_client = QueueClient()
