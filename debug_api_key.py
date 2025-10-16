"""
Отладка API ключа для OpenRouter
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

print("🔍 Отладка API ключа OpenRouter")
print("=" * 50)

# Проверяем все возможные переменные
api_key_openrouter = os.getenv('OPENROUTER_API_KEY')
api_key_llm = os.getenv('LLM_API_KEY')
api_url = os.getenv('LLM_API_URL')
api_model = os.getenv('LLM_MODEL')

print(f"OPENROUTER_API_KEY: {api_key_openrouter[:20]}..." if api_key_openrouter else "OPENROUTER_API_KEY: НЕ НАЙДЕН!")
print(f"LLM_API_KEY: {api_key_llm[:20]}..." if api_key_llm else "LLM_API_KEY: НЕ НАЙДЕН!")
print(f"LLM_API_URL: {api_url}")
print(f"LLM_MODEL: {api_model}")

# Проверяем правильность формата ключа
if api_key_openrouter:
    if api_key_openrouter.startswith('sk-or-'):
        print("✅ Формат ключа OpenRouter правильный")
    else:
        print("❌ Неправильный формат ключа OpenRouter! Должен начинаться с 'sk-or-'")
        print(f"   Текущий ключ: {api_key_openrouter[:20]}...")

if api_key_llm:
    if api_key_llm.startswith('sk-'):
        print("✅ Формат ключа LLM правильный")
    else:
        print("❌ Неправильный формат ключа LLM! Должен начинаться с 'sk-'")
        print(f"   Текущий ключ: {api_key_llm[:20]}...")

print("\n🔍 Проверяем файл .env:")
print("-" * 30)
try:
    with open('.env', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if 'API_KEY' in line or 'OPENROUTER' in line or 'LLM' in line:
                # Скрываем ключ для безопасности
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if len(value) > 10:
                        hidden_value = value[:10] + "..." + value[-4:] if len(value) > 14 else value[:10] + "..."
                        print(f"Строка {i}: {key}={hidden_value}")
                    else:
                        print(f"Строка {i}: {line.strip()}")
                else:
                    print(f"Строка {i}: {line.strip()}")
except FileNotFoundError:
    print("❌ Файл .env не найден!")
except Exception as e:
    print(f"❌ Ошибка чтения .env: {e}")

print("\n🧪 Рекомендации:")
print("-" * 30)
if not api_key_openrouter and not api_key_llm:
    print("❌ API ключ не найден!")
    print("💡 Добавьте в .env файл:")
    print("   OPENROUTER_API_KEY=sk-or-ваш_ключ")
elif api_key_openrouter and not api_key_openrouter.startswith('sk-or-'):
    print("❌ Неправильный формат ключа OpenRouter!")
    print("💡 Ключ должен начинаться с 'sk-or-'")
elif api_url != 'https://openrouter.ai/api/v1/chat/completions':
    print("⚠️ Неправильный URL API!")
    print("💡 Установите в .env:")
    print("   LLM_API_URL=https://openrouter.ai/api/v1/chat/completions")
else:
    print("✅ Настройки выглядят правильно")
    print("💡 Попробуйте:")
    print("   1. Проверить баланс на openrouter.ai")
    print("   2. Создать новый API ключ")
    print("   3. Проверить лимиты API")
