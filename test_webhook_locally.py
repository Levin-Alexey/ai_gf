"""
Скрипт для локального тестирования webhook обработки платежей
"""
import asyncio
import sys
from datetime import datetime, timezone

from database import async_session_maker
from sqlalchemy import select
from models import User


async def test_activate_subscription(telegram_id: int, days: int = 30):
    """
    Тестирование активации подписки
    """
    print(f"\n{'='*60}")
    print(f"🧪 ТЕСТ: Активация подписки для пользователя {telegram_id}")
    print(f"{'='*60}\n")
    
    try:
        # Проверяем пользователя ДО активации
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user_before = result.scalar_one_or_none()
            
            if not user_before:
                print(f"❌ Пользователь {telegram_id} НЕ НАЙДЕН в базе данных!")
                print("   Сначала пользователь должен запустить бота командой /start")
                return False
            
            print(f"✅ Пользователь найден:")
            print(f"   ID: {user_before.id}")
            print(f"   Telegram ID: {user_before.telegram_id}")
            print(f"   Имя: {user_before.get_display_name()}")
            print(f"   Подписка ДО: {user_before.subscription_expires_at}")
        
        # Активируем подписку
        print(f"\n⏳ Активация подписки на {days} дней...")
        
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            now_utc = datetime.now(timezone.utc)
            from datetime import timedelta
            
            base = user.subscription_expires_at if (
                user.subscription_expires_at and user.subscription_expires_at > now_utc
            ) else now_utc
            expires_at = base + timedelta(days=days)
            
            user.subscription_expires_at = expires_at
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"✅ Подписка успешно активирована!")
            print(f"   Дата окончания: {expires_at}")
        
        # Проверяем результат ПОСЛЕ активации
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user_after = result.scalar_one_or_none()
            
            print(f"\n📊 Результат:")
            print(f"   Подписка ПОСЛЕ: {user_after.subscription_expires_at}")
            
            if user_after.subscription_expires_at:
                now = datetime.now(timezone.utc)
                days_left = (user_after.subscription_expires_at - now).days
                print(f"   Осталось дней: {days_left}")
                
                if user_after.subscription_expires_at > now:
                    print(f"\n✅ ТЕСТ ПРОЙДЕН! Подписка активна!")
                    return True
                else:
                    print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН! Подписка истекла!")
                    return False
            else:
                print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН! Подписка не установлена!")
                return False
                
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_user_status(telegram_id: int):
    """
    Проверка текущего статуса пользователя
    """
    print(f"\n{'='*60}")
    print(f"📋 ПРОВЕРКА: Статус пользователя {telegram_id}")
    print(f"{'='*60}\n")
    
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ Пользователь {telegram_id} НЕ НАЙДЕН")
                return
            
            print(f"✅ Пользователь найден:")
            print(f"   ID в БД: {user.id}")
            print(f"   Telegram ID: {user.telegram_id}")
            print(f"   Username: {user.username or '—'}")
            print(f"   Имя: {user.first_name or '—'}")
            print(f"   Подписка до: {user.subscription_expires_at or '—'}")
            
            if user.subscription_expires_at:
                now = datetime.now(timezone.utc)
                if user.subscription_expires_at > now:
                    days_left = (user.subscription_expires_at - now).days
                    print(f"   ✅ Подписка АКТИВНА (осталось {days_left} дней)")
                else:
                    print(f"   ❌ Подписка ИСТЕКЛА")
            else:
                print(f"   ⚠️ Подписка НЕ АКТИВИРОВАНА")
                
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Главная функция"""
    
    if len(sys.argv) < 2:
        print("❌ Использование:")
        print("   python test_webhook_locally.py <telegram_id> [action]")
        print("\nПримеры:")
        print("   python test_webhook_locally.py 123456789 check")
        print("   python test_webhook_locally.py 123456789 activate")
        print("   python test_webhook_locally.py 123456789 activate 60")
        sys.exit(1)
    
    telegram_id = int(sys.argv[1])
    action = sys.argv[2] if len(sys.argv) > 2 else "check"
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    if action == "check":
        await check_user_status(telegram_id)
    elif action == "activate":
        success = await test_activate_subscription(telegram_id, days)
        if success:
            print("\n✅ Подписка успешно активирована и проверена!")
        else:
            print("\n❌ Не удалось активировать подписку!")
            sys.exit(1)
    else:
        print(f"❌ Неизвестное действие: {action}")
        print("   Доступные действия: check, activate")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
