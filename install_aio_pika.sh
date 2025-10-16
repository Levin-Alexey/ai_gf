#!/bin/bash

echo "🔧 Миграция на aio-pika (асинхронный RabbitMQ)"
echo "================================================"

# Проверяем, активировано ли виртуальное окружение
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Виртуальное окружение не активировано!"
    echo "Активируем venv..."
    source venv/bin/activate
fi

echo ""
echo "📦 Удаляем старую библиотеку pika..."
pip uninstall pika -y

echo ""
echo "📦 Устанавливаем aio-pika..."
pip install aio-pika==9.4.3

echo ""
echo "✅ Установка завершена!"
echo ""
echo "🧪 Запускаем тест RabbitMQ..."
python test_rabbitmq.py

echo ""
echo "================================================"
echo "✨ Готово! Теперь можете запустить бота и воркера:"
echo "   python main.py"
echo "   python run_worker.py"

