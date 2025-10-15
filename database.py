import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from models import Base


# ВАЖНО: Загружаем .env ПЕРЕД получением DATABASE_URL
load_dotenv()

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql+asyncpg://user:password@localhost/ai_gf'
)

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": False,  # Отключаем SSL для упрощения подключения
        "timeout": 30,  # Увеличиваем timeout до 30 секунд
    }
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Инициализация базы данных (создание таблиц).
    ВНИМАНИЕ: Enum типы должны быть созданы вручную через SQL!
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔗 Инициализация подключения к PostgreSQL...")
        logger.info(f"📊 DATABASE_URL: {DATABASE_URL}")
        
        async with engine.begin() as conn:
            # Создаем таблицы (но не enum типы!)
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ PostgreSQL база данных инициализирована успешно!")
        logger.info("📋 Все таблицы созданы/проверены")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        logger.error(f"🔍 Проверьте подключение к PostgreSQL серверу")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных.
    Используется в обработчиках для работы с БД.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Закрытие соединения с базой данных"""
    await engine.dispose()
