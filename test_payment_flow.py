"""
Тест полного цикла оплаты:
1. Создание платежа
2. Проверка webhook
3. Активация подписки
"""
import asyncio
import sys
from datetime import datetime, timezone

from database import async_session_maker
from sqlalchemy import select
from models import User


async def test_payment_flow(telegram_id: int):
    """Тестирование полного цикла оплаты"""
    
    print("=" * 60)
    print("🧪 ТЕСТ ПЛАТЁЖНОЙ СИСТЕМЫ")
    print("=" * 60)
    print()
    
    async with async_session_maker() as session:
        # 1. Проверяем пользователя
        print(f"1️⃣ Проверка пользователя {telegram_id}...")
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"   ❌ Пользователь {telegram_id} не найден в базе")
            print(f"   💡 Сначала отправьте /start боту")
            return
        
        print(f"   ✅ Пользователь найден: {user.username or user.first_name}")
        print()
        
        # 2. Проверяем текущую подписку
        print("2️⃣ Проверка текущей подписки...")
        if user.subscription_expires_at:
            now = datetime.now(timezone.utc)
            if user.subscription_expires_at > now:
                days_left = (user.subscription_expires_at - now).days
                print(f"   ✅ Подписка активна")
                print(f"   📅 Истекает: {user.subscription_expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"   ⏳ Осталось дней: {days_left}")
            else:
                print(f"   ❌ Подписка истекла: {user.subscription_expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            print(f"   ℹ️  Подписки нет")
        print()
        
        # 3. Инструкция по тестированию
        print("3️⃣ КАК ПРОТЕСТИРОВАТЬ ОПЛАТУ:")
        print()
        print("   Шаг 1: Отправьте боту 6 сообщений подряд")
        print("          (лимит 5 сообщений в день)")
        print()
        print("   Шаг 2: На 6-м сообщении появится кнопка:")
        print("          💳 Оформить подписку")
        print()
        print("   Шаг 3: Нажмите кнопку и выберите тариф:")
        print("          📅 1 месяц — 10₽ (ТЕСТ)")
        print()
        print("   Шаг 4: Нажмите 'Перейти к оплате'")
        print()
        print("   Шаг 5: Оплатите тестовой картой:")
        print("          Номер: 5555 5555 5555 4444")
        print("          Срок: 12/24")
        print("          CVC: 123")
        print()
        print("   Шаг 6: После оплаты webhook автоматически:")
        print("          • Получит уведомление от ЮKassa")
        print("          • Проверит подпись")
        print("          • Активирует подписку на 30 дней")
        print("          • Сохранит в базе данных")
        print()
        print("   Шаг 7: Проверьте логи webhook:")
        print("          sudo journalctl -u ai-gf-webhook -f")
        print()
        print("   Должно появиться:")
        print("          ✅ Подписка активирована для {telegram_id}")
        print()
        
        # 4. Проверка конфигурации
        print("4️⃣ Проверка конфигурации...")
        
        from config import (
            PAYMENT_SHOP_ID,
            PAYMENT_SECRET_KEY,
            WEBHOOK_URL,
            PAYMENT_RETURN_URL
        )
        
        errors = []
        
        if not PAYMENT_SHOP_ID:
            errors.append("   ❌ PAYMENT_SHOP_ID не настроен")
        else:
            print(f"   ✅ PAYMENT_SHOP_ID: {PAYMENT_SHOP_ID}")
        
        if not PAYMENT_SECRET_KEY:
            errors.append("   ❌ PAYMENT_SECRET_KEY не настроен")
        else:
            print(f"   ✅ PAYMENT_SECRET_KEY: {'*' * 20}")
        
        if not WEBHOOK_URL or "pay.aigirlfriendbot.ru" not in WEBHOOK_URL:
            errors.append("   ❌ WEBHOOK_URL не настроен")
        else:
            print(f"   ✅ WEBHOOK_URL: {WEBHOOK_URL}")
        
        if not PAYMENT_RETURN_URL:
            errors.append("   ❌ PAYMENT_RETURN_URL не настроен")
        else:
            print(f"   ✅ PAYMENT_RETURN_URL: {PAYMENT_RETURN_URL}")
        
        if errors:
            print()
            print("⚠️  ОШИБКИ КОНФИГУРАЦИИ:")
            for error in errors:
                print(error)
            print()
            print("Проверьте файл .env")
            return
        
        print()
        
        # 5. Проверка webhook сервера
        print("5️⃣ Проверка webhook сервера...")
        try:
            import aiohttp
            async with aiohttp.ClientSession() as client:
                async with client.get("https://pay.aigirlfriendbot.ru/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"   ✅ Webhook сервер работает")
                        print(f"   📊 Статус: {data.get('status')}")
                        print(f"   🕐 Timestamp: {data.get('timestamp')}")
                    else:
                        print(f"   ❌ Webhook сервер вернул код {resp.status}")
        except Exception as e:
            print(f"   ⚠️  Не удалось проверить webhook: {e}")
            print(f"   💡 Убедитесь что webhook запущен:")
            print(f"      sudo systemctl status ai-gf-webhook")
        
        print()
        
        # 6. Итог
        print("=" * 60)
        print("📋 ИТОГ:")
        print("=" * 60)
        print()
        print("✅ Всё готово к тестированию!")
        print()
        print("💡 Следуйте инструкции выше для тестирования оплаты")
        print()
        print("📊 После оплаты запустите этот скрипт снова:")
        print(f"   python test_payment_flow.py {telegram_id}")
        print()
        print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python test_payment_flow.py <telegram_id>")
        print("Пример: python test_payment_flow.py 782769400")
        sys.exit(1)
    
    telegram_id = int(sys.argv[1])
    asyncio.run(test_payment_flow(telegram_id))
