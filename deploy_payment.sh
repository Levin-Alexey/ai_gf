#!/bin/bash
# 🚀 Скрипт быстрого деплоя системы платежей

echo "======================================"
echo "💳 ДЕПЛОЙ СИСТЕМЫ ПЛАТЕЖЕЙ"
echo "======================================"
echo ""

# 1. Установка зависимостей
echo "📦 Шаг 1: Установка зависимостей..."
pip install yookassa==3.3.0 fastapi==0.115.4 uvicorn[standard]==0.32.0 pydantic==2.9.2
echo "✅ Зависимости установлены"
echo ""

# 2. Применение миграции
echo "🗄️  Шаг 2: Применение миграции БД..."
python apply_subscription_migration.py
echo "✅ Миграция применена"
echo ""

# 3. Тестирование
echo "🧪 Шаг 3: Тестирование системы..."
python test_payment_system.py
echo ""

# 4. Проверка портов
echo "🔍 Шаг 4: Проверка портов..."
if command -v ufw &> /dev/null; then
    echo "Открываем порт 8000..."
    sudo ufw allow 8000/tcp
    sudo ufw status | grep 8000
fi
echo ""

# 5. Инструкции
echo "======================================"
echo "📝 СЛЕДУЮЩИЕ ШАГИ:"
echo "======================================"
echo ""
echo "1. Добавьте в .env:"
echo "   WEBHOOK_URL=http://ваш-ip:8000/webhook/yookassa"
echo ""
echo "2. Запустите webhook сервер:"
echo "   python webhook_server.py"
echo ""
echo "3. Настройте webhook в ЮKassa:"
echo "   https://yookassa.ru/my/shop-settings"
echo "   URL: http://ваш-ip:8000/webhook/yookassa"
echo "   События: payment.succeeded, payment.canceled"
echo ""
echo "4. Запустите бота:"
echo "   python main.py"
echo ""
echo "5. Протестируйте платёж в Telegram боте"
echo ""
echo "======================================"
echo "✨ ГОТОВО!"
echo "======================================"
