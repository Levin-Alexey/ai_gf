#!/bin/bash

# 🚀 Установка webhook сервиса

echo "=========================================="
echo "🔧 Установка AI GF Webhook Service"
echo "=========================================="
echo ""

# Проверка, что мы в правильной директории
if [ ! -f "ai-gf-webhook.service" ]; then
    echo "❌ Ошибка: файл ai-gf-webhook.service не найден"
    echo "Запустите скрипт из директории /root/ai_gf"
    exit 1
fi

# 1. Копирование service файла
echo "📋 Копирую service файл..."
sudo cp ai-gf-webhook.service /etc/systemd/system/
if [ $? -eq 0 ]; then
    echo "✅ Файл скопирован в /etc/systemd/system/"
else
    echo "❌ Ошибка при копировании файла"
    exit 1
fi

# 2. Проверка файла
echo ""
echo "📄 Проверка установленного файла:"
sudo cat /etc/systemd/system/ai-gf-webhook.service
echo ""

# 3. Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload
echo "✅ systemd перезагружен"

# 4. Включение автозапуска
echo ""
echo "⚡ Включение автозапуска..."
sudo systemctl enable ai-gf-webhook
if [ $? -eq 0 ]; then
    echo "✅ Автозапуск включён"
else
    echo "❌ Ошибка при включении автозапуска"
    exit 1
fi

# 5. Запуск сервиса
echo ""
echo "🚀 Запуск сервиса..."
sudo systemctl start ai-gf-webhook
sleep 2

# 6. Проверка статуса
echo ""
echo "=========================================="
echo "📊 Статус сервиса:"
echo "=========================================="
sudo systemctl status ai-gf-webhook --no-pager
echo ""

# 7. Проверка работы
echo "=========================================="
echo "🧪 Проверка работоспособности:"
echo "=========================================="
sleep 1
curl -s http://localhost:8000/health
echo ""
echo ""

# Итог
if systemctl is-active --quiet ai-gf-webhook; then
    echo "=========================================="
    echo "✅ ВСЁ ГОТОВО! Webhook сервер работает!"
    echo "=========================================="
    echo ""
    echo "📝 Полезные команды:"
    echo "  - Статус: sudo systemctl status ai-gf-webhook"
    echo "  - Логи: sudo journalctl -u ai-gf-webhook -f"
    echo "  - Рестарт: sudo systemctl restart ai-gf-webhook"
    echo "  - Остановка: sudo systemctl stop ai-gf-webhook"
    echo ""
    echo "🌐 Endpoints:"
    echo "  - Health: http://localhost:8000/health"
    echo "  - Webhook: https://pay.aigirlfriendbot.ru/webhook/yookassa"
    echo ""
else
    echo "=========================================="
    echo "❌ Ошибка! Сервис не запустился"
    echo "=========================================="
    echo ""
    echo "Проверьте логи:"
    echo "  sudo journalctl -u ai-gf-webhook -n 50"
    echo ""
fi
