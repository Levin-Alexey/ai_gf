"""
Подробный тест OpenRouter API с диагностикой
"""
import asyncio
import logging
import aiohttp
import json
from config import LLM_API_URL, LLM_API_KEY, LLM_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openrouter_detailed():
    """Подробный тест OpenRouter API"""
    try:
        print("🔍 Подробная диагностика OpenRouter API")
        print("=" * 60)
        
        # 1. Проверяем конфигурацию
        print(f"📊 API URL: {LLM_API_URL}")
        print(f"📊 Model: {LLM_MODEL}")
        print(f"📊 API Key: {LLM_API_KEY[:15]}..." if LLM_API_KEY else "❌ API Key: НЕ НАЙДЕН!")
        
        if not LLM_API_KEY:
            print("\n❌ КРИТИЧЕСКАЯ ОШИБКА: API ключ не найден!")
            return False
        
        if not LLM_API_KEY.startswith('sk-or-'):
            print(f"\n❌ ОШИБКА: Неправильный формат ключа!")
            print(f"   Текущий: {LLM_API_KEY[:15]}...")
            print("   Должен начинаться с: sk-or-")
            return False
        
        # 2. Проверяем URL
        if 'openrouter.ai' not in LLM_API_URL:
            print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЕ: URL не для OpenRouter!")
            print(f"   Текущий: {LLM_API_URL}")
            print("   Рекомендуется: https://openrouter.ai/api/v1/chat/completions")
        
        # 3. Подготавливаем запрос
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-gf-bot.com",
            "X-Title": "AI Girlfriend Bot"
        }
        
        messages = [
            {
                "role": "system",
                "content": "Ты AI-помощник. Отвечай кратко на русском языке."
            },
            {
                "role": "user", 
                "content": "Привет! Это тестовое сообщение. Ответь 'Тест прошел успешно!'"
            }
        ]
        
        data = {
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print(f"\n🌐 Отправляем запрос...")
        print(f"📤 Headers: {json.dumps(headers, indent=2)}")
        print(f"📤 Data: {json.dumps(data, indent=2)}")
        
        # 4. Отправляем запрос
        async with aiohttp.ClientSession() as session:
            async with session.post(
                LLM_API_URL,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"\n📊 Статус ответа: {response.status}")
                print(f"📊 Headers ответа: {dict(response.headers)}")
                
                response_text = await response.text()
                print(f"📄 Тело ответа: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        if 'choices' in result and len(result['choices']) > 0:
                            answer = result['choices'][0]['message']['content'].strip()
                            print(f"\n✅ УСПЕХ! Получен ответ от LLM:")
                            print(f"💬 {answer}")
                            return True
                        else:
                            print(f"\n❌ Неожиданный формат ответа")
                            return False
                    except json.JSONDecodeError:
                        print(f"\n❌ Ошибка парсинга JSON ответа")
                        return False
                        
                elif response.status == 401:
                    print(f"\n❌ ОШИБКА 401: Неверная аутентификация")
                    print("🔍 Возможные причины:")
                    print("   1. Неправильный API ключ")
                    print("   2. Истек срок действия ключа")
                    print("   3. Ключ не активирован")
                    print("   4. Неправильный формат ключа")
                    
                    # Анализируем ответ для дополнительной информации
                    try:
                        error_data = json.loads(response_text)
                        if 'error' in error_data:
                            print(f"   📄 Детали ошибки: {error_data['error']}")
                    except:
                        pass
                    
                    return False
                    
                elif response.status == 429:
                    print(f"\n❌ ОШИБКА 429: Превышен лимит запросов")
                    print("🔍 Возможные причины:")
                    print("   1. Превышен лимит запросов в минуту")
                    print("   2. Исчерпан баланс API")
                    print("   3. Превышен месячный лимит")
                    return False
                    
                elif response.status == 400:
                    print(f"\n❌ ОШИБКА 400: Неверный запрос")
                    print("🔍 Возможные причины:")
                    print("   1. Неправильная модель")
                    print("   2. Неверный формат сообщений")
                    print("   3. Отсутствуют обязательные заголовки")
                    return False
                    
                else:
                    print(f"\n❌ НЕИЗВЕСТНАЯ ОШИБКА: {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        print(f"\n❌ ТАЙМАУТ: Превышено время ожидания ответа")
        return False
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return False

async def main():
    """Основная функция"""
    success = await test_openrouter_detailed()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 OpenRouter API работает корректно!")
        print("✅ Проблема решена!")
    else:
        print("⚠️ OpenRouter API имеет проблемы!")
        print("\n💡 Рекомендации:")
        print("   1. Проверьте API ключ на openrouter.ai")
        print("   2. Убедитесь, что на счету есть средства")
        print("   3. Создайте новый API ключ")
        print("   4. Проверьте настройки в .env файле")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
