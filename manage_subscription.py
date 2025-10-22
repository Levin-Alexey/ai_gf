"""
Скрипт для ручной активации подписки (для тестирования)
"""
import asyncio
from datetime import datetime, timedelta
from database import async_session_maker
from crud import get_user_by_telegram_id
from sqlalchemy import update
from models import User


async def activate_subscription(telegram_id: int, days: int = 30):
    """
    Активировать подписку для пользователя
    
    Args:
        telegram_id: Telegram ID пользователя
        days: Количество дней подписки (по умолчанию 30)
    """
    async with async_session_maker() as session:
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            print(f"❌ Пользователь с ID {telegram_id} не найден!")
            return
        
        # Устанавливаем дату окончания подписки
        expires_at = datetime.utcnow() + timedelta(days=days)
        
        # Обновляем пользователя
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(subscription_expires_at=expires_at)
        )
        await session.execute(stmt)
        await session.commit()
        
        print(f"✅ Подписка активирована!")
        print(f"👤 Пользователь: {user.get_display_name()}")
        print(f"📧 Telegram ID: {telegram_id}")
        print(f"📅 Активна до: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"⏰ Дней осталось: {days}")


async def deactivate_subscription(telegram_id: int):
    """
    Деактивировать подписку для пользователя
    
    Args:
        telegram_id: Telegram ID пользователя
    """
    async with async_session_maker() as session:
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            print(f"❌ Пользователь с ID {telegram_id} не найден!")
            return
        
        # Удаляем подписку
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(subscription_expires_at=None)
        )
        await session.execute(stmt)
        await session.commit()
        
        print(f"✅ Подписка деактивирована!")
        print(f"👤 Пользователь: {user.get_display_name()}")
        print(f"📧 Telegram ID: {telegram_id}")


async def main():
    """Главная функция с меню"""
    print("=" * 50)
    print("💎 УПРАВЛЕНИЕ ПОДПИСКАМИ")
    print("=" * 50)
    print()
    print("1. Активировать подписку (30 дней)")
    print("2. Активировать подписку (90 дней)")
    print("3. Активировать подписку (365 дней)")
    print("4. Деактивировать подписку")
    print("5. Выход")
    print()
    
    choice = input("Выберите действие (1-5): ").strip()
    
    if choice == "5":
        print("👋 До свидания!")
        return
    
    telegram_id = input("Введите Telegram ID пользователя: ").strip()
    
    try:
        telegram_id = int(telegram_id)
    except ValueError:
        print("❌ Неверный формат Telegram ID!")
        return
    
    if choice == "1":
        await activate_subscription(telegram_id, days=30)
    elif choice == "2":
        await activate_subscription(telegram_id, days=90)
    elif choice == "3":
        await activate_subscription(telegram_id, days=365)
    elif choice == "4":
        await deactivate_subscription(telegram_id)
    else:
        print("❌ Неверный выбор!")


if __name__ == '__main__':
    asyncio.run(main())
