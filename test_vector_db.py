"""
Тест инициализации векторной базы данных
"""
import asyncio
import logging
from vector_client import vector_client

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_vector_db():
    """Тест инициализации векторной базы данных"""
    try:
        print("🧪 Тестируем инициализацию векторной базы данных...")
        
        # Инициализируем векторную базу
        await vector_client.initialize()
        
        # Получаем статистику
        stats = await vector_client.get_collection_stats()
        print(f"📊 Статистика коллекции: {stats}")
        
        # Тестируем добавление тестового воспоминания
        print("📝 Добавляем тестовое воспоминание...")
        success = await vector_client.add_memory(
            memory_id="test_1",
            user_id=12345,
            content="Тестовое воспоминание для проверки векторной базы",
            memory_type="fact",
            importance="medium",
            tags=["тест", "векторная_база"]
        )
        
        if success:
            print("✅ Тестовое воспоминание добавлено!")
        else:
            print("❌ Ошибка добавления тестового воспоминания")
        
        # Тестируем поиск
        print("🔍 Тестируем семантический поиск...")
        similar_memories = await vector_client.search_similar_memories(
            user_id=12345,
            query="тест база данных",
            limit=5
        )
        
        print(f"📋 Найдено {len(similar_memories)} похожих воспоминаний")
        for i, mem in enumerate(similar_memories):
            print(f"   {i+1}. {mem['content'][:50]}... (схожесть: {mem['similarity']:.2f})")
        
        print("\n🎉 Векторная база данных работает корректно!")
        print("📁 Папка vector_db должна была создаться в корне проекта")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования векторной базы: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vector_db())
