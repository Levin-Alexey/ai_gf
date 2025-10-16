import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import init_db, close_db
from handlers import main_router
from redis_client import redis_client
from queue_client import queue_client

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден! Создайте файл .env с вашим токеном."
    )

bot = Bot(token=BOT_TOKEN)
# Используем MemoryStorage для FSM (состояний)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем роутер с обработчиками
dp.include_router(main_router)


async def on_startup():
    """Действия при запуске бота"""
    logger.info("🚀 Запуск AI Girlfriend Bot...")
    try:
        # Попытка инициализации БД (создание таблиц, если их нет)
        # ВАЖНО: Enum типы должны быть созданы вручную через init_db.sql!
        logger.info("📡 Инициализация PostgreSQL...")
        await init_db()
        logger.info("✅ PostgreSQL база данных инициализирована")
        
        # Подключаемся к Redis
        logger.info("📡 Подключение к Redis...")
        await redis_client.connect()
        
        # Подключаемся к RabbitMQ
        logger.info("📡 Подключение к RabbitMQ...")
        await queue_client.connect()
        
        logger.info("🎉 Все сервисы успешно подключены!")
        logger.info("💕 AI Girlfriend Bot готов к работе!")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        logger.warning(
            "Убедитесь, что вы выполнили init_db.sql "
            "для создания enum типов и настроили Redis/RabbitMQ!"
        )


async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Остановка бота...")
    
    # Закрываем соединения
    await close_db()
    logger.info("Соединение с БД закрыто")
    
    await redis_client.disconnect()
    logger.info("Соединение с Redis закрыто")
    
    await queue_client.disconnect()
    logger.info("Соединение с RabbitMQ закрыто")


async def main():
    """Основная функция запуска бота"""
    await on_startup()

    try:
        logger.info("Бот запущен и готов к работе! 🚀")
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())
