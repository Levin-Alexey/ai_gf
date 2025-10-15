# 🏗️ Развертывание AI Girlfriend Bot в многосерверной архитектуре

## 🏢 Архитектура системы (4 сервера)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Сервер Бота   │    │ Сервер Воркера  │    │ Сервер Redis/   │    │ Сервер PostgreSQL│
│                 │    │                 │    │ RabbitMQ        │    │                 │
│ • Telegram Bot  │    │ • LLM Worker    │    │ • Redis         │    │ • PostgreSQL    │
│                 │    │ • ChromaDB      │    │ • RabbitMQ      │    │ • Данные        │
│                 │    │ • vector_db/    │    │                 │    │ • Пользователи  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🖥️ Сервер 1: Telegram Bot

### **Установка:**
```bash
cd /opt
git clone https://github.com/your-username/AI_GF.git
cd AI_GF
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Конфигурация .env:**
```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
BOT_NAME=AI_GF

# Database (отдельный сервер)
DATABASE_URL=postgresql+asyncpg://admingf:admingf123!@postgres-server-ip/gfdb

# Redis (отдельный сервер)
REDIS_HOST=redis-rabbitmq-server-ip
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ (отдельный сервер)
RABBITMQ_HOST=redis-rabbitmq-server-ip
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=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
LLM_MODEL=openai/gpt-3.5-turbo
```

### **Systemd сервис:**
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

## 🖥️ Сервер 2: LLM Worker

### **Установка:**
```bash
cd /opt
git clone https://github.com/your-username/AI_GF.git
cd AI_GF
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Конфигурация .env:**
```env
# Database (отдельный сервер)
DATABASE_URL=postgresql+asyncpg://admingf:admingf123!@postgres-server-ip/gfdb

# Redis (отдельный сервер)
REDIS_HOST=redis-rabbitmq-server-ip
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ (отдельный сервер)
RABBITMQ_HOST=redis-rabbitmq-server-ip
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=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
LLM_MODEL=openai/gpt-3.5-turbo

# Vector Database (локально на воркере)
VECTOR_DB_PATH=/opt/vector_db
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VECTOR_SEARCH_LIMIT=10
VECTOR_SIMILARITY_THRESHOLD=0.7
```

### **Создание папки для векторной базы:**
```bash
sudo mkdir -p /opt/vector_db
sudo chmod 755 /opt/vector_db
```

### **Systemd сервис:**
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

## 🖥️ Сервер 3: Redis + RabbitMQ

### **Установка Redis:**
```bash
sudo apt update
sudo apt install redis-server -y

# Настройка Redis
sudo nano /etc/redis/redis.conf
```

**Настройки Redis:**
```
bind 0.0.0.0
port 6379
requirepass admin123
```

### **Установка RabbitMQ:**
```bash
sudo apt install rabbitmq-server -y

# Создание пользователя
sudo rabbitmqctl add_user admin T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

### **Настройка файрвола:**
```bash
sudo ufw allow from bot-server-ip to any port 6379
sudo ufw allow from worker-server-ip to any port 6379
sudo ufw allow from bot-server-ip to any port 5672
sudo ufw allow from worker-server-ip to any port 5672
```

## 🖥️ Сервер 4: PostgreSQL

### **Установка PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib -y

# Создание пользователя и базы
sudo -u postgres psql
```

**SQL команды:**
```sql
CREATE USER admingf WITH PASSWORD 'admingf123!';
CREATE DATABASE gfdb OWNER admingf;
GRANT ALL PRIVILEGES ON DATABASE gfdb TO admingf;
\q
```

### **Обновление базы данных:**
```bash
psql -h localhost -U admingf -d gfdb -f /path/to/update_db_memory.sql
```

### **Настройка доступа:**
```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```

**Настройки:**
```
listen_addresses = '*'
```

```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

**Добавить:**
```
host    all             all             bot-server-ip/32        md5
host    all             all             worker-server-ip/32     md5
```

## 🚀 Запуск системы

### **Порядок запуска:**
1. **PostgreSQL** (сервер 4)
2. **Redis + RabbitMQ** (сервер 3)
3. **LLM Worker** (сервер 2)
4. **Telegram Bot** (сервер 1)

### **Команды запуска:**
```bash
# На сервере бота
sudo systemctl enable ai-gf-bot
sudo systemctl start ai-gf-bot

# На сервере воркера
sudo systemctl enable ai-gf-worker
sudo systemctl start ai-gf-worker
```

## 📊 Мониторинг

### **Проверка всех сервисов:**
```bash
# Бот
sudo journalctl -u ai-gf-bot -f

# Воркер
sudo journalctl -u ai-gf-worker -f

# Redis
redis-cli -h redis-server-ip -p 6379 -a admin123 ping

# RabbitMQ
rabbitmqctl list_queues

# PostgreSQL
psql -h postgres-server-ip -U admingf -d gfdb -c "SELECT 1;"
```

## 🎯 Преимущества архитектуры

- ✅ **Максимальная производительность**
- ✅ **Независимое масштабирование**
- ✅ **Высокая надежность**
- ✅ **Легкое обслуживание**
- ✅ **Централизованные данные**
- ✅ **Распределенная обработка**

## 🔄 Обновление

### **На всех серверах:**
```bash
cd /opt/AI_GF
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ai-gf-*
```

**AI Girlfriend Bot готов к работе в многосерверной архитектуре!** 🚀💕
