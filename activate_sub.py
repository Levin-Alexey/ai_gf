"""
Простой скрипт для активации подписки
Использование: python activate_sub.py <telegram_id> <days>
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from database import async_session_maker
from crud import get_user_by_telegram_id
from sqlalchemy import update
from models import User


async def activate_subscription(telegram_id: int, days: int = 30):
    """Активировать подписку для пользователя"""
    async with async_session_maker() as session:
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            print(f"❌ Пользователь с ID {telegram_id} не найден!")
            return
        
        # Устанавливаем дату окончания подписки (timezone-aware)
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        
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
        print(f"⏰ Дней: {days}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python activate_sub.py <telegram_id> [days]")
        print("Пример: python activate_sub.py 782769400 30")
        sys.exit(1)
    
    telegram_id = int(sys.argv[1])
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    asyncio.run(activate_subscription(telegram_id, days))
