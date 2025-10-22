"""
Скрипт для применения миграции добавления поля подписки
"""
import asyncio
from database import engine
from sqlalchemy import text


async def apply_migration():
    """Применить миграцию добавления subscription_expires_at"""
    
    # Список SQL команд для выполнения по отдельности
    sql_commands = [
        """
        ALTER TABLE users 
        ADD COLUMN subscription_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        """,
        """
        CREATE INDEX idx_users_subscription ON users(subscription_expires_at) 
        WHERE subscription_expires_at IS NOT NULL
        """,
        """
        COMMENT ON COLUMN users.subscription_expires_at IS 
        'Дата и время окончания платной подписки. NULL = нет подписки, прошедшая дата = истёкшая подписка'
        """
    ]
    
    # Применяем каждую команду отдельно
    async with engine.begin() as conn:
        for i, sql in enumerate(sql_commands, 1):
            try:
                await conn.execute(text(sql))
                print(f"✅ Команда {i}/3 выполнена успешно")
            except Exception as e:
                if "already exists" in str(e) or "уже существует" in str(e):
                    print(f"⚠️  Команда {i}/3 пропущена (уже выполнена)")
                else:
                    raise
    
    print("\n✅ Миграция успешно применена!")
    print("📋 Добавлено поле: users.subscription_expires_at")
    print("🔍 Создан индекс: idx_users_subscription")
    
    # Закрываем движок
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(apply_migration())
