# 🚀 Быстрое исправление ошибки 401 LLM API

## 🎉 Отличные новости!
Воркер теперь работает стабильно! Но есть проблема с API ключом LLM.

## 🔍 Проблема
```
ERROR:__main__:Ошибка LLM API: 401
```

## ✅ Быстрое решение

### 1. Получите API ключ
- **OpenRouter** (рекомендуется): [openrouter.ai/keys](https://openrouter.ai/keys)
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 2. Настройте на VDS
```bash
# Подключитесь к VDS
ssh root@ваш_vds_ip

# Запустите скрипт настройки
cd /root/ai_gf
bash setup_llm_api.sh
```

### 3. Или вручную
```bash
# Откройте .env файл
nano /root/ai_gf/.env

# Добавьте (замените YOUR_API_KEY):
OPENROUTER_API_KEY=sk-or-YOUR_API_KEY
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=openai/gpt-3.5-turbo

# Перезапустите воркер
sudo systemctl restart ai-gf-worker
```

## 🧪 Проверка
```bash
# Тест API
python test_llm_api.py

# Проверка воркера
sudo systemctl status ai-gf-worker
journalctl -u ai-gf-worker -f
```

## 🎯 Результат
После настройки API ключа:
- ✅ Бот отвечает на сообщения
- ✅ LLM обрабатывает запросы
- ✅ Воспоминания сохраняются
- ✅ Система полностью функциональна

## 📚 Подробности
См. `FIX_LLM_API_401.md` для полной инструкции.
