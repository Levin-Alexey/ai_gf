# 💎 Система подписок и лимитов сообщений

## 📋 Описание

Реализована система лимитов для бесплатных пользователей и безлимитного общения для подписчиков.

## ✨ Возможности

### Для пользователей БЕЗ подписки:
- ✅ **5 сообщений в сутки** бесплатно
- ⚠️ Предупреждение при остатке 2 сообщений и менее
- 🚫 Блокировка после 5-го сообщения с предложением подписки
- 🔄 Автоматический сброс лимита каждые 24 часа (UTC)

### Для пользователей С подпиской:
- ♾️ **Безлимитные сообщения**
- 🎭 Доступ ко всем персонажам
- ⚡ Приоритетная обработка

## 🏗️ Архитектура

### 1. База данных (PostgreSQL)
```sql
-- Таблица users
ALTER TABLE users 
ADD COLUMN subscription_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Индекс для быстрой проверки
CREATE INDEX idx_users_subscription ON users(subscription_expires_at) 
WHERE subscription_expires_at IS NOT NULL;
```

**Логика:**
- `NULL` → нет подписки
- Прошедшая дата → подписка истекла
- Будущая дата → активная подписка

### 2. Redis (счётчик сообщений)
```
Ключ: msg_limit:{telegram_id}:{YYYY-MM-DD}
Значение: количество отправленных сообщений (int)
TTL: 86400 секунд (24 часа)

Пример:
msg_limit:782769400:2025-10-22 → 3 (TTL: 18ч)
```

**Преимущества Redis:**
- ⚡ Скорость: ~1ms на операцию
- 🕒 TTL из коробки (автоматический сброс)
- 💪 Атомарность операций `INCR`

### 3. Поток данных

```
Пользователь отправляет сообщение
    ↓
handlers/chat.py → handle_chat_message()
    ↓
utils.check_message_limit(redis, user)
    ↓
Проверка подписки в БД ──→ Есть? → Безлимит ✅
    ↓ Нет
Redis: INCR msg_limit:{user_id}:{date}
    ↓
Проверка: count > 5? ──→ Да → Блокировка ❌
    ↓ Нет
Сообщение отправляется в RabbitMQ → LLM ✅
```

## 📁 Изменённые файлы

### models.py
```python
class User(Base):
    # ...
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None
    )
```

### utils.py
Новые функции:
- `check_message_limit(redis, user, daily_limit=5)` - проверка лимита
- `get_subscription_status(user)` - статус подписки

### redis_client.py
Новые методы:
- `incr(key)` - инкремент счётчика
- `expire(key, seconds)` - установка TTL

### handlers/chat.py
Интеграция проверки лимита в `handle_chat_message()`:
```python
# Проверяем лимит
can_send, messages_left = await check_message_limit(redis_client, user)

if not can_send:
    # Показать предложение подписки
    return

# Предупреждение при малом остатке
if 0 <= messages_left <= 2:
    await message.answer(f"⚠️ Осталось сообщений: {messages_left}")
```

### handlers/payment.py (НОВЫЙ)
Обработчики подписки:
- `handle_pay_button()` - показ тарифов
- `handle_subscribe()` - выбор тарифа (пока заглушка)
- `handle_cancel_payment()` - отмена оплаты

## 🧪 Тестирование

### Тест лимитов
```bash
python test_message_limit.py
```

**Результаты:**
✅ Без подписки: 5 сообщений → блокировка  
✅ С активной подпиской: безлимит  
✅ С истёкшей подпиской: возврат к лимиту 5  

### Тест в боте
1. Отправить 5 сообщений без подписки
2. На 6-м сообщении появится кнопка "💳 Оформить подписку"
3. Нажать кнопку → увидеть тарифы
4. Выбрать тариф → увидеть инструкцию для оплаты

## 💳 Тарифы подписки

| Период | Цена | Экономия |
|--------|------|----------|
| 1 месяц | 299₽ | - |
| 3 месяца | 699₽ | -22% |
| 1 год | 1999₽ | -44% |

## 🔧 TODO: Интеграция платежей

Для полноценной работы подписок необходимо:

1. **Выбрать платёжную систему:**
   - ЮKassa (Россия)
   - Stripe (международные)
   - Telegram Stars (криптовалюта)

2. **Реализовать в handlers/payment.py:**
   ```python
   # Создание платежа
   payment_link = await payment_provider.create_payment(
       amount=plan['price'],
       description=f"Подписка {plan['name']}"
   )
   
   # Webhook для подтверждения оплаты
   @router.post("/payment/webhook")
   async def payment_webhook(request):
       # Активация подписки
       user.subscription_expires_at = now + timedelta(days=plan['days'])
       await session.commit()
   ```

3. **Добавить в БД:**
   ```sql
   -- Таблица истории платежей
   CREATE TABLE payments (
       id BIGSERIAL PRIMARY KEY,
       user_id BIGINT REFERENCES users(id),
       amount DECIMAL(10,2),
       plan VARCHAR(10),
       status VARCHAR(20),
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

## 📊 Метрики и аналитика

### Текущие возможности
- ✅ Счётчик сообщений в Redis (TTL 24ч)
- ✅ Статус подписки в БД
- ✅ Логи событий (лимит достигнут, подписка открыта)

### Будущие метрики
- 📈 Конверсия в подписку (сколько пользователей купили после лимита)
- 💰 Средний чек подписки
- 🔄 Retention подписчиков (продления)
- 📊 Популярность тарифов

## 🚀 Запуск

### Применить миграцию БД
```bash
python apply_subscription_migration.py
```

### Запустить бота
```bash
python main.py
```

### Запустить воркера
```bash
python llm_worker.py
```

## 🎯 Примеры использования

### Активировать подписку вручную (для тестирования)
```python
from datetime import datetime, timedelta
from database import async_session_maker
from crud import get_user_by_telegram_id

async with async_session_maker() as session:
    user = await get_user_by_telegram_id(session, 782769400)
    user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
    await session.commit()
    print(f"✅ Подписка активирована до {user.subscription_expires_at}")
```

### Проверить статус подписки
```python
from utils import get_subscription_status

status = await get_subscription_status(user)
print(f"Подписка: {status['has_subscription']}")
print(f"Осталось дней: {status['days_left']}")
```

### Очистить счётчик сообщений (для тестирования)
```python
from redis_client import redis_client
from datetime import datetime

today = datetime.utcnow().date().isoformat()
key = f"msg_limit:782769400:{today}"
await redis_client.redis.delete(key)
print("✅ Счётчик сброшен")
```

## 📝 Логи

### Успешная отправка сообщения
```
INFO - Сообщение пользователя 782769400 отправлено в очередь
```

### Достижение лимита
```
INFO - Пользователь 782769400 достиг лимита сообщений
```

### Открытие меню подписки
```
INFO - Пользователь 782769400 открыл меню подписки
```

### Выбор тарифа
```
INFO - Пользователь 782769400 выбрал тариф 1m
```

---

## 🎉 Итого

Реализована полноценная система монетизации через подписки:
- ✅ Лимиты для бесплатных пользователей
- ✅ Безлимит для подписчиков
- ✅ UI для оформления подписки
- ✅ Гибкая тарифная сетка
- ⚙️ Заготовка для интеграции платежей

**Следующий шаг:** Интеграция платёжной системы (ЮKassa/Stripe/Stars)
