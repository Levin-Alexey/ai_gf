# Миграция на aio-pika (Асинхронный RabbitMQ)

## 🔍 Проблема
Ваш код использовал **синхронную** библиотеку `pika` в **асинхронном** коде aiogram. Это блокировало event loop, и сообщения не отправлялись в очередь RabbitMQ.

## ✅ Решение
Код переписан на использование `aio-pika` - асинхронной библиотеки для RabbitMQ, совместимой с asyncio.

## 📝 Что изменено

### 1. **requirements.txt**
   - Заменено: `pika==1.3.2` → `aio-pika==9.4.3`

### 2. **queue_client.py**
   - Весь класс `QueueClient` переписан на асинхронный код
   - Все методы теперь `async`
   - Используется `aio_pika.connect_robust()` вместо `pika.BlockingConnection`

### 3. **main.py**
   - `queue_client.connect()` → `await queue_client.connect()`
   - `queue_client.disconnect()` → `await queue_client.disconnect()`

### 4. **handlers/chat.py**
   - `queue_client.publish_message()` → `await queue_client.publish_message()`

### 5. **llm_worker.py**
   - `queue_client.connect()` → `await queue_client.connect()`
   - `queue_client.disconnect()` → `await queue_client.disconnect()`
   - `queue_client.consume_requests()` → `await queue_client.consume_requests()`
   - `handle_llm_request()` теперь `async`

### 6. Тестовые файлы
   - **test_rabbitmq.py** - переписан на async
   - **test_system.py** - обновлены вызовы queue_client
   - **diagnostics.py** - обновлена функция test_rabbitmq_connection()

## 🚀 Установка

### На VDS (Linux):
```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Удалите старую библиотеку
pip uninstall pika -y

# Установите новую библиотеку
pip install aio-pika==9.4.3

# Или переустановите все зависимости
pip install -r requirements.txt
```

### На Windows:
```cmd
# Активируйте виртуальное окружение
venv\Scripts\activate

# Удалите старую библиотеку
pip uninstall pika -y

# Установите новую библиотеку
pip install aio-pika==9.4.3

# Или переустановите все зависимости
pip install -r requirements.txt
```

## 🧪 Проверка

После установки проверьте работу:

```bash
# Тест RabbitMQ
python test_rabbitmq.py

# Полная диагностика
python diagnostics.py

# Тест всей системы
python test_system.py
```

## 📊 Преимущества

✅ **Нет блокировок** - event loop работает без задержек  
✅ **Автоматическое переподключение** - используется `connect_robust()`  
✅ **Правильная асинхронность** - все операции неблокирующие  
✅ **Лучшая производительность** - параллельная обработка запросов  

## ⚠️ Важно

- Убедитесь, что RabbitMQ сервер запущен и доступен
- Проверьте конфигурацию в `.env` файле:
  ```
  RABBITMQ_HOST=5.23.53.246
  RABBITMQ_PORT=5672
  RABBITMQ_USER=admin
  RABBITMQ_PASSWORD=ваш_пароль
  RABBITMQ_VHOST=/
  ```

## 🎯 Тестирование на VDS

Из вашего лога видно, что RabbitMQ на VDS работает нормально. После установки `aio-pika` все должно заработать:

```bash
# На VDS
cd /root/ai_gf
source venv/bin/activate
pip install aio-pika==9.4.3
python test_rabbitmq.py
```

Если возникнут проблемы, проверьте логи:
```bash
# Запустите бота с подробными логами
python main.py

# Запустите воркера
python run_worker.py
```

## 📚 Дополнительная информация

- [Документация aio-pika](https://aio-pika.readthedocs.io/)
- [Примеры использования](https://github.com/mosquito/aio-pika/tree/master/docs/source/examples)

