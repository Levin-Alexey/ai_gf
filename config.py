"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')

# Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

# LLM API
LLM_API_URL = os.getenv('LLM_API_URL', 
                       'https://openrouter.ai/api/v1/chat/completions')
LLM_API_KEY = os.getenv('OPENROUTER_API_KEY') or os.getenv('LLM_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'openai/gpt-3.5-turbo')

# Настройки чата
CHAT_HISTORY_LIMIT = 50  # Максимальное количество сообщений в истории
CHAT_TIMEOUT = 300  # Таймаут чата в секундах (5 минут)

# Настройки векторного поиска
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vector_db')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
VECTOR_SEARCH_LIMIT = int(os.getenv('VECTOR_SEARCH_LIMIT', 10))
VECTOR_SIMILARITY_THRESHOLD = float(os.getenv('VECTOR_SIMILARITY_THRESHOLD', 0.7))

# Настройки для распределенной архитектуры
WORKER_SERVER = os.getenv('WORKER_SERVER', 'localhost')  # IP сервера воркера
BOT_SERVER = os.getenv('BOT_SERVER', 'localhost')        # IP сервера бота

# ЮKassa (платежная система)
PAYMENT_SHOP_ID = os.getenv('PAYMENT_SHOP_ID')
PAYMENT_SECRET_KEY = os.getenv('PAYMENT_SECRET_KEY')
PAYMENT_RETURN_URL = os.getenv('PAYMENT_RETURN_URL', 'https://t.me/MyGirlfriend_AI_bot')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # URL вашего сервера для webhook
YOOKASSA_WEBHOOK_SECRET = os.getenv('YOOKASSA_WEBHOOK_SECRET', '')

# Реквизиты для чека (если включена фискализация в YooKassa)
# Должен быть указан либо email, либо phone покупателя.
# Можно задать в .env: PAYMENT_RECEIPT_EMAIL=user@example.com или PAYMENT_RECEIPT_PHONE=+79991234567
PAYMENT_RECEIPT_EMAIL = os.getenv('PAYMENT_RECEIPT_EMAIL', '')
PAYMENT_RECEIPT_PHONE = os.getenv('PAYMENT_RECEIPT_PHONE', '')

# Настройки безопасности webhook
# Можно отключить проверку подписи ЮKassa (НЕ рекомендуется в проде)
YOOKASSA_DISABLE_SIGNATURE_CHECK = (
    os.getenv('YOOKASSA_DISABLE_SIGNATURE_CHECK', 'false')
    .lower() in ('1', 'true', 'yes', 'y')
)
