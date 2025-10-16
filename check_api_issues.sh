#!/bin/bash

echo "🔍 Полная диагностика API проблем"
echo "================================="

cd /root/ai_gf
source venv/bin/activate

echo ""
echo "1️⃣ Проверяем конфигурацию API..."
python debug_api_key.py

echo ""
echo "2️⃣ Тестируем API с подробной диагностикой..."
python test_openrouter_detailed.py

echo ""
echo "3️⃣ Проверяем статус воркера..."
sudo systemctl status ai-gf-worker --no-pager

echo ""
echo "4️⃣ Последние логи воркера..."
journalctl -u ai-gf-worker --since "5 minutes ago" --no-pager

echo ""
echo "5️⃣ Проверяем файл .env..."
echo "Содержимое .env файла (скрытые ключи):"
grep -E "(API_KEY|OPENROUTER|LLM)" .env | sed 's/=.*/=***СКРЫТО***/'

echo ""
echo "================================="
echo "🎯 Диагностика завершена!"
echo ""
echo "💡 Если проблема остается:"
echo "   1. Проверьте баланс на openrouter.ai"
echo "   2. Создайте новый API ключ"
echo "   3. Убедитесь в правильности .env файла"
echo "   4. Проверьте лимиты API"
