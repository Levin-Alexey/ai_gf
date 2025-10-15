"""
Диагностические команды для проверки подключений в многосерверной архитектуре
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_postgresql_connection():
    """Тест подключения к PostgreSQL"""
    try:
        logger.info("🔍 Тестируем подключение к PostgreSQL...")
        from database import async_session_maker
        
        async with async_session_maker() as session:
            result = await session.execute("SELECT 1 as test")
            test_value = result.scalar()
            
        if test_value == 1:
            logger.info("✅ PostgreSQL подключение работает!")
            return True
        else:
            logger.error("❌ PostgreSQL вернул неожиданный результат")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
        logger.error(f"🔍 DATABASE_URL: {os.getenv('DATABASE_URL', 'НЕ НАЙДЕН')}")
        return False

async def test_redis_connection():
    """Тест подключения к Redis"""
    try:
        logger.info("🔍 Тестируем подключение к Redis...")
        from redis_client import redis_client
        
        await redis_client.connect()
        await redis_client.redis.ping()
        await redis_client.disconnect()
        
        logger.info("✅ Redis подключение работает!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {e}")
        logger.error(f"🔍 REDIS_HOST: {os.getenv('REDIS_HOST', 'НЕ НАЙДЕН')}")
        logger.error(f"🔍 REDIS_PORT: {os.getenv('REDIS_PORT', 'НЕ НАЙДЕН')}")
        return False

def test_rabbitmq_connection():
    """Тест подключения к RabbitMQ"""
    try:
        logger.info("🔍 Тестируем подключение к RabbitMQ...")
        from queue_client import queue_client
        
        queue_client.connect()
        queue_client.disconnect()
        
        logger.info("✅ RabbitMQ подключение работает!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
        logger.error(f"🔍 RABBITMQ_HOST: {os.getenv('RABBITMQ_HOST', 'НЕ НАЙДЕН')}")
        logger.error(f"🔍 RABBITMQ_PORT: {os.getenv('RABBITMQ_PORT', 'НЕ НАЙДЕН')}")
        return False

async def test_vector_db():
    """Тест векторной базы данных"""
    try:
        logger.info("🔍 Тестируем векторную базу данных...")
        from vector_client import vector_client
        
        await vector_client.initialize()
        stats = await vector_client.get_collection_stats()
        
        logger.info("✅ Векторная база данных работает!")
        logger.info(f"📊 Статистика: {stats}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка векторной базы данных: {e}")
        logger.error(f"🔍 VECTOR_DB_PATH: {os.getenv('VECTOR_DB_PATH', 'НЕ НАЙДЕН')}")
        return False

async def test_llm_api():
    """Тест LLM API"""
    try:
        logger.info("🔍 Тестируем LLM API...")
        import aiohttp
        
        api_url = os.getenv('LLM_API_URL')
        api_key = os.getenv('LLM_API_KEY')
        
        if not api_url or not api_key:
            logger.error("❌ LLM API настройки не найдены")
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": os.getenv('LLM_MODEL', 'openai/gpt-3.5-turbo'),
            "messages": [{"role": "user", "content": "Тест"}],
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=data, headers=headers) as response:
                if response.status == 200:
                    logger.info("✅ LLM API работает!")
                    return True
                else:
                    logger.error(f"❌ LLM API вернул статус: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Ошибка LLM API: {e}")
        return False

async def test_bot_token():
    """Тест токена бота"""
    try:
        logger.info("🔍 Тестируем токен бота...")
        from aiogram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("❌ BOT_TOKEN не найден")
            return False
        
        bot = Bot(token=bot_token)
        bot_info = await bot.get_me()
        await bot.session.close()
        
        logger.info(f"✅ Токен бота работает! Бот: @{bot_info.username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка токена бота: {e}")
        return False

async def run_all_tests():
    """Запуск всех диагностических тестов"""
    logger.info("🚀 Запускаем диагностику системы...")
    logger.info("=" * 50)
    
    tests = [
        ("PostgreSQL", test_postgresql_connection()),
        ("Redis", test_redis_connection()),
        ("RabbitMQ", test_rabbitmq_connection()),
        ("Vector DB", test_vector_db()),
        ("LLM API", test_llm_api()),
        ("Bot Token", test_bot_token()),
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        logger.info(f"\n🧪 Тест: {test_name}")
        logger.info("-" * 30)
        
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    logger.info("\n" + "=" * 50)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ:")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        logger.info(f"{test_name:15} | {status}")
        if result:
            passed += 1
    
    logger.info("-" * 50)
    logger.info(f"Результат: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        logger.info("🎉 Все тесты прошли! Система готова к работе!")
    else:
        logger.info("⚠️  Есть проблемы! Проверьте настройки подключений.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests())
