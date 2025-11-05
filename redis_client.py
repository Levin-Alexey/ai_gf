import json
import logging
import time
from typing import List, Dict
import redis.asyncio as redis
from config import (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, 
                   CHAT_HISTORY_LIMIT, CHAT_TIMEOUT)

logger = logging.getLogger(__name__)

class RedisClient:
    """Клиент для работы с Redis"""
    
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """Подключиться к Redis"""
        try:
            logger.info(f"🔗 Подключаемся к Redis: {REDIS_HOST}:{REDIS_PORT}")
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            
            await self.redis.ping()
            logger.info("✅ Redis подключение установлено успешно!")
            logger.info(f"📊 Redis конфигурация: host={REDIS_HOST}, port={REDIS_PORT}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            raise
    
    async def disconnect(self):
        """Отключиться от Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Соединение с Redis закрыто")
    
    def _get_chat_key(self, user_id: int) -> str:
        """Получить ключ для истории чата пользователя"""
        return f"chat_history:{user_id}"
    
    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю чата"""
        try:
            chat_key = self._get_chat_key(user_id)
            message_data = {
                "role": role,
                "content": content,
                "timestamp": time.time()
            }
            message_json = json.dumps(message_data)
            
            # Добавляем сообщение в начало списка
            await self.redis.lpush(chat_key, message_json)
            
            # Ограничиваем количество сообщений
            await self.redis.ltrim(chat_key, 0, CHAT_HISTORY_LIMIT - 1)
            
            # Устанавливаем время жизни ключа
            await self.redis.expire(chat_key, CHAT_TIMEOUT)
            
        except Exception as e:
            logger.error(f"Ошибка добавления сообщения в Redis: {e}")
    
    async def get_chat_history(self, user_id: int) -> List[Dict]:
        """Получить историю чата пользователя"""
        try:
            chat_key = self._get_chat_key(user_id)
            messages = await self.redis.lrange(chat_key, 0, -1)
            
            history = []
            for msg in reversed(messages):
                try:
                    message_data = json.loads(msg)
                    history.append(message_data)
                except json.JSONDecodeError:
                    continue
            
            return history
            
        except Exception as e:
            logger.error(f"Ошибка получения истории чата из Redis: {e}")
            return []
    
    async def clear_chat_history(self, user_id: int) -> None:
        """Очистить историю чата пользователя"""
        try:
            chat_key = self._get_chat_key(user_id)
            await self.redis.delete(chat_key)
            logger.info(f"История чата очищена для пользователя {user_id}")
        except Exception as e:
            logger.error(f"Ошибка очистки истории чата: {e}")
    
    async def set_user_chat_state(self, user_id: int, is_chatting: bool) -> None:
        """Установить состояние чата пользователя"""
        try:
            state_key = f"chat_state:{user_id}"
            await self.redis.set(state_key, "1" if is_chatting else "0", ex=CHAT_TIMEOUT)
        except Exception as e:
            logger.error(f"Ошибка установки состояния чата: {e}")
    
    async def get_user_chat_state(self, user_id: int) -> bool:
        """Получить состояние чата пользователя"""
        try:
            state_key = f"chat_state:{user_id}"
            state = await self.redis.get(state_key)
            return state == "1"
        except Exception as e:
            logger.error(f"Ошибка получения состояния чата: {e}")
            return False


# Создаем экземпляр клиента
redis_client = RedisClient()
