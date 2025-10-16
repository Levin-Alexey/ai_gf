# 🔧 Исправление ошибки 401 LLM API

## 🔍 Проблема
Воркер получает ошибку **401 Unauthorized** при обращении к LLM API:

```
ERROR:__main__:Ошибка LLM API: 401
ERROR:__main__:❌ Не удалось получить ответ от LLM для пользователя 525944420
```

## 🔍 Причина
Отсутствует или неправильно настроен API ключ для LLM сервиса.

## ✅ Решение

### 1. Получите API ключ

#### Вариант A: OpenAI API
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Зарегистрируйтесь/войдите в аккаунт
3. Перейдите в [API Keys](https://platform.openai.com/api-keys)
4. Создайте новый API ключ
5. Скопируйте ключ (начинается с `sk-...`)

#### Вариант B: OpenRouter API (рекомендуется)
1. Перейдите на [openrouter.ai](https://openrouter.ai)
2. Зарегистрируйтесь/войдите
3. Перейдите в [Keys](https://openrouter.ai/keys)
4. Создайте новый API ключ
5. Скопируйте ключ (начинается с `sk-or-...`)

### 2. Настройте .env файл

На вашем VDS добавьте в файл `.env`:

```bash
# Подключитесь к VDS
ssh root@ваш_vds_ip

# Откройте файл .env
nano /root/ai_gf/.env
```

Добавьте одну из конфигураций:

#### Для OpenAI:
```env
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
```

#### Для OpenRouter (рекомендуется):
```env
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_API_KEY=sk-or-your_openrouter_api_key_here
LLM_MODEL=openai/gpt-3.5-turbo
```

### 3. Перезапустите воркер

```bash
# Остановите воркер
sudo systemctl stop ai-gf-worker

# Запустите воркер
sudo systemctl start ai-gf-worker

# Проверьте статус
sudo systemctl status ai-gf-worker

# Следите за логами
journalctl -u ai-gf-worker -f
```

## 🧪 Проверка

### 1. Проверьте настройки:
```bash
# Проверьте, что API ключ загружается
cd /root/ai_gf
source venv/bin/activate
python -c "
from config import LLM_API_KEY, LLM_API_URL, LLM_MODEL
print(f'API URL: {LLM_API_URL}')
print(f'API Key: {LLM_API_KEY[:10]}...' if LLM_API_KEY else 'API Key: НЕ НАЙДЕН!')
print(f'Model: {LLM_MODEL}')
"
```

### 2. Отправьте тестовое сообщение боту
Напишите боту любое сообщение и проверьте логи:

```bash
journalctl -u ai-gf-worker --since "1 minute ago"
```

Вы должны увидеть:
```
INFO:__main__:🤖 Отправляем запрос к LLM API для пользователя 525944420
INFO:__main__:✅ Получен ответ от LLM для пользователя 525944420
INFO:__main__:Ответ отправлен в чат 525944420
```

## 💡 Рекомендации

### OpenRouter vs OpenAI
- **OpenRouter** - дешевле, больше моделей, проще настройка
- **OpenAI** - официальный API, но дороже

### Модели
- `openai/gpt-3.5-turbo` - быстрая и дешевая
- `openai/gpt-4` - качественнее, но дороже
- `anthropic/claude-3-haiku` - хорошее соотношение цена/качество

### Безопасность
- Никогда не коммитьте `.env` файл в git
- Регулярно ротируйте API ключи
- Устанавливайте лимиты на использование

## 🚨 Устранение неполадок

### Если API ключ не загружается:
```bash
# Проверьте файл .env
cat /root/ai_gf/.env | grep -E "(LLM_API_KEY|OPENROUTER_API_KEY)"

# Перезагрузите переменные окружения
sudo systemctl daemon-reload
sudo systemctl restart ai-gf-worker
```

### Если все еще ошибка 401:
1. Проверьте правильность API ключа
2. Убедитесь, что на счету есть средства
3. Проверьте лимиты API
4. Попробуйте другой API ключ

### Если ошибка 429 (Rate Limit):
```bash
# Добавьте в .env задержку между запросами
LLM_REQUEST_DELAY=1
```

## 📊 Ожидаемый результат

После настройки API ключа:
- ✅ Воркер получает ответы от LLM
- ✅ Бот отвечает на сообщения пользователей
- ✅ Сообщения сохраняются в историю
- ✅ Воспоминания анализируются и сохраняются

## 🎯 Итог

Настройка API ключа - это последний шаг для полной работоспособности системы. После этого ваш AI бот будет полностью функционален!
