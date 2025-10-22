# 💳 Интеграция ЮKassa для приёма платежей

## 📋 Описание

Полноценная интеграция с платёжной системой ЮKassa для автоматической активации подписок после оплаты.

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│           Пользователь (Telegram)                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ 1. Выбирает тариф
                  ▼
┌─────────────────────────────────────────────────────┐
│         Бот (handlers/payment.py)                   │
│  • Создаёт платёж через ЮKassa API                  │
│  • Добавляет metadata (telegram_id, days)           │
│  • Отправляет ссылку на оплату                      │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ 2. Создаёт платёж
                  ▼
┌─────────────────────────────────────────────────────┐
│              ЮKassa API                             │
│  • Принимает платёж                                 │
│  • Обрабатывает карту                               │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ 3. Отправляет webhook
                  ▼
┌─────────────────────────────────────────────────────┐
│      Webhook сервер (webhook_server.py)             │
│  • Проверяет подпись                                │
│  • Извлекает metadata                               │
│  • Активирует подписку в БД                         │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ 4. Обновляет subscription_expires_at
                  ▼
┌─────────────────────────────────────────────────────┐
│            PostgreSQL Database                      │
│  users.subscription_expires_at = NOW() + days       │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Установка

### 1. Установить зависимости

**Windows:**
```bash
.\install_payment_deps.bat
```

**Linux/Mac:**
```bash
bash install_payment_deps.sh
```

**Или вручную:**
```bash
pip install yookassa==3.3.0
pip install fastapi==0.115.4
pip install uvicorn[standard]==0.32.0
pip install pydantic==2.9.2
```

---

### 2. Настроить .env

Добавьте (уже есть):
```env
PAYMENT_SHOP_ID=1181697
PAYMENT_SECRET_KEY=live_Ee4j3Lp9erVpLw6YTZSaqj-pEGvAVjGA0ZMi8pSPUog
WEBHOOK_URL=https://your-server.com:8000/webhook/yookassa
```

⚠️ **ВАЖНО:** Замените `your-server.com` на реальный домен или IP вашего сервера!

---

### 3. Настроить webhook в ЮKassa

1. Перейдите в личный кабинет: https://yookassa.ru/my/shop-settings
2. Найдите раздел **"HTTP-уведомления"**
3. Добавьте URL: `https://your-server.com:8000/webhook/yookassa`
4. Выберите события:
   - ✅ `payment.succeeded` (успешный платёж)
   - ✅ `payment.canceled` (отменённый платёж)

---

### 4. Открыть порт 8000

**На сервере:**
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Проверка:**
```bash
curl http://localhost:8000/health
```

Ответ: `{"status":"healthy","timestamp":"..."}`

---

## 🔧 Запуск

### Вариант 1: Вручную (для тестирования)

**Терминал 1 - Бот:**
```bash
python main.py
```

**Терминал 2 - Webhook:**
```bash
python webhook_server.py
```

---

### Вариант 2: Systemd (для production)

Создайте файлы сервисов:

**`/etc/systemd/system/ai-gf-bot.service`:**
```ini
[Unit]
Description=AI GF Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/AI_GF
Environment="PATH=/path/to/AI_GF/venv/bin"
ExecStart=/path/to/AI_GF/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/ai-gf-webhook.service`:**
```ini
[Unit]
Description=AI GF Payment Webhook
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/AI_GF
Environment="PATH=/path/to/AI_GF/venv/bin"
ExecStart=/path/to/AI_GF/venv/bin/python webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Запуск:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-gf-bot ai-gf-webhook
sudo systemctl start ai-gf-bot ai-gf-webhook
```

**Проверка статуса:**
```bash
sudo systemctl status ai-gf-bot
sudo systemctl status ai-gf-webhook
```

**Логи:**
```bash
sudo journalctl -u ai-gf-bot -f
sudo journalctl -u ai-gf-webhook -f
```

---

## 🧪 Тестирование

### 1. Проверка webhook сервера

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{"status":"healthy","timestamp":"2025-10-22T14:30:00+00:00"}
```

---

### 2. Тестовая активация подписки

**Без оплаты (для разработки):**
```bash
curl -X POST http://localhost:8000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 782769400, "days": 30}'
```

Ответ:
```json
{"status":"success","message":"Подписка активирована"}
```

---

### 3. Тестовый платёж в боте

1. Запустите бота: `/start`
2. Нажмите "💬 Начать чат"
3. Отправьте 6 сообщений (превысите лимит)
4. Нажмите "💳 Оформить подписку"
5. Выберите тариф
6. Нажмите "💳 Перейти к оплате"

В **тестовом режиме** ЮKassa используйте карту:
```
Номер: 5555 5555 5555 4444
Срок: 12/24
CVC: 123
```

---

## 📊 Мониторинг

### Логи webhook

```bash
# В реальном времени
tail -f /var/log/ai-gf-webhook.log

