# 🔧 Исправление заголовков для OpenRouter API

## 🔍 Проблема
OpenRouter требует дополнительные заголовки для работы:
- `HTTP-Referer` - URL сайта для ранжирования на openrouter.ai
- `X-Title` - название сайта для ранжирования на openrouter.ai

## ✅ Что исправлено

### 1. **llm_worker.py**
Добавлены обязательные заголовки:
```python
headers = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://ai-gf-bot.com",  # Обязательно для OpenRouter
    "X-Title": "AI Girlfriend Bot"  # Обязательно для OpenRouter
}
```

### 2. **test_llm_api.py**
Обновлен тестовый файл с правильными заголовками.

## 🚀 Установка исправлений

### На VDS:
```bash
# Остановите воркер
sudo systemctl stop ai-gf-worker

# Обновите файлы llm_worker.py и test_llm_api.py
# (используйте git pull или скопируйте обновленные файлы)

# Запустите воркер
sudo systemctl start ai-gf-worker

# Проверьте статус
sudo systemctl status ai-gf-worker
```

### Проверьте настройки .env:
```bash
# Убедитесь, что в .env файле есть:
cat /root/ai_gf/.env | grep -E "(OPENROUTER_API_KEY|LLM_API_URL)"

# Должно быть:
OPENROUTER_API_KEY=sk-or-ваш_ключ
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=openai/gpt-3.5-turbo
```

## 🧪 Тестирование

### 1. Тест API:
```bash
cd /root/ai_gf
source venv/bin/activate
python test_llm_api.py
```

### 2. Проверка воркера:
```bash
sudo systemctl status ai-gf-worker
journalctl -u ai-gf-worker -f
```

### 3. Тест с ботом:
Напишите боту сообщение и проверьте логи. Должно быть:
```
INFO:__main__:🤖 Отправляем запрос к LLM API для пользователя 525944420
INFO:__main__:✅ Получен ответ от LLM для пользователя 525944420
```

## 📊 Ожидаемый результат

После исправления заголовков:
- ✅ OpenRouter API принимает запросы
- ✅ Воркер получает ответы от LLM
- ✅ Бот отвечает на сообщения пользователей
- ✅ Ошибка 401 исчезает

## 🔧 Дополнительные настройки

### Если нужно изменить заголовки:
В файле `llm_worker.py` найдите строки 380-381:
```python
"HTTP-Referer": "https://ai-gf-bot.com",  # Замените на ваш домен
"X-Title": "AI Girlfriend Bot"  # Замените на название вашего проекта
```

### Рекомендуемые модели OpenRouter:
- `openai/gpt-3.5-turbo` - быстрая и дешевая
- `google/gemini-2.0-flash-exp` - хорошее качество
- `anthropic/claude-3-haiku` - отличное соотношение цена/качество
- `meta-llama/llama-3.1-8b-instruct:free` - бесплатная модель

## 🎯 Итог

Теперь OpenRouter API должен работать корректно с правильными заголовками!
