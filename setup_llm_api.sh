#!/bin/bash

echo "🔧 Настройка LLM API на VDS"
echo "============================"

# Проверяем наличие .env файла
if [ ! -f "/root/ai_gf/.env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с базовыми настройками"
    exit 1
fi

echo "📋 Текущие настройки LLM API:"
echo "-----------------------------"
grep -E "(LLM_API_KEY|OPENROUTER_API_KEY|LLM_API_URL|LLM_MODEL)" /root/ai_gf/.env || echo "Настройки не найдены"

echo ""
echo "🔑 Введите API ключ:"
echo "1) OpenAI API ключ (начинается с sk-...)"
echo "2) OpenRouter API ключ (начинается с sk-or-...)"
echo ""
read -p "Выберите тип API (1 или 2): " api_type

if [ "$api_type" = "1" ]; then
    echo ""
    echo "📝 Введите OpenAI API ключ:"
    read -p "API Key: " api_key
    
    if [[ $api_key == sk-* ]]; then
        # Обновляем .env файл для OpenAI
        sed -i '/^LLM_API_URL=/d' /root/ai_gf/.env
        sed -i '/^LLM_API_KEY=/d' /root/ai_gf/.env
        sed -i '/^OPENROUTER_API_KEY=/d' /root/ai_gf/.env
        sed -i '/^LLM_MODEL=/d' /root/ai_gf/.env
        
        echo "" >> /root/ai_gf/.env
        echo "# LLM API Settings" >> /root/ai_gf/.env
        echo "LLM_API_URL=https://api.openai.com/v1/chat/completions" >> /root/ai_gf/.env
        echo "LLM_API_KEY=$api_key" >> /root/ai_gf/.env
        echo "LLM_MODEL=gpt-3.5-turbo" >> /root/ai_gf/.env
        
        echo "✅ OpenAI API настроен!"
        
    else
        echo "❌ Неверный формат OpenAI API ключа!"
        echo "Ключ должен начинаться с 'sk-'"
        exit 1
    fi
    
elif [ "$api_type" = "2" ]; then
    echo ""
    echo "📝 Введите OpenRouter API ключ:"
    read -p "API Key: " api_key
    
    if [[ $api_key == sk-or-* ]]; then
        # Обновляем .env файл для OpenRouter
        sed -i '/^LLM_API_URL=/d' /root/ai_gf/.env
        sed -i '/^LLM_API_KEY=/d' /root/ai_gf/.env
        sed -i '/^OPENROUTER_API_KEY=/d' /root/ai_gf/.env
        sed -i '/^LLM_MODEL=/d' /root/ai_gf/.env
        
        echo "" >> /root/ai_gf/.env
        echo "# LLM API Settings" >> /root/ai_gf/.env
        echo "LLM_API_URL=https://openrouter.ai/api/v1/chat/completions" >> /root/ai_gf/.env
        echo "OPENROUTER_API_KEY=$api_key" >> /root/ai_gf/.env
        echo "LLM_MODEL=openai/gpt-3.5-turbo" >> /root/ai_gf/.env
        
        echo "✅ OpenRouter API настроен!"
        
    else
        echo "❌ Неверный формат OpenRouter API ключа!"
        echo "Ключ должен начинаться с 'sk-or-'"
        exit 1
    fi
    
else
    echo "❌ Неверный выбор!"
    exit 1
fi

echo ""
echo "🧪 Тестируем API..."
cd /root/ai_gf
source venv/bin/activate
python test_llm_api.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🔄 Перезапускаем воркер..."
    sudo systemctl restart ai-gf-worker
    
    echo ""
    echo "✅ Готово! LLM API настроен и работает!"
    echo "📊 Проверьте статус воркера:"
    echo "   sudo systemctl status ai-gf-worker"
    echo ""
    echo "📋 Следите за логами:"
    echo "   journalctl -u ai-gf-worker -f"
    
else
    echo ""
    echo "❌ API тест не прошел!"
    echo "💡 Проверьте правильность API ключа"
    echo "📄 См. файл FIX_LLM_API_401.md для решения"
fi

echo ""
echo "============================"
echo "🎯 Настройка завершена!"
