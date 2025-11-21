"""
Быстрая диагностика системы платежей
"""
import asyncio
import os
from datetime import datetime, timezone

from database import async_session_maker
from sqlalchemy import select, text
from models import User


async def check_database_connection():
    """Проверка подключения к базе данных"""
    print("\n" + "="*60)
    print("🔌 ПРОВЕРКА: Подключение к базе данных")
    print("="*60 + "\n")
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Подключение успешно!")
            print(f"   PostgreSQL версия: {version}\n")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}\n")
        return False


async def check_users_table():
    """Проверка таблицы пользователей"""
    print("="*60)
    print("👥 ПРОВЕРКА: Таблица пользователей")
    print("="*60 + "\n")
    
    try:
        async with async_session_maker() as session:
            # Подсчет всех пользователей
            result = await session.execute(
                text("SELECT COUNT(*) FROM users;")
            )
            total = result.scalar()
            
            # Подсчет пользователей с подпиской
            result = await session.execute(
                text(
                    "SELECT COUNT(*) FROM users "
                    "WHERE subscription_expires_at IS NOT NULL "
                    "AND subscription_expires_at > NOW();"
                )
            )
            subscribed = result.scalar()
            
            print(f"📊 Статистика:")
            print(f"   Всего пользователей: {total}")
            print(f"   С активной подпиской: {subscribed}")
            print(f"   Без подписки: {total - subscribed}\n")
            
            # Последние 5 пользователей
            result = await session.execute(
                select(User).order_by(User.id.desc()).limit(5)
            )
            users = result.scalars().all()
            
            if users:
                print("📋 Последние 5 пользователей:")
                for user in users:
                    status = "✅ Активна" if (
                        user.subscription_expires_at and
                        user.subscription_expires_at > datetime.now(
                            timezone.utc
                        )
                    ) else "❌ Нет"
                    print(
                        f"   • TG ID: {user.telegram_id}, "
                        f"Имя: {user.get_display_name()}, "
                        f"Подписка: {status}"
                    )
                print()
            
            return True
    except Exception as e:
        print(f"❌ Ошибка проверки таблицы: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def check_subscription_field():
    """Проверка наличия поля subscription_expires_at"""
    print("="*60)
    print("🔍 ПРОВЕРКА: Поле subscription_expires_at")
    print("="*60 + "\n")
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                text(
                    "SELECT column_name, data_type "
                    "FROM information_schema.columns "
                    "WHERE table_name = 'users' "
                    "AND column_name = 'subscription_expires_at';"
                )
            )
            row = result.fetchone()
            
            if row:
                print(f"✅ Поле существует:")
                print(f"   Название: {row[0]}")
                print(f"   Тип данных: {row[1]}\n")
                return True
            else:
                print(
                    "❌ Поле subscription_expires_at НЕ НАЙДЕНО "
                    "в таблице users!\n"
                )
                print(
                    "   Выполните миграцию: "
                    "psql -d ai_gf -f add_subscription_field.sql\n"
                )
                return False
    except Exception as e:
        print(f"❌ Ошибка проверки поля: {e}\n")
        return False


async def check_env_variables():
    """Проверка переменных окружения"""
    print("="*60)
    print("⚙️ ПРОВЕРКА: Переменные окружения")
    print("="*60 + "\n")
    
    required_vars = {
        "DATABASE_URL": "Подключение к БД",
        "BOT_TOKEN": "Telegram Bot Token",
        "PAYMENT_SHOP_ID": "ЮKassa Shop ID",
        "PAYMENT_SECRET_KEY": "ЮKassa Secret Key",
        "WEBHOOK_URL": "URL для webhook"
    }
    
    all_ok = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # Скрываем секретные значения
            if "SECRET" in var or "TOKEN" in var or "PASSWORD" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {desc} ({var}): {display_value}")
        else:
            print(f"❌ {desc} ({var}): НЕ УСТАНОВЛЕНА")
            all_ok = False
    
    print()
    return all_ok


async def run_diagnostics():
    """Запуск всех проверок"""
    print("\n" + "🏥 ДИАГНОСТИКА СИСТЕМЫ ПЛАТЕЖЕЙ" + "\n")
    
    results = {}
    
    # Проверка переменных окружения
    results['env'] = await check_env_variables()
    
    # Проверка подключения к БД
    results['db'] = await check_database_connection()
    
    if results['db']:
        # Проверка поля подписки
        results['field'] = await check_subscription_field()
        
        # Проверка таблицы пользователей
        results['users'] = await check_users_table()
    
    # Итоговый отчёт
    print("="*60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("="*60 + "\n")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("✅ Все проверки пройдены успешно!")
        print("   Система платежей готова к работе.\n")
    else:
        print("❌ Обнаружены проблемы:")
        if not results.get('env'):
            print("   • Не все переменные окружения установлены")
        if not results.get('db'):
            print("   • Проблемы с подключением к базе данных")
        if not results.get('field'):
            print("   • Отсутствует поле subscription_expires_at")
        if not results.get('users'):
            print("   • Проблемы с таблицей пользователей")
        print("\n   Исправьте ошибки и запустите диагностику снова.\n")
    
    return all_ok


if __name__ == "__main__":
    success = asyncio.run(run_diagnostics())
    exit(0 if success else 1)
