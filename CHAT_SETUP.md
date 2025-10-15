# Настройка чата с AI

## Обзор системы

Система чата с AI состоит из следующих компонентов:

1. **Telegram Bot** - основной бот для взаимодействия с пользователями
2. **Redis** - хранение истории чатов
3. **RabbitMQ** - очереди для обработки сообщений
4. **LLM Worker** - воркер для обработки запросов через LLM API

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка окружения

1. Скопируйте `env_example.txt` в `.env`
2. Заполните необходимые переменные:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_from_BotFather

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis
REDIS_HOST=5.23.53.246
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
```

## Запуск системы

### 1. Запуск основного бота

```bash
python main.py
```

### 2. Запуск LLM воркера (в отдельном терминале)

```bash
python run_worker.py
```

## Как это работает

1. Пользователь нажимает кнопку "💬 Начать чат"
2. Бот переходит в режим чата и сохраняет состояние в Redis
3. Когда пользователь отправляет сообщение:
   - Сообщение отправляется в очередь RabbitMQ
   - LLM воркер получает сообщение из очереди
   - Воркер получает историю чата из Redis
   - Отправляет запрос к LLM API
   - Сохраняет ответ в Redis
   - Отправляет ответ обратно в бот
   - Бот отправляет ответ пользователю

## Функции чата

- **Начать чат** - переход в режим общения с AI
- **Главное меню** - возврат в основное меню
- **Очистить историю** - удаление истории чата из Redis

## Структура файлов

- `handlers/chat.py` - обработчик чата
- `redis_client.py` - клиент для работы с Redis
- `queue_client.py` - клиент для работы с RabbitMQ
- `llm_worker.py` - воркер для обработки LLM запросов
- `bot_integration.py` - интеграция между воркером и ботом
- `config.py` - конфигурация приложения
- `run_worker.py` - скрипт для запуска воркера

## Требования

- Python 3.8+
- Redis сервер
- RabbitMQ сервер
- PostgreSQL база данных
- OpenAI API ключ (или другой LLM API)
