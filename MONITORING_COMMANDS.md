# 📊 Команды для мониторинга AI Girlfriend Bot

## 🔍 Быстрая диагностика

### **1. Проверка всех подключений:**
```bash
# Запуск полной диагностики
python diagnostics.py

# Быстрая проверка
bash quick_diagnostics.sh
```

### **2. Проверка сервисов:**
```bash
# Статус всех сервисов
sudo systemctl status ai-gf-bot ai-gf-worker

# Проверка активности
systemctl is-active ai-gf-bot
systemctl is-active ai-gf-worker
```

## 📋 Логи в реальном времени

### **Логи бота:**
```bash
# Последние логи
sudo journalctl -u ai-gf-bot -n 50

# Логи в реальном времени
sudo journalctl -u ai-gf-bot -f

# Логи за последний час
sudo journalctl -u ai-gf-bot --since "1 hour ago"
```

### **Логи воркера:**
```bash
# Последние логи
sudo journalctl -u ai-gf-worker -n 50

# Логи в реальном времени
sudo journalctl -u ai-gf-worker -f

# Логи за последний час
sudo journalctl -u ai-gf-worker --since "1 hour ago"
```

### **Все логи системы:**
```bash
# Логи всех сервисов AI GF
sudo journalctl -u ai-gf-* -f

# Логи с фильтром по уровню
sudo journalctl -u ai-gf-* --priority=err
```

## 🔗 Проверка подключений

### **PostgreSQL:**
```bash
# Проверка подключения
python test_db_connection_memory.py

# Прямое подключение
psql -h postgres-server-ip -U admingf -d gfdb -c "SELECT 1;"

# Проверка таблиц
psql -h postgres-server-ip -U admingf -d gfdb -c "\dt"
```

### **Redis:**
```bash
# Проверка подключения
redis-cli -h redis-server-ip -p 6379 -a admin123 ping

# Информация о Redis
redis-cli -h redis-server-ip -p 6379 -a admin123 info

# Список ключей
redis-cli -h redis-server-ip -p 6379 -a admin123 keys "*"
```

### **RabbitMQ:**
```bash
# Список очередей
rabbitmqctl list_queues

# Статус RabbitMQ
rabbitmqctl status

# Список подключений
rabbitmqctl list_connections
```

### **Векторная база:**
```bash
# Проверка папки
ls -la /opt/vector_db/

# Размер базы данных
du -sh /opt/vector_db/

# Тест векторной базы
python test_vector_db.py
```

## 🚨 Поиск ошибок

### **Ошибки подключений:**
```bash
# Поиск ошибок PostgreSQL
sudo journalctl -u ai-gf-* | grep -i "postgresql\|database"

# Поиск ошибок Redis
sudo journalctl -u ai-gf-* | grep -i "redis"

# Поиск ошибок RabbitMQ
sudo journalctl -u ai-gf-* | grep -i "rabbitmq\|queue"

# Поиск ошибок LLM API
sudo journalctl -u ai-gf-* | grep -i "llm\|api"
```

### **Ошибки векторной базы:**
```bash
# Поиск ошибок ChromaDB
sudo journalctl -u ai-gf-* | grep -i "chroma\|vector"

# Поиск ошибок эмбеддингов
sudo journalctl -u ai-gf-* | grep -i "embedding\|sentence"
```

### **Ошибки бота:**
```bash
# Поиск ошибок Telegram
sudo journalctl -u ai-gf-* | grep -i "telegram\|bot"

# Поиск ошибок отправки сообщений
sudo journalctl -u ai-gf-* | grep -i "send_message\|отправк"
```

## 📊 Мониторинг производительности

### **Использование ресурсов:**
```bash
# Использование CPU и памяти
top -p $(pgrep -f "python.*main.py")
top -p $(pgrep -f "python.*run_worker.py")

# Использование диска
df -h
du -sh /opt/AI_GF/

# Сетевые подключения
netstat -tlnp | grep python
ss -tlnp | grep python
```

### **Статистика сервисов:**
```bash
# Время работы сервисов
systemctl show ai-gf-bot --property=ActiveEnterTimestamp
systemctl show ai-gf-worker --property=ActiveEnterTimestamp

# Количество перезапусков
journalctl -u ai-gf-bot | grep "Started AI Girlfriend Bot" | wc -l
journalctl -u ai-gf-worker | grep "Started AI Girlfriend Worker" | wc -l
```

## 🔄 Управление сервисами

### **Перезапуск:**
```bash
# Перезапуск бота
sudo systemctl restart ai-gf-bot

# Перезапуск воркера
sudo systemctl restart ai-gf-worker

# Перезапуск всех сервисов
sudo systemctl restart ai-gf-*
```

### **Остановка/запуск:**
```bash
# Остановка
sudo systemctl stop ai-gf-bot ai-gf-worker

# Запуск
sudo systemctl start ai-gf-bot ai-gf-worker

# Включение автозапуска
sudo systemctl enable ai-gf-bot ai-gf-worker
```

## 🧪 Тестирование

### **Тест системы:**
```bash
# Полный тест системы
python test_system.py

# Тест только базы данных
python test_db_connection_memory.py

# Тест векторной базы
python test_vector_db.py
```

### **Тест вручную:**
```bash
# Запуск бота вручную
cd /opt/AI_GF
source venv/bin/activate
python main.py

# Запуск воркера вручную
cd /opt/AI_GF
source venv/bin/activate
python run_worker.py
```

## 📈 Полезные команды

### **Просмотр конфигурации:**
```bash
# Просмотр .env файла
cat .env

# Просмотр systemd сервисов
cat /etc/systemd/system/ai-gf-bot.service
cat /etc/systemd/system/ai-gf-worker.service
```

### **Очистка логов:**
```bash
# Очистка старых логов
sudo journalctl --vacuum-time=7d

# Очистка логов сервисов
sudo journalctl -u ai-gf-* --vacuum-time=3d
```

### **Резервное копирование:**
```bash
# Резервное копирование векторной базы
tar -czf vector_db_backup_$(date +%Y%m%d).tar.gz /opt/vector_db/

# Резервное копирование конфигурации
cp .env .env.backup.$(date +%Y%m%d)
```

## 🎯 Быстрые команды для отладки

```bash
# Полная диагностика
python diagnostics.py && echo "✅ Все тесты прошли" || echo "❌ Есть проблемы"

# Проверка логов на ошибки
sudo journalctl -u ai-gf-* --since "10 minutes ago" | grep -i error

# Проверка подключений
netstat -tlnp | grep -E "(6379|5672|5432)"

# Статус всех сервисов
systemctl status ai-gf-* --no-pager
```

**Используйте эти команды для быстрой диагностики проблем!** 🔍
