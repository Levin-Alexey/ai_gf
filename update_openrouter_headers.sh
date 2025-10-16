#!/bin/bash

echo "🔧 Обновление заголовков OpenRouter API"
echo "========================================"

# Останавливаем воркер
echo "⏹️ Останавливаем воркер..."
sudo systemctl stop ai-gf-worker

echo ""
echo "📝 Обновите файлы llm_worker.py и test_llm_api.py на вашем локальном компьютере"
echo "   и загрузите их на VDS"
echo ""
echo "🔑 Проверьте настройки API в .env файле:"
echo "   nano /root/ai_gf/.env"
echo ""
echo "   Должно быть:"
echo "   OPENROUTER_API_KEY=sk-or-ваш_ключ"
echo "   LLM_API_URL=https://openrouter.ai/api/v1/chat/completions"
echo "   LLM_MODEL=openai/gpt-3.5-turbo"
echo ""
echo "🧪 После обновления файлов выполните:"
echo "   sudo systemctl start ai-gf-worker"
echo "   python test_llm_api.py"
echo "   journalctl -u ai-gf-worker -f"
echo ""
echo "========================================"
echo "🎯 Теперь OpenRouter API должен работать!"
