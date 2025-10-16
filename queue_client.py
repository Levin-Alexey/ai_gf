"""
RabbitMQ клиент для очередей сообщений
"""
import json
import logging
from typing import Dict, Any, Callable
import pika
from config import (RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER,
                   RABBITMQ_PASSWORD, RABBITMQ_VHOST)

logger = logging.getLogger(__name__)


class QueueClient:
    """Клиент для работы с RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "llm_requests"
        self.response_queue = "llm_responses"
    
    def connect(self):
        """Подключение к RabbitMQ"""
        try:
            logger.info(f"🔗 Подключаемся к RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            logger.info(f"📊 RabbitMQ конфигурация: user={RABBITMQ_USER}, vhost={RABBITMQ_VHOST}")
            
            # Создаем параметры подключения с увеличенными таймаутами
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VHOST,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5,
                socket_timeout=30,
                blocked_connection_timeout=300,
                heartbeat=600
            )
            
            # Подключаемся к RabbitMQ
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Объявляем очереди
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.queue_declare(queue=self.response_queue, durable=True)
            
            logger.info("✅ RabbitMQ подключение установлено успешно!")
            logger.info(f"📋 Созданы очереди: {self.queue_name}, {self.response_queue}")
            
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            raise
    
    def disconnect(self):
        """Отключение от RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Соединение с RabbitMQ закрыто")
        except Exception as e:
            logger.error(f"Ошибка отключения от RabbitMQ: {e}")
    
    def publish_message(self, message: Dict[str, Any]) -> None:
        """Отправить сообщение в очередь"""
        try:
            if not self.channel or self.channel.is_closed:
                raise Exception("Канал RabbitMQ не открыт")
            
            # Отправляем сообщение в очередь
            self.channel.basic_publish(
                exchange='',
                routing_key="llm_requests",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Делаем сообщение постоянным
                )
            )
            
            logger.info(f"Сообщение отправлено в очередь: {message.get('user_id')}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в очередь: {e}")
            raise
    
    def consume_requests(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Прослушивать запросы из очереди"""
        try:
            if not self.channel or self.channel.is_closed:
                raise Exception("Канал RabbitMQ не открыт")
            
            def on_message(channel, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(message)
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения: {e}")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Настраиваем потребление сообщений
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=on_message
            )
            
            logger.info("Начинаем прослушивание запросов...")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Ошибка потребления сообщений: {e}")
            raise
    
    def stop_consuming(self):
        """Остановить потребление сообщений"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
                logger.info("Потребление сообщений остановлено")
        except Exception as e:
            logger.error(f"Ошибка остановки потребления: {e}")

# Глобальный экземпляр клиента очередей
queue_client = QueueClient()
