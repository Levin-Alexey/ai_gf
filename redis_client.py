import json
import logging
import time
from typing import List, Dict
import redis.asyncio as redis
from config import (REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, 
                   CHAT_HISTORY_LIMIT, CHAT_TIMEOUT)

logger = logging.getLogger(__name__)

class RedisClient:

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

        return f"chat_history:{user_id}"

    async def add_message(self, user_id: int, role: str, content: str) -> None:

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

    async def get_user_chat_state(self, user_id: int) -> bool:

        return await self.redis.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
