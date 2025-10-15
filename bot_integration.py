"""
Интеграция между LLM воркером и ботом
"""
import logging
# Bot integration module
from aiogram import Bot
from config import BOT_TOKEN

logger = logging.getLogger(__name__)


class BotIntegration:
    """Класс для интеграции с ботом"""
    
    def __init__(self):
        self.bot = None
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            self.bot = Bot(token=BOT_TOKEN)
            logger.info("Bot интеграция инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    async def send_message_to_user(self, chat_id: int, message: str):
        """Отправить сообщение пользователю"""
        try:
            if self.bot:
                await self.bot.send_message(chat_id, message)
                logger.info(f"Сообщение отправлено пользователю {chat_id}")
            else:
                logger.error("Бот не инициализирован")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
    
    async def close(self):
        """Закрытие соединения с ботом"""
        if self.bot:
            await self.bot.session.close()
            logger.info("Соединение с ботом закрыто")

# Глобальный экземпляр интеграции
bot_integration = BotIntegration()
