# 💎 Система Платежей и Подписок - Для README.md

Добавьте этот раздел в README.md после основных инструкций:

---

## 💳 Система Платежей (ЮKassa)

### Возможности

- 💰 **Платная подписка** через ЮKassa
- 🎁 **Бесплатный тариф**: 5 сообщений/день
- ♾️ **Подписка**: безлимитные сообщения
- 🤖 **Автоматическая активация** через webhook

### Тарифы

| Тариф | Цена | Экономия |
|-------|------|----------|
| 1 месяц | 299₽ | - |
| 3 месяца | 699₽ | -22% |
| 1 год | 1999₽ | -44% |

### Быстрый старт

**1. Установить зависимости:**
```bash
.\install_payment_deps.bat
```

**2. Настроить .env:**
```env
PAYMENT_SHOP_ID=ваш_shop_id
PAYMENT_SECRET_KEY=ваш_secret_key
WEBHOOK_URL=http://ваш-сервер:8000/webhook/yookassa
```

**3. Применить миграцию БД:**
```bash
python apply_subscription_migration.py
```

**4. Запустить webhook сервер:**
```bash
python webhook_server.py  # Порт 8000
```

**5. Настроить webhook в ЮKassa:**
- URL: `http://ваш-сервер:8000/webhook/yookassa`
- События: `payment.succeeded`, `payment.canceled`
- https://yookassa.ru/my/shop-settings

### Документация

- 📖 **Быстрый старт:** `PAYMENT_QUICKSTART.md`
- 🔧 **Настройка ЮKassa:** `YOOKASSA_SETUP.md`
- 📊 **Система подписок:** `SUBSCRIPTION_SYSTEM.md`
- ✅ **Чеклист:** `PAYMENT_CHECKLIST.md`

### Тестирование

```bash
# Проверка системы
python test_payment_system.py

# Ручная активация (для теста)
python activate_sub.py 782769400 30
```

---
