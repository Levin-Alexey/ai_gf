# 🏗️ Развертывание AI Girlfriend Bot в распределенной архитектуре

## 🏢 Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐
│   Сервер Бота   │    │ Сервер Воркера  │
│                 │    │                 │
│ • Telegram Bot  │    │ • LLM Worker    │
│ • PostgreSQL    │    │ • ChromaDB      │
│ • Redis         │    │ • Vector DB     │
│ • RabbitMQ      │    │                 │
└─────────────────┘    └─────────────────┘
         │                       │
         └─────── Интернет ──────┘
```

## 🖥️ Сервер 1: Бот + База данных

### **1. Установка:**
```bash
# Клонируем репозиторий
cd /opt
git clone https://github.com/your-username/AI_GF.git
cd AI_GF

# Создаем виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Конфигурация .env:**
```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
BOT_NAME=AI_GF

# Database (локальная)
DATABASE_URL=postgresql+asyncpg://admingf:admingf123!@localhost/gfdb

# Redis (локальная)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ (локальная)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=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
LLM_MODEL=openai/gpt-3.5-turbo

# Распределенная архитектура
WORKER_SERVER=192.168.1.100  # IP сервера воркера
BOT_SERVER=192.168.1.101     # IP сервера бота
```

### **3. Systemd сервис для бота:**
```bash
sudo nano /etc/systemd/system/ai-gf-bot.service
```

```ini
[Unit]
Description=AI Girlfriend Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/AI_GF
Environment=PATH=/opt/AI_GF/venv/bin
ExecStart=/opt/AI_GF/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🖥️ Сервер 2: LLM Воркер

### **1. Установка:**
```bash
# Клонируем репозиторий
cd /opt
git clone https://github.com/your-username/AI_GF.git
cd AI_GF

# Создаем виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Конфигурация .env:**
```env
# Database (удаленная)
DATABASE_URL=postgresql+asyncpg://admingf:admingf123!@192.168.1.101/gfdb

# Redis (удаленная)
REDIS_HOST=192.168.1.101
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ (удаленная)
RABBITMQ_HOST=192.168.1.101
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=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
LLM_MODEL=openai/gpt-3.5-turbo

# Vector Database (локальная на сервере воркера)
VECTOR_DB_PATH=/opt/vector_db
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VECTOR_SEARCH_LIMIT=10
VECTOR_SIMILARITY_THRESHOLD=0.7

# Распределенная архитектура
WORKER_SERVER=192.168.1.100  # IP сервера воркера
BOT_SERVER=192.168.1.101     # IP сервера бота
```

### **3. Создание папки для векторной базы:**
```bash
# Создаем папку для векторной базы
sudo mkdir -p /opt/vector_db
sudo chmod 755 /opt/vector_db
sudo chown root:root /opt/vector_db
```

### **4. Systemd сервис для воркера:**
```bash
sudo nano /etc/systemd/system/ai-gf-worker.service
```

```ini
[Unit]
Description=AI Girlfriend Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/AI_GF
Environment=PATH=/opt/AI_GF/venv/bin
ExecStart=/opt/AI_GF/venv/bin/python run_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🔧 Настройка сетевого доступа

### **На сервере бота (открываем порты):**
```bash
# PostgreSQL
sudo ufw allow from 192.168.1.100 to any port 5432

# Redis
sudo ufw allow from 192.168.1.100 to any port 6379

# RabbitMQ
sudo ufw allow from 192.168.1.100 to any port 5672
```

### **На сервере воркера (открываем порты):**
```bash
# Для мониторинга (опционально)
sudo ufw allow from 192.168.1.101 to any port 22
```

## 🚀 Запуск системы

### **1. На сервере бота:**
```bash
# Обновляем базу данных
psql -h localhost -U admingf -d gfdb -f update_db_memory.sql

# Запускаем бота
sudo systemctl enable ai-gf-bot
sudo systemctl start ai-gf-bot
```

### **2. На сервере воркера:**
```bash
# Запускаем воркер
sudo systemctl enable ai-gf-worker
sudo systemctl start ai-gf-worker
```

## 📊 Мониторинг

### **На сервере бота:**
```bash
# Логи бота
sudo journalctl -u ai-gf-bot -f

# Статус сервисов
sudo systemctl status ai-gf-bot
```

### **На сервере воркера:**
```bash
# Логи воркера
sudo journalctl -u ai-gf-worker -f

# Статус сервисов
sudo systemctl status ai-gf-worker

# Проверка векторной базы
ls -la /opt/vector_db/
```

## 🔄 Обновление системы

### **На обоих серверах:**
```bash
# Останавливаем сервисы
sudo systemctl stop ai-gf-bot    # на сервере бота
sudo systemctl stop ai-gf-worker # на сервере воркера

# Обновляем код
cd /opt/AI_GF
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Запускаем сервисы
sudo systemctl start ai-gf-bot    # на сервере бота
sudo systemctl start ai-gf-worker # на сервере воркера
```

## ✅ Проверка работы

### **1. Отправьте сообщение боту в Telegram**
### **2. Проверьте логи на сервере воркера:**
```bash
sudo journalctl -u ai-gf-worker -f
```

**Ожидаемые логи:**
```
🚀 Запуск LLM Worker...
✅ Redis подключение установлено успешно!
✅ RabbitMQ подключение установлено успешно!
✅ Векторная база данных ChromaDB инициализирована!
📁 Путь к векторной БД: /opt/vector_db
👂 Начинаем прослушивание запросов из RabbitMQ...
📨 Получен запрос от пользователя 12345: Привет...
```

### **3. Проверьте создание векторной базы:**
```bash
ls -la /opt/vector_db/
```

## 🎯 Готово!

**AI Girlfriend Bot развернут в распределенной архитектуре!**
- 🖥️ **Сервер 1:** Бот + PostgreSQL + Redis + RabbitMQ
- 🖥️ **Сервер 2:** LLM Воркер + ChromaDB
- 🔗 **Связь:** Через сеть по защищенным портам
