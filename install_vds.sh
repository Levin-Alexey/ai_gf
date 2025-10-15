#!/bin/bash

# 🚀 Автоматическая установка AI Girlfriend Bot на VDS
# Использование: bash install_vds.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем установку AI Girlfriend Bot на VDS..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    log_error "Запустите скрипт с правами root: sudo bash install_vds.sh"
    exit 1
fi

# 1. Обновление системы
log_info "Обновляем систему..."
apt update && apt upgrade -y

# 2. Установка Python и зависимостей
log_info "Устанавливаем Python 3.11 и зависимости..."
apt install python3.11 python3.11-venv python3.11-dev python3-pip git build-essential libpq-dev -y

# 3. Создание директории проекта
log_info "Создаем директорию проекта..."
mkdir -p /opt/AI_GF
cd /opt/AI_GF

# 4. Клонирование репозитория (если не существует)
if [ ! -d ".git" ]; then
    log_info "Клонируем репозиторий..."
    # Замените на ваш репозиторий
    git clone https://github.com/your-username/AI_GF.git .
else
    log_info "Обновляем код из репозитория..."
    git pull origin main
fi

# 5. Создание виртуального окружения
log_info "Создаем виртуальное окружение..."
python3.11 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
log_info "Устанавливаем Python зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Создание .env файла
log_info "Создаем .env файл..."
if [ ! -f ".env" ]; then
    cp env_example.txt .env
    log_warn "Файл .env создан из примера. Отредактируйте его: nano .env"
fi

# 8. Создание systemd сервисов
log_info "Создаем systemd сервисы..."

# Сервис для бота
cat > /etc/systemd/system/ai-gf-bot.service << EOF
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
EOF

# Сервис для воркера
cat > /etc/systemd/system/ai-gf-worker.service << EOF
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
EOF

# 9. Перезагрузка systemd
log_info "Перезагружаем systemd..."
systemctl daemon-reload

# 10. Включение автозапуска
log_info "Включаем автозапуск сервисов..."
systemctl enable ai-gf-bot
systemctl enable ai-gf-worker

# 11. Проверка подключения к базе данных
log_info "Проверяем подключение к базе данных..."
if python test_db_connection_memory.py; then
    log_info "✅ Подключение к базе данных работает!"
else
    log_warn "❌ Проблемы с подключением к базе данных. Проверьте .env файл"
fi

# 12. Запуск сервисов
log_info "Запускаем сервисы..."
systemctl start ai-gf-bot
systemctl start ai-gf-worker

# 13. Проверка статуса
log_info "Проверяем статус сервисов..."
echo "Статус бота:"
systemctl status ai-gf-bot --no-pager -l
echo ""
echo "Статус воркера:"
systemctl status ai-gf-worker --no-pager -l

# 14. Информация о мониторинге
log_info "🎉 Установка завершена!"
echo ""
echo "📊 Команды для мониторинга:"
echo "  Просмотр логов бота:     sudo journalctl -u ai-gf-bot -f"
echo "  Просмотр логов воркера:  sudo journalctl -u ai-gf-worker -f"
echo "  Статус сервисов:         sudo systemctl status ai-gf-*"
echo "  Перезапуск:              sudo systemctl restart ai-gf-*"
echo ""
echo "🔧 Не забудьте:"
echo "  1. Отредактировать .env файл: nano /opt/AI_GF/.env"
echo "  2. Обновить базу данных: psql -h 72.56.69.63 -U admingf -d gfdb -f /opt/AI_GF/update_db_memory.sql"
echo "  3. Проверить работу бота в Telegram"
echo ""
log_info "AI Girlfriend Bot готов к работе! 💕"
