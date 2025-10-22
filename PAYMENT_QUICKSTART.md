# 🚀 Быстрый старт системы платежей

## ✅ Что уже готово

1. ✅ **Модели БД** - поле `subscription_expires_at` в таблице `users`
2. ✅ **Система лимитов** - 5 сообщений/день для бесплатных пользователей
3. ✅ **Webhook сервер** - `webhook_server.py` для приёма уведомлений от ЮKassa
4. ✅ **Обработчики оплаты** - `handlers/payment.py` с интеграцией ЮKassa API
5. ✅ **Конфигурация** - ЮKassa ключи в `.env`

---

## 📝 Шаги для запуска

### 1️⃣ Установить зависимости (если ещё не установлены)

**Windows:**
```bash
.\install_payment_deps.bat
```

**Или вручную:**
```bash
.\venv\Scripts\pip.exe install yookassa==3.3.0
.\venv\Scripts\pip.exe install fastapi==0.115.4
.\venv\Scripts\pip.exe install uvicorn[standard]==0.32.0
.\venv\Scripts\pip.exe install pydantic==2.9.2
```

---

### 2️⃣ Добавить WEBHOOK_URL в .env

Откройте `.env` и добавьте:
```env
WEBHOOK_URL=http://ваш-сервер-ip:8000/webhook/yookassa
```

⚠️ **Замените `ваш-сервер-ip` на реальный IP/домен!**

Пример:
```env
WEBHOOK_URL=http://72.56.69.63:8000/webhook/yookassa
```

---

### 3️⃣ Открыть порт 8000 на сервере

**Ubuntu/Debian:**
```bash
sudo ufw allow 8000/tcp
```

**Проверка:**
```bash
sudo ufw status
```

---

### 4️⃣ Запустить webhook сервер

**Локально (для теста):**
```bash
.\venv\Scripts\python.exe webhook_server.py
```

**Проверка работы:**
```bash
curl http://localhost:8000/health
```

Должно вернуть:
```json
{"status":"healthy","timestamp":"2025-10-22T..."}
```

---

### 5️⃣ Настроить webhook в ЮKassa

1. Войдите: https://yookassa.ru/my/shop-settings
2. Найдите **"HTTP-уведомления"**
3. Добавьте URL: `http://ваш-сервер:8000/webhook/yookassa`
4. Выберите события:
   - ✅ `payment.succeeded`
   - ✅ `payment.canceled`
5. Сохраните

---

### 6️⃣ Протестировать платёж

**В боте:**
1. `/start`
2. "💬 Начать чат"
3. Отправьте 6 сообщений (превысите лимит)
4. Нажмите "💳 Оформить подписку"
5. Выберите тариф
6. Оплатите тестовой картой:
   - **Номер:** 5555 5555 5555 4444
   - **Срок:** 12/24
   - **CVC:** 123

**После оплаты:**
- Webhook получит уведомление
- Подписка активируется автоматически
- Лимит снимется (безлимит)

---

### 7️⃣ Проверить логи

**Webhook сервер (в консоли):**
```
INFO - 📨 Получено уведомление: payment.succeeded
INFO - ✅ Подписка активирована для 782769400 на 30 дней
```

**Проверить подписку в БД:**
```bash
.\venv\Scripts\python.exe -c "import asyncio; from database import async_session_maker; from crud import get_user_by_telegram_id; async def check(): async with async_session_maker() as s: u = await get_user_by_telegram_id(s, 782769400); print(f'Подписка до: {u.subscription_expires_at}'); asyncio.run(check())"
```

---

## 🔥 Production запуск (на сервере)

### Создать systemd сервисы

**`/etc/systemd/system/ai-gf-webhook.service`:**
```ini
[Unit]
Description=AI GF Payment Webhook
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/AI_GF
ExecStart=/path/to/AI_GF/venv/bin/python webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Запуск:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-gf-webhook
sudo systemctl start ai-gf-webhook
sudo systemctl status ai-gf-webhook
```

---

## 🧪 Тестовый webhook (без оплаты)

Для разработки можно активировать подписку напрямую:

```bash
curl -X POST http://localhost:8000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 782769400, "days": 30}'
```

⚠️ **Этот endpoint НЕ проверяет подпись! Отключите в production!**

---

## 📊 Мониторинг

### Проверка webhook сервера
```bash
curl http://localhost:8000/health
```

### Логи в реальном времени
```bash
# На сервере
sudo journalctl -u ai-gf-webhook -f

# Локально
python webhook_server.py  # смотрите консоль
```

---

## ⚠️ Важные моменты

### Безопасность
- ✅ Webhook **обязательно** проверяет подпись
- ✅ Секретный ключ хранится в `.env` (не коммитить в git!)
- ✅ Для production используйте HTTPS (nginx + SSL)

### Порты
- **8000** - webhook сервер (нужно открыть в firewall)
- **80/443** - nginx (если используете HTTPS)

### Одновременный запуск
- ✅ **Бот** и **webhook** могут работать одновременно
- ✅ Используют **разные порты** (нет конфликта)
- ✅ Можно запустить на одном сервере

---

## 📚 Документация

- **Полная инструкция:** `YOOKASSA_SETUP.md`
- **Система подписок:** `SUBSCRIPTION_SYSTEM.md`
- **ЮKassa API:** https://yookassa.ru/developers/api

---

## 🎯 Checklist

Перед запуском убедитесь:

- [ ] Установлены зависимости (yookassa, fastapi, uvicorn)
- [ ] Добавлен `WEBHOOK_URL` в `.env`
- [ ] Открыт порт 8000 на сервере
- [ ] Запущен webhook сервер (`python webhook_server.py`)
- [ ] Настроен webhook в ЮKassa личном кабинете
- [ ] Протестирован тестовый платёж
- [ ] Проверены логи webhook сервера

---

## ✨ Всё готово!

Теперь система платежей полностью работает:
1. Пользователь превышает лимит → видит кнопку подписки
2. Выбирает тариф → переходит к оплате ЮKassa
3. Оплачивает → webhook активирует подписку автоматически
4. Получает безлимит! 🎉

**Вопросы?** Смотрите `YOOKASSA_SETUP.md` 📖
