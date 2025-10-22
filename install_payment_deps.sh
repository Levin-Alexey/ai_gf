#!/bin/bash
# Скрипт установки зависимостей для платёжной системы

echo "📦 Установка зависимостей для ЮKassa и webhook..."

# Устанавливаем пакеты
pip install yookassa==3.3.0
pip install fastapi==0.115.4
pip install "uvicorn[standard]==0.32.0"
pip install pydantic==2.9.2

echo "✅ Зависимости установлены!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Добавьте WEBHOOK_URL в .env файл"
echo "2. Запустите webhook сервер: python webhook_server.py"
echo "3. Настройте webhook в ЮKassa: https://yookassa.ru/my/shop-settings"
