"""
Тест подключения к LLM API
"""
import asyncio
import logging
import aiohttp
from config import LLM_API_URL, LLM_API_KEY, LLM_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_api():
    """Тестируем подключение к LLM API"""
    try:
        logger.info("🧪 Тестируем подключение к LLM API...")
        logger.info(f"📊 API URL: {LLM_API_URL}")
        logger.info(f"📊 Model: {LLM_MODEL}")
        logger.info(f"📊 API Key: {LLM_API_KEY[:10]}..." if LLM_API_KEY else "❌ API Key: НЕ НАЙДЕН!")
        
        if not LLM_API_KEY:
            logger.error("❌ API ключ не найден!")
            logger.error("💡 Добавьте в .env файл:")
            logger.error("   OPENROUTER_API_KEY=sk-or-your_api_key_here")
            logger.error("   или")
            logger.error("   LLM_API_KEY=sk-your_api_key_here")
            return False
        
        # Создаем тестовое сообщение
        messages = [
            {
                "role": "system",
                "content": "Ты AI-помощник. Отвечай кратко на русском языке."
            },
            {
                "role": "user",
                "content": "Привет! Это тестовое сообщение."
            }
        ]
        
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-gf-bot.com",  # Обязательно для OpenRouter
            "X-Title": "AI Girlfriend Bot"  # Обязательно для OpenRouter
        }
        
        data = {
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        logger.info("🌐 Отправляем тестовый запрос к API...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                LLM_API_URL,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                logger.info(f"📊 Статус ответа: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        answer = result['choices'][0]['message']['content'].strip()
                        logger.info(f"✅ Получен ответ от LLM:")
                        logger.info(f"💬 {answer}")
                        return True
                    else:
                        logger.error("❌ Неожиданный формат ответа API")
                        logger.error(f"📄 Ответ: {result}")
                        return False
                        
                elif response.status == 401:
                    logger.error("❌ Ошибка 401: Неверный API ключ")
                    logger.error("💡 Проверьте правильность API ключа в .env файле")
                    return False
                    
                elif response.status == 429:
                    logger.error("❌ Ошибка 429: Превышен лимит запросов")
                    logger.error("💡 Подождите немного или проверьте баланс API")
                    return False
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка API: {response.status}")
                    logger.error(f"📄 Ответ: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        logger.error("❌ Таймаут запроса к API")
        return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании API: {e}")
        return False

async def main():
    """Основная функция"""
    print("=" * 60)
    print("🧪 Тест подключения к LLM API")
    print("=" * 60)
    
    success = await test_llm_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 LLM API работает корректно!")
        print("✅ Бот готов отвечать на сообщения!")
    else:
        print("⚠️ LLM API имеет проблемы!")
        print("💡 См. файл FIX_LLM_API_401.md для решения")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
