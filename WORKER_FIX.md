# 🔧 Исправление проблемы с отключением воркера

## 🔍 Проблема
LLM Worker запускается, подключается ко всем сервисам, но сразу же отключается. В логах видно:

```
INFO:__main__:👂 Начинаем прослушивание запросов из RabbitMQ...
INFO:queue_client:Начинаем прослушивание запросов...
INFO:redis_client:Соединение с Redis закрыто
INFO:queue_client:Соединение с RabbitMQ закрыто
INFO:__main__:LLM Worker остановлен
```

## 🔍 Причина
В новом асинхронном коде `aio-pika` метод `consume_requests` не блокировал выполнение программы. После настройки потребления сообщений функция завершалась, и воркер сразу отключался.

## ✅ Решение

### 1. **queue_client.py**
Добавлен бесконечный цикл в метод `consume_requests`:

```python
async def consume_requests(self, callback):
    # ... настройка потребления ...
    
    # Бесконечный цикл для поддержания работы воркера
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Получен сигнал остановки потребления")
        # Останавливаем потребление
        if hasattr(self, '_consumer_tag') and self._consumer_tag:
            await queue.cancel(self._consumer_tag)
```

### 2. **llm_worker.py**
Улучшена обработка сигналов остановки:

```python
async def start(self):
    # ... инициализация ...
    
    try:
        await queue_client.consume_requests(self.handle_llm_request)
    except asyncio.CancelledError:
        logger.info("Получен сигнал остановки воркера")
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания (Ctrl+C)")
```

### 3. **Правильная остановка**
Добавлен метод `stop_consuming` для корректной остановки потребления сообщений.

## 🚀 Установка исправлений

### На VDS:
```bash
cd /root/ai_gf
source venv/bin/activate

# Обновите файлы queue_client.py и llm_worker.py
# (используйте git pull или скопируйте обновленные файлы)

# Перезапустите воркер
sudo systemctl restart ai-gf-worker
sudo systemctl status ai-gf-worker
```

### Проверка логов:
```bash
# Следите за логами в реальном времени
journalctl -u ai-gf-worker -f

# Или проверьте последние логи
journalctl -u ai-gf-worker --since "5 minutes ago"
```

## 📊 Ожидаемый результат

После исправлений воркер должен:

1. ✅ Запуститься и подключиться ко всем сервисам
2. ✅ Начать прослушивание RabbitMQ
3. ✅ **НЕ отключаться** сразу после запуска
4. ✅ Оставаться в режиме ожидания сообщений
5. ✅ Обрабатывать сообщения из очереди
6. ✅ Корректно останавливаться по сигналу

## 🧪 Тестирование

### 1. Проверьте статус сервиса:
```bash
sudo systemctl status ai-gf-worker
```

### 2. Отправьте тестовое сообщение:
```bash
python test_rabbitmq.py
```

### 3. Проверьте логи:
```bash
journalctl -u ai-gf-worker --since "1 minute ago"
```

## 📝 Дополнительно

Если воркер все еще отключается:

1. **Проверьте конфигурацию** в `.env`:
   ```
   RABBITMQ_HOST=5.23.53.246
   RABBITMQ_PORT=5672
   RABBITMQ_USER=admin
   RABBITMQ_PASSWORD=ваш_пароль
   ```

2. **Проверьте доступность RabbitMQ**:
   ```bash
   python test_rabbitmq.py
   ```

3. **Запустите воркер вручную** для отладки:
   ```bash
   cd /root/ai_gf
   source venv/bin/activate
   python run_worker.py
   ```

## 🎯 Результат

После применения исправлений воркер будет работать стабильно и обрабатывать сообщения из RabbitMQ без преждевременного отключения.
