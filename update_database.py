"""
Скрипт для обновления базы данных PostgreSQL
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def update_database():
    """Обновление базы данных для долгосрочной памяти"""
    try:
        # Подключение к базе данных
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL не найден в .env файле!")
            return
        
        # Исправляем URL для asyncpg
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f"🔗 Подключаемся к базе данных...")
        conn = await asyncpg.connect(database_url)
        
        # Чтение SQL файла
        print("📖 Читаем SQL скрипт...")
        with open('update_db_memory.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Выполнение скрипта
        print("⚡ Выполняем обновление базы данных...")
        await conn.execute(sql_script)
        
        # Проверяем созданные таблицы
        print("🔍 Проверяем созданные таблицы...")
        
        # Проверяем таблицы
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_memories', 'user_emotions', 'user_relationships')
            ORDER BY table_name
        """)
        
        print("✅ Созданные таблицы:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Проверяем enum типы
        enums = await conn.fetch("""
            SELECT typname 
            FROM pg_type 
            WHERE typname IN ('memory_type', 'memory_importance')
            ORDER BY typname
        """)
        
        print("✅ Созданные enum типы:")
        for enum_type in enums:
            print(f"   - {enum_type['typname']}")
        
        # Проверяем индексы
        indexes = await conn.fetch("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename IN ('user_memories', 'user_emotions', 'user_relationships')
            ORDER BY tablename, indexname
        """)
        
        print("✅ Созданные индексы:")
        for index in indexes:
            print(f"   - {index['indexname']}")
        
        await conn.close()
        print("\n🎉 База данных успешно обновлена!")
        print("🚀 Теперь можно запускать бота и воркер!")
        
    except Exception as e:
        print(f"❌ Ошибка обновления базы данных: {e}")
        print("\n💡 Возможные причины:")
        print("   - Неправильные данные подключения в .env")
        print("   - Нет доступа к базе данных")
        print("   - База данных не существует")
        print("   - Пользователь не имеет прав на создание таблиц")

if __name__ == "__main__":
    asyncio.run(update_database())
