"""
Воркер для обработки сообщений через LLM
"""
import logging
import asyncio
import aiohttp
from typing import Dict, Any, List
from queue_client import queue_client
from redis_client import redis_client
from bot_integration import bot_integration
from memory_client import memory_client
from models import MemoryType, MemoryImportance
from config import LLM_API_URL, LLM_API_KEY, LLM_MODEL
from database import async_session_maker
from crud import (
    get_persona_by_id,
    get_user_persona_setting,
    get_user_by_telegram_id
)

logger = logging.getLogger(__name__)


class LLMWorker:
    """Воркер для обработки сообщений через LLM API"""
    
    def __init__(self):
        self.session = None
    
    async def start(self):
        """Запуск воркера"""
        try:
            logger.info("🚀 Запуск LLM Worker...")
            
            # Подключаемся к Redis
            logger.info("📡 Инициализация Redis...")
            await redis_client.connect()
            
            # Подключаемся к RabbitMQ
            logger.info("📡 Инициализация RabbitMQ...")
            await queue_client.connect()
            
            # Инициализируем интеграцию с ботом
            logger.info("📡 Инициализация Bot Integration...")
            await bot_integration.initialize()
            
            # Создаем HTTP сессию
            self.session = aiohttp.ClientSession()
            logger.info("🌐 HTTP сессия создана")
            
            logger.info("✅ LLM Worker успешно запущен!")
            logger.info("👂 Начинаем прослушивание запросов из RabbitMQ...")
            
            # Начинаем прослушивание очереди запросов
            # Этот метод будет блокировать выполнение
            try:
                await queue_client.consume_requests(self.handle_llm_request)
            except asyncio.CancelledError:
                logger.info("Получен сигнал остановки воркера")
            except KeyboardInterrupt:
                logger.info("Получен сигнал прерывания (Ctrl+C)")
            except Exception as e:
                logger.error(f"Ошибка в процессе прослушивания: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Ошибка запуска LLM Worker: {e}")
            raise
    
    async def stop(self):
        """Остановка воркера"""
        try:
            # Останавливаем потребление сообщений
            await queue_client.stop_consuming()
            
            # Закрываем HTTP сессию
            if self.session:
                await self.session.close()
            
            # Отключаемся от всех сервисов
            await redis_client.disconnect()
            await queue_client.disconnect()
            await bot_integration.close()
            
            logger.info("LLM Worker остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка остановки LLM Worker: {e}")
    
    async def handle_llm_request(self, message: Dict[str, Any]):
        """Обработка запроса к LLM"""
        try:
            # Запускаем асинхронную обработку
            await self.process_llm_request(message)
        except Exception as e:
            logger.error(f"Ошибка обработки запроса LLM: {e}")
    
    async def process_llm_request(self, message: Dict[str, Any]):
        """Асинхронная обработка запроса к LLM"""
        try:
            user_id = message.get('user_id')
            user_message = message.get('message')
            chat_id = message.get('chat_id')
            persona_id = message.get('persona_id')
            
            logger.info(f"📨 Получен запрос от пользователя {user_id}: {user_message[:50]}...")
            
            if not all([user_id, user_message, chat_id]):
                logger.error("❌ Неполные данные в сообщении")
                return
            
            # Проверяем типы
            if not isinstance(user_id, int) or not isinstance(chat_id, int):
                logger.error("❌ Некорректные типы user_id или chat_id")
                return
                
            if not isinstance(user_message, str):
                logger.error("❌ Некорректный тип user_message")
                return
            
            # Получаем историю чата из Redis
            chat_history = await redis_client.get_chat_history(user_id)
            
            # Получаем долгосрочную память пользователя через семантический поиск
            semantic_memories = await memory_client.search_semantic_memories(
                user_id=user_id,
                query=user_message,
                limit=15
            )
            
            # Получаем также важные воспоминания
            important_memories = await memory_client.get_user_memories(
                user_id, 
                importance_min=MemoryImportance.HIGH,
                limit=10
            )
            
            # Получаем недавние эмоции
            recent_emotions = await memory_client.get_recent_emotions(user_id, days=3, limit=5)
            
            # Получаем информацию о персонаже
            persona = None
            persona_overrides = {}
            if persona_id:
                async with async_session_maker() as session:
                    persona = await get_persona_by_id(session, persona_id)
                    if persona:
                        # Получаем пользователя по telegram_id для получения внутреннего ID
                        user = await get_user_by_telegram_id(
                            session, telegram_id=user_id
                        )
                        if user:
                            persona_setting = await get_user_persona_setting(
                                session, user.id
                            )
                            if persona_setting:
                                persona_overrides = persona_setting.overrides
            
            # Формируем контекст для LLM
            messages = self.build_llm_context(
                chat_history, 
                user_message, 
                semantic_memories, 
                important_memories, 
                recent_emotions,
                persona,
                persona_overrides
            )
            
            # Отправляем запрос к LLM API
            logger.info(f"🤖 Отправляем запрос к LLM API для пользователя {user_id}")
            llm_response = await self.call_llm_api(messages)
            
            if llm_response:
                logger.info(f"✅ Получен ответ от LLM для пользователя {user_id}")
                
                # Сохраняем сообщения в Redis
                await redis_client.add_message(user_id, "user", user_message)
                await redis_client.add_message(user_id, "assistant", llm_response)
                logger.info(f"💾 Сообщения сохранены в Redis для пользователя {user_id}")
                
                # Анализируем и сохраняем новую информацию в долгосрочную память
                logger.info(f"🧠 Анализируем воспоминания для пользователя {user_id}")
                await self._analyze_and_save_memories(user_id, user_message, llm_response)
                
                # Отправляем ответ обратно в бот
                await self.send_response_to_bot(chat_id, llm_response)
                logger.info(f"📤 Ответ отправлен пользователю {user_id}")
            else:
                logger.error(f"❌ Не удалось получить ответ от LLM для пользователя {user_id}")
                # Отправляем сообщение об ошибке
                error_message = ("Извините, произошла ошибка при обработке "
                               "вашего сообщения. Попробуйте еще раз.")
                await self.send_response_to_bot(chat_id, error_message)
                
        except Exception as e:
            logger.error(f"Ошибка обработки запроса LLM: {e}")
    
    def build_llm_context(
        self, 
        chat_history: List[Dict], 
        user_message: str, 
        semantic_memories: List = None,
        important_memories: List = None,
        recent_emotions: List = None,
        persona = None,
        persona_overrides: dict = None
    ) -> List[Dict]:
        """Построение контекста для LLM с долгосрочной памятью"""
        messages = []
        
        # Формируем системное сообщение с контекстом памяти
        system_content = self._build_system_message(
            semantic_memories, 
            important_memories, 
            recent_emotions,
            persona,
            persona_overrides or {}
        )
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        messages.append(system_message)
        
        # Добавляем историю чата
        for msg in chat_history:
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Добавляем текущее сообщение пользователя
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _build_system_message(
        self, 
        semantic_memories: List = None, 
        important_memories: List = None, 
        recent_emotions: List = None,
        persona = None,
        persona_overrides: dict = None
    ) -> str:
        """Построение системного сообщения с контекстом памяти"""
        
        # Если есть персонаж, используем его промпт-шаблон
        if persona:
            base_prompt = persona.prompt_template + "\n\n"
            
            # Применяем кастомизации пользователя
            if persona_overrides:
                if 'prompt_addition' in persona_overrides:
                    base_prompt += persona_overrides['prompt_addition'] + "\n\n"
        else:
            # Базовый промпт по умолчанию
            base_prompt = (
                "Ты AI-девушка, которая ведет долгосрочные отношения с пользователем. "
                "Ты помнишь важные факты о нем, его предпочтения, эмоции и отношения. "
                "Отвечай на русском языке, будь теплой, заботливой и понимающей. "
                "Используй информацию из памяти для более персонализированного общения.\n\n"
            )
        
        # Добавляем семантически релевантные воспоминания
        if semantic_memories:
            base_prompt += "РЕЛЕВАНТНАЯ ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ (найдена по смыслу):\n"
            for mem_data in semantic_memories[:8]:  # Топ-8 релевантных воспоминаний
                memory = mem_data["memory"]
                similarity = mem_data["similarity"]
                base_prompt += f"- {memory.content} (тип: {memory.memory_type.value}, схожесть: {similarity:.2f})\n"
            base_prompt += "\n"
        
        # Добавляем важные воспоминания
        if important_memories:
            base_prompt += "ВАЖНАЯ ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:\n"
            for memory in important_memories[:5]:  # Топ-5 важных воспоминаний
                base_prompt += f"- {memory.content} (тип: {memory.memory_type.value}, важность: {memory.importance.value})\n"
            base_prompt += "\n"
        
        # Добавляем недавние эмоции
        if recent_emotions:
            base_prompt += "НЕДАВНИЕ ЭМОЦИИ ПОЛЬЗОВАТЕЛЯ:\n"
            for emotion in recent_emotions:
                base_prompt += f"- {emotion.emotion} (интенсивность: {emotion.intensity:.1f})"
                if emotion.context:
                    base_prompt += f" - {emotion.context}"
                base_prompt += "\n"
            base_prompt += "\n"
        
        base_prompt += (
            "ИНСТРУКЦИИ:\n"
            "- Помни и используй информацию о пользователе для персонализации\n"
            "- Будь эмпатичной и учитывай эмоциональное состояние\n"
            "- Строй долгосрочные отношения, а не просто отвечай на вопросы\n"
            "- Если узнаешь что-то новое о пользователе, запомни это\n"
            "- Будь естественной и теплой в общении"
        )
        
        # Добавляем стиль ответа персонажа
        if persona and persona.reply_style:
            base_prompt += "\n\nСТИЛЬ ОТВЕТОВ:\n"
            reply_style = persona.reply_style
            
            if 'pace' in reply_style:
                base_prompt += f"- Темп общения: {reply_style['pace']}\n"
            if 'length' in reply_style:
                base_prompt += f"- Длина ответов: {reply_style['length']}\n"
            if 'structure' in reply_style:
                base_prompt += f"- Структура: {reply_style['structure']}\n"
            if 'signatures' in reply_style:
                base_prompt += f"- Подписи/фразы: {reply_style['signatures']}\n"
            
            # Применяем кастомизации стиля
            if persona_overrides and 'reply_style' in persona_overrides:
                custom_style = persona_overrides['reply_style']
                base_prompt += "\nКАСТОМИЗАЦИИ СТИЛЯ:\n"
                for key, value in custom_style.items():
                    base_prompt += f"- {key}: {value}\n"
        
        return base_prompt
    
    async def _analyze_and_save_memories(self, user_id: int, user_message: str, llm_response: str):
        """Анализирует разговор и сохраняет важную информацию в долгосрочную память"""
        try:
            # Простой анализ на ключевые слова для определения типа информации
            message_lower = user_message.lower()
            
            # Анализ эмоций
            emotion_keywords = {
                'happy': ['рад', 'счастлив', 'хорошо', 'отлично', 'замечательно', 'ура'],
                'sad': ['грустно', 'печально', 'плохо', 'ужасно', 'депрессия'],
                'anxious': ['волнуюсь', 'беспокоюсь', 'тревожно', 'нервничаю', 'переживаю'],
                'excited': ['взволнован', 'восторг', 'не могу дождаться', 'супер'],
                'angry': ['злой', 'разозлился', 'бесит', 'раздражает', 'ярость'],
                'tired': ['устал', 'устала', 'усталость', 'измотан', 'выжат']
            }
            
            detected_emotion = None
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_emotion = emotion
                    break
            
            # Сохраняем эмоцию если обнаружена
            if detected_emotion:
                intensity = 0.7  # Базовая интенсивность
                await memory_client.add_emotion(
                    user_id=user_id,
                    emotion=detected_emotion,
                    intensity=intensity,
                    context=user_message[:200]  # Первые 200 символов как контекст
                )
                logger.info(f"Сохранена эмоция {detected_emotion} для пользователя {user_id}")
            
            # Анализ на факты о пользователе
            fact_keywords = ['я', 'меня', 'мой', 'моя', 'мое', 'мне', 'у меня', 'я работаю', 'я живу', 'я учусь']
            if any(keyword in message_lower for keyword in fact_keywords):
                # Определяем важность на основе ключевых слов
                importance = MemoryImportance.MEDIUM
                if any(word in message_lower for word in ['важно', 'критично', 'серьезно', 'проблема']):
                    importance = MemoryImportance.HIGH
                elif any(word in message_lower for word in ['мечтаю', 'хочу', 'цель', 'планирую']):
                    importance = MemoryImportance.HIGH
                
                # Сохраняем как факт
                await memory_client.add_memory(
                    user_id=user_id,
                    content=user_message,
                    memory_type=MemoryType.FACT,
                    importance=importance,
                    tags=self._extract_tags(user_message)
                )
                logger.info(f"Сохранен факт для пользователя {user_id}")
            
            # Анализ на предпочтения
            preference_keywords = ['люблю', 'нравится', 'предпочитаю', 'выбираю', 'мне нравится', 'не люблю', 'не нравится']
            if any(keyword in message_lower for keyword in preference_keywords):
                await memory_client.add_memory(
                    user_id=user_id,
                    content=user_message,
                    memory_type=MemoryType.PREFERENCE,
                    importance=MemoryImportance.MEDIUM,
                    tags=self._extract_tags(user_message)
                )
                logger.info(f"Сохранено предпочтение для пользователя {user_id}")
            
            # Анализ на цели и мечты
            goal_keywords = ['хочу', 'мечтаю', 'цель', 'планирую', 'надеюсь', 'стремись', 'желаю']
            if any(keyword in message_lower for keyword in goal_keywords):
                await memory_client.add_memory(
                    user_id=user_id,
                    content=user_message,
                    memory_type=MemoryType.GOAL,
                    importance=MemoryImportance.HIGH,
                    tags=self._extract_tags(user_message)
                )
                logger.info(f"Сохранена цель/мечта для пользователя {user_id}")
            
            # Анализ на отношения
            relationship_keywords = ['мама', 'папа', 'брат', 'сестра', 'друг', 'подруга', 'жена', 'муж', 'парень', 'девушка', 'коллега']
            if any(keyword in message_lower for keyword in relationship_keywords):
                await memory_client.add_memory(
                    user_id=user_id,
                    content=user_message,
                    memory_type=MemoryType.RELATIONSHIP,
                    importance=MemoryImportance.MEDIUM,
                    tags=self._extract_tags(user_message)
                )
                logger.info(f"Сохранена информация об отношениях для пользователя {user_id}")
                
        except Exception as e:
            logger.error(f"Ошибка анализа и сохранения воспоминаний: {e}")
    
    def _extract_tags(self, text: str) -> List[str]:
        """Извлекает теги из текста"""
        tags = []
        text_lower = text.lower()
        
        # Простое извлечение тегов по ключевым словам
        tag_keywords = {
            'работа': ['работа', 'работаю', 'офис', 'карьера', 'профессия'],
            'семья': ['семья', 'родители', 'мама', 'папа', 'брат', 'сестра'],
            'друзья': ['друзья', 'друг', 'подруга', 'компания'],
            'здоровье': ['здоровье', 'болезнь', 'врач', 'больница', 'лечение'],
            'хобби': ['хобби', 'увлечение', 'спорт', 'музыка', 'книги', 'фильмы'],
            'путешествия': ['путешествие', 'отпуск', 'страна', 'город', 'поездка'],
            'учеба': ['учеба', 'университет', 'школа', 'экзамен', 'диплом'],
            'финансы': ['деньги', 'зарплата', 'покупка', 'трата', 'экономия']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    async def call_llm_api(self, messages: List[Dict]) -> str:
        """Вызов LLM API"""
        try:
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-gf-bot.com",  # Обязательно для OpenRouter
                "X-Title": "AI Girlfriend Bot"  # Обязательно для OpenRouter
            }
            
            data = {
                "model": LLM_MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            async with self.session.post(
                LLM_API_URL,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    logger.error(f"Ошибка LLM API: {response.status}")
                    return ""
                    
        except Exception as e:
            logger.error(f"Ошибка вызова LLM API: {e}")
            return ""
    
    async def send_response_to_bot(self, chat_id: int, response: str):
        """Отправка ответа обратно в бот"""
        try:
            # Отправляем ответ через интеграцию с ботом
            await bot_integration.send_message_to_user(chat_id, response)
            logger.info(f"Ответ отправлен в чат {chat_id}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки ответа в бот: {e}")

# Глобальный экземпляр воркера
llm_worker = LLMWorker()

async def main():
    """Основная функция воркера"""
    worker = LLMWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await worker.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
