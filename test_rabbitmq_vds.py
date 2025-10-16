"""
Расширенный тест подключения к RabbitMQ на VDS сервере
"""
import logging
import pika
import socket
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_VHOST

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_network_connectivity():
    """Тестируем сетевое подключение к серверу"""
    try:
        logger.info(f"🌐 Тестируем TCP подключение к {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        
        # Создаем сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 секунд таймаут
        
        # Пытаемся подключиться
        result = sock.connect_ex((RABBITMQ_HOST, RABBITMQ_PORT))
        sock.close()
        
        if result == 0:
            logger.info("✅ TCP подключение успешно!")
            return True
        else:
            logger.error(f"❌ TCP подключение не удалось: код {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка сетевого подключения: {e}")
        return False

def test_rabbitmq_with_timeouts():
    """Тестируем RabbitMQ с различными таймаутами"""
    timeouts = [10, 30, 60]  # Секунды
    
    for timeout in timeouts:
        try:
            logger.info(f"🧪 Тестируем RabbitMQ с таймаутом {timeout} секунд...")
            
            # Создаем учетные данные
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            
            # Параметры подключения с настраиваемым таймаутом
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VHOST,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1,
                socket_timeout=timeout,
                blocked_connection_timeout=timeout,
                heartbeat=0  # Отключаем heartbeat для теста
            )
            
            # Пытаемся подключиться
            logger.info("🔗 Устанавливаем соединение...")
            connection = pika.BlockingConnection(parameters)
            
            logger.info("📋 Создаем канал...")
            channel = connection.channel()
            
            logger.info("🗂 Объявляем очереди...")
            channel.queue_declare(queue='test_queue', durable=True)
            
            logger.info("📤 Отправляем тестовое сообщение...")
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body='Тестовое сообщение',
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            logger.info("🔚 Закрываем соединение...")
            connection.close()
            
            logger.info(f"✅ RabbitMQ работает с таймаутом {timeout} секунд!")
            return True
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"❌ AMQP ошибка с таймаутом {timeout}с: {e}")
            
        except Exception as e:
            logger.error(f"❌ Общая ошибка с таймаутом {timeout}с: {e}")
    
    return False

def test_rabbitmq_guest():
    """Тестируем подключение с guest/guest (если доступно)"""
    try:
        logger.info("🧪 Тестируем подключение с guest/guest...")
        
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host='/',
            credentials=credentials,
            socket_timeout=30
        )
        
        connection = pika.BlockingConnection(parameters)
        connection.close()
        
        logger.info("✅ Guest подключение работает!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Guest подключение не работает: {e}")
        return False

def main():
    """Основная функция диагностики"""
    logger.info("🚀 Запускаем расширенную диагностику RabbitMQ на VDS...")
    logger.info("=" * 60)
    
    # Информация о конфигурации
    logger.info(f"📊 Сервер: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    logger.info(f"📊 Пользователь: {RABBITMQ_USER}")
    logger.info(f"📊 Виртуальный хост: {RABBITMQ_VHOST}")
    logger.info("=" * 60)
    
    # Тест 1: Сетевое подключение
    logger.info("\n🌐 ШАГ 1: Проверяем сетевое подключение")
    if not test_network_connectivity():
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Нет сетевого подключения к серверу!")
        return False
    
    # Тест 2: RabbitMQ с разными таймаутами
    logger.info("\n🐰 ШАГ 2: Проверяем RabbitMQ с разными таймаутами")
    if test_rabbitmq_with_timeouts():
        logger.info("🎉 RabbitMQ работает!")
        return True
    
    # Тест 3: Guest подключение (если основное не работает)
    logger.info("\n👤 ШАГ 3: Проверяем guest подключение")
    if test_rabbitmq_guest():
        logger.warning("⚠️ Основные учетные данные не работают, но guest работает")
        logger.warning("💡 Проверьте настройки пользователя admin на сервере")
        return False
    
    logger.error("❌ Все тесты провалились!")
    logger.error("💡 Возможные причины:")
    logger.error("   1. Неправильные учетные данные (admin/password)")
    logger.error("   2. Пользователь admin не имеет прав на виртуальный хост '/'")
    logger.error("   3. RabbitMQ сервер не принимает внешние подключения")
    logger.error("   4. Проблемы с файрволом на VDS сервере")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Диагностика завершена успешно!")
    else:
        print("\n⚠️ Диагностика выявила проблемы!")