"""
Тест всей системы долгосрочной памяти
"""
import asyncio
import sys
import traceback

async def test_system():
    """Тест всей системы"""
    print("🧪 Тестируем систему долгосрочной памяти...")
    
    try:
        # 1. Тест импорта модулей
        print("\n1️⃣ Тестируем импорт модулей...")
        from memory_client import memory_client
        from vector_client import vector_client
        from llm_worker import llm_worker
        from redis_client import redis_client
        from queue_client import queue_client
        print("✅ Все модули импортируются успешно!")
        
        # 2. Тест подключения к базе данных
        print("\n2️⃣ Тестируем подключение к PostgreSQL...")
        from database import async_session_maker
        async with async_session_maker() as session:
            result = await session.execute("SELECT 1")
            print("✅ PostgreSQL подключение работает!")
        
        # 3. Тест подключения к Redis
        print("\n3️⃣ Тестируем подключение к Redis...")
        await redis_client.connect()
        await redis_client.disconnect()
        print("✅ Redis подключение работает!")
        
        # 4. Тест подключения к RabbitMQ
        print("\n4️⃣ Тестируем подключение к RabbitMQ...")
        await queue_client.connect()
        await queue_client.disconnect()
        print("✅ RabbitMQ подключение работает!")
        
        # 5. Тест инициализации векторной базы
        print("\n5️⃣ Тестируем инициализацию векторной базы...")
        await vector_client.initialize()
        stats = await vector_client.get_collection_stats()
        print(f"✅ Векторная база инициализирована! Статистика: {stats}")
        
        # 6. Тест создания воспоминания
        print("\n6️⃣ Тестируем создание воспоминания...")
        from models import MemoryType, MemoryImportance
        
        # Создаем тестовое воспоминание
        memory = await memory_client.add_memory(
            user_id=12345,  # Тестовый пользователь
            content="Тестовое воспоминание для проверки системы",
            memory_type=MemoryType.FACT,
            importance=MemoryImportance.MEDIUM,
            tags=["тест", "система"]
        )
        print(f"✅ Воспоминание создано! ID: {memory.id}")
        
        # 7. Тест семантического поиска
        print("\n7️⃣ Тестируем семантический поиск...")
        similar_memories = await memory_client.search_semantic_memories(
            user_id=12345,
            query="тест системы",
            limit=5
        )
        print(f"✅ Семантический поиск работает! Найдено: {len(similar_memories)} воспоминаний")
        
        # 8. Тест добавления эмоции
        print("\n8️⃣ Тестируем добавление эмоции...")
        emotion = await memory_client.add_emotion(
            user_id=12345,
            emotion="happy",
            intensity=0.8,
            context="Тестирование системы"
        )
        print(f"✅ Эмоция добавлена! ID: {emotion.id}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🚀 Система готова к работе!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        print("\n🔍 Детали ошибки:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_system())
    if success:
        print("\n✅ Система полностью готова!")
        sys.exit(0)
    else:
        print("\n❌ Есть проблемы в системе!")
        sys.exit(1)
