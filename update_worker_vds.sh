#!/bin/bash

echo "🔧 Обновление LLM Worker на VDS"
echo "================================="

# Останавливаем воркер
echo "⏹️ Останавливаем воркер..."
sudo systemctl stop ai-gf-worker

# Проверяем статус
echo "📊 Проверяем статус..."
sudo systemctl status ai-gf-worker --no-pager

echo ""
echo "✅ Воркер остановлен"
echo ""
echo "📝 Обновите файлы queue_client.py и llm_worker.py на вашем локальном компьютере"
echo "   и загрузите их на VDS, затем выполните:"
echo ""
echo "   sudo systemctl start ai-gf-worker"
echo "   sudo systemctl status ai-gf-worker"
echo "   journalctl -u ai-gf-worker -f"
echo ""
echo "================================="
echo "🎯 После обновления воркер должен работать стабильно!"
