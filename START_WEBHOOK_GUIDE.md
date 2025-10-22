# 🚀 Быстрый запуск Webhook сервера

## Вариант 1: Ручной запуск (для тестирования)

```bash
cd /root/ai_gf
chmod +x start_webhook.sh
./start_webhook.sh
```

Сервер запустится в текущем терминале. Для остановки нажмите `Ctrl+C`.

---

## Вариант 2: Systemd service (для production)

### Шаг 1: Автоматическая установка сервиса

```bash
cd /root/ai_gf
chmod +x install_webhook_service.sh
./install_webhook_service.sh
```

Скрипт автоматически:
- ✅ Скопирует service файл в `/etc/systemd/system/`
- ✅ Перезагрузит systemd
- ✅ Включит автозапуск
- ✅ Запустит сервис
- ✅ Проверит работу

### Шаг 2: Или вручную

```bash
cd /root/ai_gf

# 1. Копирование service файла (ВАЖНО!)
sudo cp ai-gf-webhook.service /etc/systemd/system/

# 2. Перезагрузка systemd
sudo systemctl daemon-reload

# 3. Включение автозапуска
sudo systemctl enable ai-gf-webhook

# 4. Запуск сервиса
sudo systemctl start ai-gf-webhook

# 5. Проверка статуса
sudo systemctl status ai-gf-webhook
```

Должно быть: `Active: active (running)`

---

## ✅ Проверка работы

```bash
# Локальная проверка
curl http://localhost:8000/health

# Внешняя проверка (если nginx настроен)
curl https://pay.aigirlfriendbot.ru/health
```

Ожидается: `{"status":"healthy","timestamp":"..."}`

---

## 📊 Полезные команды

### Просмотр логов
```bash
# В реальном времени
sudo journalctl -u ai-gf-webhook -f

# Последние 50 строк
sudo journalctl -u ai-gf-webhook -n 50

# С определённой даты
sudo journalctl -u ai-gf-webhook --since "2025-01-20"
```

### Управление сервисом
```bash
# Запуск
sudo systemctl start ai-gf-webhook

# Остановка
sudo systemctl stop ai-gf-webhook

# Перезапуск
sudo systemctl restart ai-gf-webhook

# Статус
sudo systemctl status ai-gf-webhook

# Отключить автозапуск
sudo systemctl disable ai-gf-webhook
```

---

## 🔧 Если что-то не работает

### 1. Сервис не запускается
```bash
# Проверить ошибки
sudo journalctl -u ai-gf-webhook -n 50

# Проверить файл сервиса
sudo systemctl cat ai-gf-webhook

# Проверить синтаксис
sudo systemctl daemon-reload
sudo systemctl status ai-gf-webhook
```

### 2. Порт 8000 занят
```bash
# Найти процесс на порту 8000
sudo lsof -i :8000

# Убить процесс (замените PID)
sudo kill -9 PID
```

### 3. Права доступа
```bash
cd /root/ai_gf
chmod +x webhook_server.py
chmod +x start_webhook.sh
```

### 4. Виртуальное окружение
```bash
cd /root/ai_gf
source venv/bin/activate
pip install yookassa fastapi uvicorn pydantic
```

---

## 🎯 Полная установка с нуля

```bash
cd /root/ai_gf

# 1. Установка зависимостей
source venv/bin/activate
pip install yookassa==3.3.0 fastapi==0.115.4 uvicorn[standard]==0.32.0 pydantic==2.9.2

# 2. Проверка конфигурации
python test_payment_system.py

# 3. Установка сервиса
sudo cp ai-gf-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-gf-webhook
sudo systemctl start ai-gf-webhook

# 4. Проверка
sudo systemctl status ai-gf-webhook
curl http://localhost:8000/health
```

---

## 📝 Что дальше?

После запуска webhook сервера:

1. **Настройте nginx** (если ещё не настроен):
   ```bash
   # Смотрите NGINX_SETUP.md
   ```

2. **Добавьте webhook в ЮKassa**:
   - URL: `https://pay.aigirlfriendbot.ru/webhook/yookassa`
   - События: `payment.succeeded`, `payment.canceled`

3. **Протестируйте платёж**:
   - В боте отправьте 6 сообщений
   - Нажмите "Оформить подписку"
   - Оплатите тестовой картой: `5555 5555 5555 4444`

4. **Проверьте логи**:
   ```bash
   sudo journalctl -u ai-gf-webhook -f
   ```

---

**Готово! Webhook сервер работает!** 🎉
