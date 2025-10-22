"""
Тест интеграции ЮKassa и webhook сервера
"""
import asyncio
import sys


async def test_imports():
    """Проверка установки всех зависимостей"""
    print("🔍 Проверка зависимостей...\n")
    
    errors = []
    
    # Проверяем yookassa
    try:
        from yookassa import Configuration, Payment
        print("✅ yookassa установлен")
    except ImportError:
        errors.append("❌ yookassa НЕ установлен")
        print(errors[-1])
    
    # Проверяем fastapi
    try:
        from fastapi import FastAPI
        print("✅ fastapi установлен")
    except ImportError:
        errors.append("❌ fastapi НЕ установлен")
        print(errors[-1])
    
    # Проверяем uvicorn
    try:
        import uvicorn
        print("✅ uvicorn установлен")
    except ImportError:
        errors.append("❌ uvicorn НЕ установлен")
        print(errors[-1])
    
    # Проверяем pydantic
    try:
        from pydantic import BaseModel
        print("✅ pydantic установлен")
    except ImportError:
        errors.append("❌ pydantic НЕ установлен")
        print(errors[-1])
    
    print()
    
    if errors:
        print("⚠️  Найдены проблемы с зависимостями!")
        print("Установите: .\\install_payment_deps.bat")
        return False
    else:
        print("✅ Все зависимости установлены!\n")
        return True


async def test_config():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации...\n")
    
    from config import (
        PAYMENT_SHOP_ID,
        PAYMENT_SECRET_KEY,
        WEBHOOK_URL
    )
    
    errors = []
    
    if not PAYMENT_SHOP_ID:
        errors.append("❌ PAYMENT_SHOP_ID не установлен в .env")
        print(errors[-1])
    else:
        print(f"✅ PAYMENT_SHOP_ID: {PAYMENT_SHOP_ID}")
    
    if not PAYMENT_SECRET_KEY:
        errors.append("❌ PAYMENT_SECRET_KEY не установлен в .env")
        print(errors[-1])
    else:
        print(f"✅ PAYMENT_SECRET_KEY: {PAYMENT_SECRET_KEY[:20]}...")
    
    if not WEBHOOK_URL:
        errors.append("⚠️  WEBHOOK_URL не установлен (нужно добавить в .env)")
        print(errors[-1])
    else:
        print(f"✅ WEBHOOK_URL: {WEBHOOK_URL}")
    
    print()
    
    if errors:
        print("⚠️  Найдены проблемы с конфигурацией!")
        return False
    else:
        print("✅ Конфигурация корректна!\n")
        return True


async def test_yookassa_connection():
    """Проверка подключения к ЮKassa API"""
    print("🔍 Проверка подключения к ЮKassa...\n")
    
    try:
        from yookassa import Configuration, Payment
        from config import PAYMENT_SHOP_ID, PAYMENT_SECRET_KEY
        
        # Настраиваем ЮKassa
        Configuration.account_id = PAYMENT_SHOP_ID
        Configuration.secret_key = PAYMENT_SECRET_KEY
        
        # Пробуем получить список платежей (проверка авторизации)
        payments = Payment.list({"limit": 1})
        
        print("✅ Подключение к ЮKassa успешно!")
        print(f"   Account ID: {PAYMENT_SHOP_ID}")
        print(f"   Платежей в истории: проверено\n")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к ЮKassa: {e}\n")
        print("   Проверьте PAYMENT_SHOP_ID и PAYMENT_SECRET_KEY\n")
        return False


async def test_database():
    """Проверка подключения к БД и наличия поля подписки"""
    print("🔍 Проверка базы данных...\n")
    
    try:
        from database import async_session_maker
        from sqlalchemy import text
        
        async with async_session_maker() as session:
            # Проверяем наличие колонки subscription_expires_at
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' 
                AND column_name='subscription_expires_at'
            """))
            
            if result.scalar():
                print("✅ Поле subscription_expires_at существует")
                
                # Проверяем наличие индекса
                result = await session.execute(text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename='users' 
                    AND indexname='idx_users_subscription'
                """))
                
                if result.scalar():
                    print("✅ Индекс idx_users_subscription существует")
                else:
                    print("⚠️  Индекс idx_users_subscription НЕ существует")
                
                print()
                return True
            else:
                print("❌ Поле subscription_expires_at НЕ существует!")
                print("   Запустите: python apply_subscription_migration.py\n")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}\n")
        return False


async def test_webhook_server():
    """Проверка импорта webhook сервера"""
    print("🔍 Проверка webhook сервера...\n")
    
    try:
        import webhook_server
        print("✅ webhook_server.py импортируется без ошибок")
        print("   Запустите: python webhook_server.py")
        print("   Порт: 8000\n")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта webhook_server: {e}\n")
        return False


async def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ СИСТЕМЫ ПЛАТЕЖЕЙ")
    print("=" * 60)
    print()
    
    results = []
    
    # Тест 1: Зависимости
    results.append(await test_imports())
    
    # Тест 2: Конфигурация
    results.append(await test_config())
    
    # Тест 3: ЮKassa
    results.append(await test_yookassa_connection())
    
    # Тест 4: База данных
    results.append(await test_database())
    
    # Тест 5: Webhook сервер
    results.append(await test_webhook_server())
    
    # Итоги
    print("=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 60)
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Пройдено: {passed}/{total}")
    print(f"❌ Провалено: {total - passed}/{total}")
    print()
    
    if all(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print()
        print("📝 Следующие шаги:")
        print("1. Добавьте WEBHOOK_URL в .env")
        print("2. Запустите: python webhook_server.py")
        print("3. Настройте webhook в ЮKassa: https://yookassa.ru/my/shop-settings")
        print("4. Протестируйте платёж в боте!")
    else:
        print("⚠️  Некоторые тесты провалены!")
        print("Исправьте ошибки и запустите тест снова.")
    
    print()


if __name__ == '__main__':
    asyncio.run(main())
