#!/bin/bash

# 🔄 Скрипт обновления AI Girlfriend Bot на VDS
# Использование: bash update_vds.sh

set -e

echo "🔄 Обновляем AI Girlfriend Bot..."

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Запустите скрипт с правами root: sudo bash update_vds.sh"
    exit 1
fi

# Переход в директорию проекта
cd /opt/AI_GF

# 1. Остановка сервисов
log_info "Останавливаем сервисы..."
systemctl stop ai-gf-bot
systemctl stop ai-gf-worker

# 2. Обновление кода
log_info "Обновляем код из репозитория..."
git pull origin main

# 3. Активация виртуального окружения
log_info "Активируем виртуальное окружение..."
source venv/bin/activate

# 4. Обновление зависимостей
log_info "Обновляем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Перезагрузка systemd
log_info "Перезагружаем systemd..."
systemctl daemon-reload

# 6. Запуск сервисов
log_info "Запускаем сервисы..."
systemctl start ai-gf-bot
systemctl start ai-gf-worker

# 7. Проверка статуса
log_info "Проверяем статус..."
sleep 5
systemctl status ai-gf-bot --no-pager -l
systemctl status ai-gf-worker --no-pager -l

log_info "✅ Обновление завершено!"
echo ""
echo "📊 Для мониторинга используйте:"
echo "  sudo journalctl -u ai-gf-bot -f"
echo "  sudo journalctl -u ai-gf-worker -f"
