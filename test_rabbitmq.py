"""
Простой тест подключения к RabbitMQ
"""
import logging
from queue_client import queue_client
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_VHOST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rabbitmq():
    """Тестируем подключение к RabbitMQ"""
    try:
        logger.info("🧪 Тестируем подключение к RabbitMQ...")
        logger.info(f"📊 Хост: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        logger.info(f"📊 Пользователь: {RABBITMQ_USER}")
        logger.info(f"📊 Vhost: {RABBITMQ_VHOST}")
        
        # Пытаемся подключиться
        queue_client.connect()
        logger.info("✅ Подключение к RabbitMQ успешно!")
        
        # Пытаемся отправить тестовое сообщение
        test_message = {
            "user_id": 123456,
            "chat_id": 123456,
            "message": "Тестовое сообщение",
            "timestamp": 1234567890
        }
        
        queue_client.publish_message(test_message)
        logger.info("✅ Тестовое сообщение отправлено в очередь!")
        
        # Отключаемся
        queue_client.disconnect()
        logger.info("✅ Отключение от RabbitMQ успешно!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании RabbitMQ: {e}")
        logger.error(f"❌ Тип ошибки: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_rabbitmq()
    if success:
        print("\n🎉 RabbitMQ работает корректно!")
    else:
        print("\n⚠️ RabbitMQ имеет проблемы!")