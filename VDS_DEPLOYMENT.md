# 🚀 Развертывание AI Girlfriend Bot на VDS

## 📋 Подготовка VDS

### **1. Подключение к серверу:**
```bash
ssh root@your-vds-ip
# или
ssh username@your-vds-ip
```

### **2. Обновление системы:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### **3. Установка Python 3.11+:**
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# CentOS/RHEL
sudo yum install python311 python311-pip python311-devel -y
```

### **4. Установка системных зависимостей:**
```bash
# Ubuntu/Debian
sudo apt install git build-essential libpq-dev -y

# CentOS/RHEL
sudo yum groupinstall "Development Tools" -y
sudo yum install postgresql-devel -y
```

## 📥 Клонирование проекта

### **1. Клонируем репозиторий:**
```bash
cd /opt  # или /home/username
git clone https://github.com/your-username/AI_GF.git
cd AI_GF
```

### **2. Создаем виртуальное окружение:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### **3. Устанавливаем зависимости:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔧 Настройка окружения

### **1. Создаем .env файл:**
```bash
cp env_example.txt .env
nano .env
```

### **2. Заполняем .env файл:**
```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
BOT_NAME=AI_GF

# Database
DATABASE_URL=postgresql+asyncpg://admingf:admingf123!@72.56.69.63/gfdb

# Redis
REDIS_HOST=5.23.53.246
REDIS_PORT=6379
REDIS_PASSWORD=admin123

# RabbitMQ
RABBITMQ_HOST=5.23.53.246
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=T7#mQ$vP2@wL9$nR6&zE8*bY5^cN3
RABBITMQ_VHOST=/

# LLM API
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=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
LLM_MODEL=openai/gpt-3.5-turbo

# Vector Database
VECTOR_DB_PATH=/opt/AI_GF/vector_db
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VECTOR_SEARCH_LIMIT=10
VECTOR_SIMILARITY_THRESHOLD=0.7
```

## 🗄️ Настройка базы данных

### **1. Обновляем PostgreSQL:**
```bash
# Подключаемся к базе данных
psql -h 72.56.69.63 -U admingf -d gfdb

# Выполняем SQL скрипт
\i update_db_memory.sql

# Выходим
\q
```

### **2. Проверяем подключение:**
```bash
python test_db_connection_memory.py
```

## 🔄 Создание systemd сервисов

### **1. Создаем сервис для бота:**
```bash
sudo nano /etc/systemd/system/ai-gf-bot.service
```

**Содержимое файла:**
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

### **2. Создаем сервис для воркера:**
```bash
sudo nano /etc/systemd/system/ai-gf-worker.service
```

**Содержимое файла:**
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

## 🚀 Запуск сервисов

### **1. Перезагружаем systemd:**
```bash
sudo systemctl daemon-reload
```

### **2. Включаем автозапуск:**
```bash
sudo systemctl enable ai-gf-bot
sudo systemctl enable ai-gf-worker
```

### **3. Запускаем сервисы:**
```bash
sudo systemctl start ai-gf-bot
sudo systemctl start ai-gf-worker
```

### **4. Проверяем статус:**
```bash
sudo systemctl status ai-gf-bot
sudo systemctl status ai-gf-worker
```

## 📊 Мониторинг

### **1. Просмотр логов:**
```bash
# Логи бота
sudo journalctl -u ai-gf-bot -f

# Логи воркера
sudo journalctl -u ai-gf-worker -f

# Все логи
sudo journalctl -u ai-gf-* -f
```

### **2. Перезапуск сервисов:**
```bash
sudo systemctl restart ai-gf-bot
sudo systemctl restart ai-gf-worker
```

### **3. Остановка сервисов:**
```bash
sudo systemctl stop ai-gf-bot
sudo systemctl stop ai-gf-worker
```

## 🔧 Обновление системы

### **1. Остановка сервисов:**
```bash
sudo systemctl stop ai-gf-bot
sudo systemctl stop ai-gf-worker
```

### **2. Обновление кода:**
```bash
cd /opt/AI_GF
git pull origin main
```

### **3. Обновление зависимостей:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### **4. Запуск сервисов:**
```bash
sudo systemctl start ai-gf-bot
sudo systemctl start ai-gf-worker
```

## 🛠️ Диагностика проблем

### **1. Проверка подключений:**
```bash
# PostgreSQL
python test_db_connection_memory.py

# Redis
redis-cli -h 5.23.53.246 -p 6379 -a admin123 ping

# RabbitMQ
rabbitmqctl list_queues
```

### **2. Проверка портов:**
```bash
netstat -tlnp | grep :6379  # Redis
netstat -tlnp | grep :5672  # RabbitMQ
```

### **3. Проверка процессов:**
```bash
ps aux | grep python
```

## 📁 Структура на VDS

```
/opt/AI_GF/
├── main.py                 # Основной бот
├── run_worker.py           # LLM воркер
├── .env                    # Конфигурация
├── requirements.txt        # Зависимости
├── venv/                   # Виртуальное окружение
├── vector_db/              # Векторная база (создается автоматически)
├── handlers/               # Обработчики бота
├── memory_client.py        # Клиент памяти
├── vector_client.py        # Векторный клиент
└── ...
```

## ✅ Проверка работы

### **1. Отправьте сообщение боту в Telegram**
### **2. Проверьте логи:**
```bash
sudo journalctl -u ai-gf-bot -f
```

**Ожидаемые логи:**
```
🚀 Запуск AI Girlfriend Bot...
✅ PostgreSQL база данных инициализирована
✅ Redis подключение установлено успешно!
✅ RabbitMQ подключение установлено успешно!
💕 AI Girlfriend Bot готов к работе!
```

## 🎯 Готово!

**AI Girlfriend Bot развернут на VDS и готов к работе!** 🚀💕
