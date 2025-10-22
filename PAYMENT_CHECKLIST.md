# ✅ Чеклист запуска системы платежей

## 📋 Перед запуском проверьте:

### 1. Зависимости
- [ ] Установлен `yookassa==3.3.0`
- [ ] Установлен `fastapi==0.115.4`
- [ ] Установлен `uvicorn[standard]==0.32.0`
- [ ] Установлен `pydantic==2.9.2`

**Установка:**
```bash
.\install_payment_deps.bat
```

---

### 2. Конфигурация (.env)
- [ ] `PAYMENT_SHOP_ID=1181697` ✅
- [ ] `PAYMENT_SECRET_KEY=live_Ee4j3...` ✅
- [ ] `WEBHOOK_URL=http://ваш-ip:8000/webhook/yookassa` ⚠️ **ДОБАВИТЬ!**

---

### 3. База данных
- [ ] Поле `subscription_expires_at` создано
- [ ] Индекс `idx_users_subscription` создан

**Применить миграцию:**
```bash
python apply_subscription_migration.py
```

---

### 4. Сервер
- [ ] Порт 8000 открыт в firewall
- [ ] Webhook сервер запускается без ошибок

**Проверка порта:**
```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

**Запуск webhook:**
```bash
python webhook_server.py
```

**Проверка работы:**
```bash
curl http://localhost:8000/health
```

---

### 5. ЮKassa
- [ ] Webhook URL добавлен в ЮKassa
- [ ] События `payment.succeeded` и `payment.canceled` выбраны
- [ ] Тестовый магазин активен

**Настройка:**
1. https://yookassa.ru/my/shop-settings
2. HTTP-уведомления
3. Добавить URL: **`https://pay.aigirlfriendbot.ru/webhook/yookassa`** ⚠️
4. Выбрать события:
   - ✅ `payment.succeeded`
   - ✅ `payment.canceled`
5. ЮKassa отправит тестовый запрос для проверки

---

### 6. Тестирование
- [ ] `test_payment_system.py` проходит все тесты
- [ ] Можно создать тестовый платёж
- [ ] Webhook получает уведомления

**Запуск тестов:**
```bash
python test_payment_system.py
```

---

## 🚀 Порядок запуска

### Production (systemd):
```bash
sudo systemctl start ai-gf-bot
sudo systemctl start ai-gf-webhook
```

### Разработка (вручную):
```bash
# Терминал 1
python main.py

# Терминал 2
python webhook_server.py
```

---

## ✅ После запуска проверьте:

### 1. Webhook работает
```bash
curl http://localhost:8000/health
# Ожидается: {"status":"healthy","timestamp":"..."}
```

### 2. Лимиты работают
```bash
python test_message_limit.py
# Ожидается: 5 сообщений ✅, 6-е ❌
```

### 3. Платёж работает
1. В боте отправить 6 сообщений
2. Нажать "💳 Оформить подписку"
3. Выбрать тариф
4. Оплатить тестовой картой: `5555 5555 5555 4444`

### 4. Webhook получает уведомления
Проверить логи:
```bash
# В консоли webhook сервера должно быть:
INFO - 📨 Получено уведомление: payment.succeeded
INFO - ✅ Подписка активирована для {telegram_id}
```

### 5. Подписка активировалась
```bash
python activate_sub.py 782769400 30
# Ожидается: ✅ Подписка активирована!
```

---

## 🎯 Всё готово, если:

- ✅ Все тесты проходят
- ✅ Webhook отвечает на `/health`
- ✅ Можно создать платёж в боте
- ✅ Webhook получает уведомления от ЮKassa
- ✅ Подписка активируется автоматически
- ✅ Лимит снимается после оплаты

---

## 📞 Помощь

**Проблемы?** Смотрите документацию:
- `PAYMENT_QUICKSTART.md` - быстрый старт
- `YOOKASSA_SETUP.md` - детальная настройка
- `PAYMENT_SUMMARY.md` - общая сводка
