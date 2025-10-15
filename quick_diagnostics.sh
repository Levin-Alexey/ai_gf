#!/bin/bash

# 🔍 Быстрая диагностика AI Girlfriend Bot
# Использование: bash quick_diagnostics.sh

echo "🔍 Быстрая диагностика AI Girlfriend Bot..."
echo "=============================================="

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Проверка .env файла
echo ""
log_info "Проверяем .env файл..."
if [ -f ".env" ]; then
    log_info "✅ .env файл найден"
    
    # Проверяем ключевые переменные
    if grep -q "BOT_TOKEN=" .env; then
        log_info "✅ BOT_TOKEN найден"
    else
        log_error "❌ BOT_TOKEN не найден в .env"
    fi
    
    if grep -q "DATABASE_URL=" .env; then
        log_info "✅ DATABASE_URL найден"
    else
        log_error "❌ DATABASE_URL не найден в .env"
    fi
    
    if grep -q "REDIS_HOST=" .env; then
        log_info "✅ REDIS_HOST найден"
    else
        log_error "❌ REDIS_HOST не найден в .env"
    fi
    
    if grep -q "RABBITMQ_HOST=" .env; then
        log_info "✅ RABBITMQ_HOST найден"
    else
        log_error "❌ RABBITMQ_HOST не найден в .env"
    fi
    
    if grep -q "LLM_API_KEY=" .env; then
        log_info "✅ LLM_API_KEY найден"
    else
        log_error "❌ LLM_API_KEY не найден в .env"
    fi
else
    log_error "❌ .env файл не найден!"
fi

# Проверка Python зависимостей
echo ""
log_info "Проверяем Python зависимости..."
if python -c "import aiogram" 2>/dev/null; then
    log_info "✅ aiogram установлен"
else
    log_error "❌ aiogram не установлен"
fi

if python -c "import redis" 2>/dev/null; then
    log_info "✅ redis установлен"
else
    log_error "❌ redis не установлен"
fi

if python -c "import pika" 2>/dev/null; then
    log_info "✅ pika установлен"
else
    log_error "❌ pika не установлен"
fi

if python -c "import chromadb" 2>/dev/null; then
    log_info "✅ chromadb установлен"
else
    log_error "❌ chromadb не установлен"
fi

if python -c "import sentence_transformers" 2>/dev/null; then
    log_info "✅ sentence_transformers установлен"
else
    log_error "❌ sentence_transformers не установлен"
fi

# Проверка файлов проекта
echo ""
log_info "Проверяем файлы проекта..."
required_files=(
    "main.py"
    "run_worker.py"
    "memory_client.py"
    "vector_client.py"
    "redis_client.py"
    "queue_client.py"
    "bot_integration.py"
    "models.py"
    "config.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_info "✅ $file найден"
    else
        log_error "❌ $file не найден"
    fi
done

# Проверка systemd сервисов
echo ""
log_info "Проверяем systemd сервисы..."
if systemctl is-active --quiet ai-gf-bot 2>/dev/null; then
    log_info "✅ ai-gf-bot сервис активен"
else
    log_warn "⚠️  ai-gf-bot сервис не активен"
fi

if systemctl is-active --quiet ai-gf-worker 2>/dev/null; then
    log_info "✅ ai-gf-worker сервис активен"
else
    log_warn "⚠️  ai-gf-worker сервис не активен"
fi

# Проверка логов
echo ""
log_info "Проверяем последние логи..."
if systemctl is-active --quiet ai-gf-bot 2>/dev/null; then
    echo "Последние 5 строк логов бота:"
    journalctl -u ai-gf-bot --no-pager -n 5
fi

if systemctl is-active --quiet ai-gf-worker 2>/dev/null; then
    echo "Последние 5 строк логов воркера:"
    journalctl -u ai-gf-worker --no-pager -n 5
fi

# Проверка сетевых подключений
echo ""
log_info "Проверяем сетевые подключения..."

# Получаем хосты из .env
if [ -f ".env" ]; then
    redis_host=$(grep "REDIS_HOST=" .env | cut -d'=' -f2)
    rabbitmq_host=$(grep "RABBITMQ_HOST=" .env | cut -d'=' -f2)
    db_host=$(grep "DATABASE_URL=" .env | cut -d'=' -f2 | sed 's/.*@\([^:]*\):.*/\1/')
    
    if [ -n "$redis_host" ] && [ "$redis_host" != "localhost" ]; then
        if ping -c 1 "$redis_host" >/dev/null 2>&1; then
            log_info "✅ Redis сервер $redis_host доступен"
        else
            log_error "❌ Redis сервер $redis_host недоступен"
        fi
    fi
    
    if [ -n "$rabbitmq_host" ] && [ "$rabbitmq_host" != "localhost" ]; then
        if ping -c 1 "$rabbitmq_host" >/dev/null 2>&1; then
            log_info "✅ RabbitMQ сервер $rabbitmq_host доступен"
        else
            log_error "❌ RabbitMQ сервер $rabbitmq_host недоступен"
        fi
    fi
    
    if [ -n "$db_host" ] && [ "$db_host" != "localhost" ]; then
        if ping -c 1 "$db_host" >/dev/null 2>&1; then
            log_info "✅ PostgreSQL сервер $db_host доступен"
        else
            log_error "❌ PostgreSQL сервер $db_host недоступен"
        fi
    fi
fi

echo ""
log_info "Диагностика завершена!"
echo ""
log_info "Для подробной диагностики запустите:"
echo "python diagnostics.py"
