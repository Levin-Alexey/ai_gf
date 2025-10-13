"""
Скрипт для проверки подключения к PostgreSQL
Запустите: python test_db_connection.py
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


async def test_connection():
    print("=" * 60)
    print("Тест подключения к PostgreSQL")
    print("=" * 60)
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL не найден в .env файле!")
        print("\nСоздайте файл .env и добавьте:")
        print("DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname")
        return
    
    # Скрываем пароль в выводе
    safe_url = DATABASE_URL.replace(
        DATABASE_URL.split('@')[0].split('//')[1].split(':')[-1],
        '***'
    ) if '@' in DATABASE_URL else DATABASE_URL
    
    print(f"\n📌 DATABASE_URL: {safe_url}")
    print(f"\n🔄 Пытаюсь подключиться к серверу...")
    
    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(
                __import__('sqlalchemy').text('SELECT version()')
            )
            version = result.scalar()
            print(f"\n✅ УСПЕХ! Подключение установлено!")
            print(f"📊 PostgreSQL версия: {version}")
        
        await engine.dispose()
        print("\n🎉 Всё работает! Можете запускать бота.")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА подключения!")
        print(f"   Тип ошибки: {type(e).__name__}")
        print(f"   Описание: {e}")
        print("\n💡 Проверьте:")
        print("   1. Правильность DATABASE_URL в файле .env")
        print("   2. Доступность PostgreSQL сервера (хост, порт)")
        print("   3. Правильность логина/пароля")
        print("   4. Что база данных 'ai_gf' существует")
        print("   5. Файрвол не блокирует соединение")
        print(f"\n📝 Формат DATABASE_URL:")
        print("   postgresql+asyncpg://username:password@host:port/database")
        print("   Пример:")
        print("   postgresql+asyncpg://postgres:mypass@192.168.1.100:5432/ai_gf")


if __name__ == '__main__':
    asyncio.run(test_connection())

