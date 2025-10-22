#!/bin/bash

# 🚀 Скрипт запуска webhook сервера для YooKassa

echo "=========================================="
echo "🚀 Запуск Webhook сервера (YooKassa)"
echo "=========================================="
echo ""

# Переход в рабочую директорию
cd /root/ai_gf

# Активация виртуального окружения
source venv/bin/activate

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python -c "import yookassa, fastapi, uvicorn" 2>/dev/null; then
    echo "⚠️  Устанавливаю недостающие зависимости..."
    pip install yookassa==3.3.0 fastapi==0.115.4 uvicorn[standard]==0.32.0 pydantic==2.9.2
fi

# Проверка .env
if [ ! -f ".env" ]; then
    echo "❌ Ошибка: Файл .env не найден!"
    exit 1
fi

# Проверка WEBHOOK_URL
if ! grep -q "WEBHOOK_URL.*pay.aigirlfriendbot.ru" .env; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: WEBHOOK_URL не содержит pay.aigirlfriendbot.ru"
fi

echo ""
echo "✅ Всё готово! Запускаю webhook сервер..."
echo ""
echo "📍 URL: https://pay.aigirlfriendbot.ru/webhook/yookassa"
echo "🏥 Health check: https://pay.aigirlfriendbot.ru/health"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "=========================================="
echo ""

# Запуск сервера
python webhook_server.py
