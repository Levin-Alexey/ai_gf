# 🔧 Полное решение проблемы 401 OpenRouter API

## 😤 Понимаю ваше разочарование!
Ошибка 401 все еще есть? Давайте разберемся пошагово!

## 🔍 Пошаговая диагностика

### Шаг 1: Проверьте конфигурацию
```bash
# На VDS
cd /root/ai_gf
source venv/bin/activate
python debug_api_key.py
```

### Шаг 2: Подробный тест API
```bash
python test_openrouter_detailed.py
```

### Шаг 3: Полная диагностика
```bash
bash check_api_issues.sh
```

## 🔧 Возможные причины ошибки 401

### 1. **Неправильный формат ключа**
❌ **Неправильно:** `sk-abc123...`  
✅ **Правильно:** `sk-or-abc123...`

```bash
# Проверьте формат
cat .env | grep OPENROUTER_API_KEY
# Должно быть: OPENROUTER_API_KEY=sk-or-ваш_ключ
```

### 2. **Неправильный URL**
❌ **Неправильно:** `https://api.openai.com/v1/chat/completions`  
✅ **Правильно:** `https://openrouter.ai/api/v1/chat/completions`

```bash
# Проверьте URL
cat .env | grep LLM_API_URL
```

### 3. **Неправильная переменная**
В `.env` файле должно быть:
```env
OPENROUTER_API_KEY=sk-or-ваш_ключ
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=openai/gpt-3.5-turbo
```

**НЕ используйте:** `LLM_API_KEY` - только `OPENROUTER_API_KEY`!

### 4. **Проблемы с аккаунтом OpenRouter**

#### Проверьте баланс:
1. Зайдите на [openrouter.ai](https://openrouter.ai)
2. Перейдите в раздел "Credits"
3. Убедитесь, что есть средства

#### Проверьте ключ:
1. Перейдите в [Keys](https://openrouter.ai/keys)
2. Убедитесь, что ключ активен
3. При необходимости создайте новый

### 5. **Проблемы с лимитами**
- Превышен лимит запросов в минуту
- Превышен месячный лимит
- Заблокирован аккаунт

## 🚀 Пошаговое решение

### Вариант 1: Полная переустановка API ключа

1. **Создайте новый ключ на OpenRouter:**
   - Зайдите на [openrouter.ai/keys](https://openrouter.ai/keys)
   - Удалите старый ключ
   - Создайте новый ключ

2. **Обновите .env файл:**
   ```bash
   nano /root/ai_gf/.env
   ```
   
   Замените на:
   ```env
   OPENROUTER_API_KEY=sk-or-НОВЫЙ_КЛЮЧ
   LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
   LLM_MODEL=openai/gpt-3.5-turbo
   ```

3. **Перезапустите воркер:**
   ```bash
   sudo systemctl restart ai-gf-worker
   ```

4. **Протестируйте:**
   ```bash
   python test_openrouter_detailed.py
   ```

### Вариант 2: Переключение на OpenAI API

Если OpenRouter не работает, используйте OpenAI:

1. **Получите ключ OpenAI:**
   - Зайдите на [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Создайте новый ключ

2. **Обновите .env:**
   ```env
   LLM_API_KEY=sk-ваш_openai_ключ
   LLM_API_URL=https://api.openai.com/v1/chat/completions
   LLM_MODEL=gpt-3.5-turbo
   ```

3. **Перезапустите воркер:**
   ```bash
   sudo systemctl restart ai-gf-worker
   ```

### Вариант 3: Использование бесплатной модели

Попробуйте бесплатную модель:

```env
OPENROUTER_API_KEY=sk-or-ваш_ключ
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

## 🧪 Тестирование

### После каждого изменения:

1. **Тест конфигурации:**
   ```bash
   python debug_api_key.py
   ```

2. **Тест API:**
   ```bash
   python test_openrouter_detailed.py
   ```

3. **Проверка воркера:**
   ```bash
   sudo systemctl status ai-gf-worker
   journalctl -u ai-gf-worker -f
   ```

4. **Тест с ботом:**
   - Напишите боту сообщение
   - Проверьте логи

## 🚨 Экстренное решение

Если ничего не помогает:

1. **Создайте новый аккаунт OpenRouter**
2. **Используйте другой email**
3. **Создайте новый API ключ**
4. **Обновите .env файл**

## 📞 Поддержка

Если проблема остается:
1. Проверьте [статус OpenRouter](https://status.openrouter.ai)
2. Обратитесь в поддержку OpenRouter
3. Попробуйте другой API провайдер

## 🎯 Ожидаемый результат

После исправления должно быть:
```
INFO:__main__:🤖 Отправляем запрос к LLM API для пользователя 525944420
INFO:__main__:✅ Получен ответ от LLM для пользователя 525944420
```

**БЕЗ ошибки 401!** 🎉