# Или через journalctl
sudo journalctl -u ai-gf-webhook -f
```

**Успешный платёж:**
```
INFO - 📨 Получено уведомление: payment.succeeded
INFO - ✅ Подписка активирована для 782769400 на 30 дней до 2025-11-21
INFO - ✅ Платёж обработан для 782769400
```

**Отклонённая подпись:**
```
WARNING - ❌ Невалидная подпись webhook!
```

---

## 🔒 Безопасность

### Проверка подписи webhook

Webhook сервер **обязательно** проверяет подпись каждого запроса от ЮKassa:

```python
def verify_webhook_signature(body: bytes, signature: str) -> bool:
    expected = hmac.new(
        PAYMENT_SECRET_KEY.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

⚠️ **Без валидной подписи запрос отклоняется!**

---

### HTTPS для production

Для продакшена **обязательно** используйте HTTPS:

1. Установите nginx как reverse proxy
2. Получите SSL сертификат (Let's Encrypt)
3. Настройте nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-server.com;
    
    ssl_certificate /etc/letsencrypt/live/your-server.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-server.com/privkey.pem;
    
    location /webhook/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 💰 Тарифы

| Период | Цена | Дней | Скидка |
|--------|------|------|--------|
| 1 месяц | 299₽ | 30 | - |
| 3 месяца | 699₽ | 90 | -22% |
| 1 год | 1999₽ | 365 | -44% |

Тарифы настраиваются в `handlers/payment.py`:

```python
plans = {
    "1m": {"name": "1 месяц", "price": 299, "days": 30},
    "3m": {"name": "3 месяца", "price": 699, "days": 90},
    "1y": {"name": "1 год", "price": 1999, "days": 365}
}
```

---

## 🐛 Troubleshooting

### Проблема: Webhook не получает уведомления

**Решение:**
1. Проверьте, что webhook сервер запущен: `curl http://localhost:8000/health`
2. Проверьте порт 8000: `sudo netstat -tulpn | grep 8000`
3. Проверьте URL в ЮKassa (должен быть HTTPS для production)
4. Проверьте логи: `sudo journalctl -u ai-gf-webhook -f`

---

### Проблема: "Invalid signature"

**Решение:**
1. Проверьте `PAYMENT_SECRET_KEY` в `.env`
2. Убедитесь, что ключ совпадает с ключом в ЮKassa
3. Проверьте, что используется **секретный ключ**, а не публичный

---

### Проблема: Подписка не активируется

**Решение:**
1. Проверьте metadata в платеже (должны быть `telegram_id` и `days`)
2. Проверьте подключение к PostgreSQL
3. Проверьте логи webhook: `sudo journalctl -u ai-gf-webhook -f`

---

### Проблема: Ошибка при создании платежа

**Решение:**
1. Проверьте `PAYMENT_SHOP_ID` и `PAYMENT_SECRET_KEY` в `.env`
2. Убедитесь, что магазин активен в ЮKassa
3. Проверьте баланс магазина (для тестового режима)
4. Проверьте логи бота: `sudo journalctl -u ai-gf-bot -f`

---

## 📚 Полезные ссылки

- **ЮKassa API:** https://yookassa.ru/developers/api
- **Webhook документация:** https://yookassa.ru/developers/using-api/webhooks
- **Личный кабинет:** https://yookassa.ru/my
- **Тестовые карты:** https://yookassa.ru/developers/payment-acceptance/testing-and-going-live/testing

---

## 🎯 Итого

✅ **Полная интеграция с ЮKassa**  
✅ **Автоматическая активация подписок**  
✅ **Безопасная проверка подписей**  
✅ **Готово к production использованию**  
✅ **Systemd сервисы для автозапуска**  

**Следующие шаги:**
1. Установить зависимости: `.\install_payment_deps.bat`
2. Добавить `WEBHOOK_URL` в `.env`
3. Запустить webhook сервер: `python webhook_server.py`
4. Настроить webhook в ЮKassa
5. Протестировать платёж!

🚀 **Готово к приёму денег!** 💰
