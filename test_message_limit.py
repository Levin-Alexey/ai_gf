"""
Тест системы лимитов сообщений
"""
import asyncio
from datetime import datetime, timedelta
from redis_client import redis_client
from database import async_session_maker
from crud import get_user_by_telegram_id
from utils import check_message_limit, get_subscription_status


async def test_limits():
    """Тестируем систему лимитов"""
    
    # Подключаемся к Redis
    await redis_client.connect()
    
    # Получаем реального пользователя из БД
    async with async_session_maker() as session:
        # Используем существующего пользователя (ID 782769400 из истории)
        user = await get_user_by_telegram_id(session, 782769400)
        
        if not user:
            print("❌ Пользователь не найден!")
            return
        
        print(f"👤 Тестируем пользователя: {user.get_display_name()}")
        print(f"📧 Telegram ID: {user.telegram_id}")
        
        # 1. Проверяем статус подписки
        print("\n📊 Статус подписки:")
        sub_status = await get_subscription_status(user)
        print(f"   Есть подписка: {sub_status['has_subscription']}")
        print(f"   Истекает: {sub_status['expires_at']}")
        print(f"   Дней осталось: {sub_status['days_left']}")
        
        # 2. Тестируем лимиты без подписки
        print("\n🧪 Тест 1: Проверка лимитов БЕЗ подписки")
        for i in range(7):
            can_send, left = await check_message_limit(redis_client, user)
            status = "✅" if can_send else "❌"
            print(f"   Сообщение {i+1}: {status} (осталось: {left})")
        
        # 3. Симулируем активную подписку
        print("\n🧪 Тест 2: Проверка с АКТИВНОЙ подпиской")
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        for i in range(3):
            can_send, left = await check_message_limit(redis_client, user)
            status = "✅" if can_send else "❌"
            limit_str = "безлимит" if left == -1 else f"осталось: {left}"
            print(f"   Сообщение {i+1}: {status} ({limit_str})")
        
        # 4. Симулируем истёкшую подписку
        print("\n🧪 Тест 3: Проверка с ИСТЁКШЕЙ подпиской")
        user.subscription_expires_at = datetime.utcnow() - timedelta(days=1)
        can_send, left = await check_message_limit(redis_client, user)
        status = "✅" if can_send else "❌"
        print(f"   Первое сообщение: {status} (осталось: {left})")
        
    # Отключаемся
    await redis_client.disconnect()
    print("\n✅ Тест завершён!")


if __name__ == '__main__':
    asyncio.run(test_limits())
