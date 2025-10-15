"""
Тест подключения к базе данных и проверка новых таблиц
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Тест подключения к базе данных"""
    try:
        database_url = os.getenv('DATABASE_URL')
        print(f"🔗 DATABASE_URL: {database_url}")
        
        if not database_url:
            print("❌ DATABASE_URL не найден в .env файле!")
            return
        
        # Исправляем URL для asyncpg
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f"🔗 Исправленный URL: {database_url}")
        print("🔗 Подключаемся к базе данных...")
        conn = await asyncpg.connect(database_url)
        print("✅ Подключение успешно!")
        
        # Проверяем существующие таблицы
        print("\n📋 Существующие таблицы:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Проверяем новые таблицы
        print("\n🔍 Проверяем новые таблицы для памяти:")
        new_tables = ['user_memories', 'user_emories', 'user_relationships']
        
        for table_name in new_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table_name)
            
            if exists:
                print(f"   ✅ {table_name} - существует")
            else:
                print(f"   ❌ {table_name} - НЕ существует")
        
        # Проверяем enum типы
        print("\n🔍 Проверяем enum типы:")
        enum_types = ['memory_type', 'memory_importance']
        
        for enum_name in enum_types:
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM pg_type 
                    WHERE typname = $1
                )
            """, enum_name)
            
            if exists:
                print(f"   ✅ {enum_name} - существует")
            else:
                print(f"   ❌ {enum_name} - НЕ существует")
        
        await conn.close()
        print("\n✅ Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print(f"Тип ошибки: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_connection())
