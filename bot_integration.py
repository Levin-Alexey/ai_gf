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
            logger.info("🔗 Инициализация BotIntegration...")
            if not BOT_TOKEN:
                logger.error("❌ BOT_TOKEN не найден в переменных окружения")
                raise ValueError("BOT_TOKEN не найден в переменных окружения.")
            
            logger.info(f"📊 BOT_TOKEN: {BOT_TOKEN[:10]}...")
            self.bot = Bot(token=BOT_TOKEN)
            logger.info("✅ BotIntegration инициализирован успешно!")
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    async def send_message_to_user(self, chat_id: int, message: str):
        """Отправить сообщение пользователю"""
        try:
            if self.bot:
                logger.info(f"📤 Отправляем сообщение пользователю {chat_id}")
                logger.info(f"📝 Длина сообщения: {len(message)} символов")
                await self.bot.send_message(chat_id, message)
                logger.info(f"✅ Сообщение успешно отправлено пользователю {chat_id}")
            else:
                logger.error("❌ Бот не инициализирован для отправки сообщения")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения пользователю {chat_id}: {e}")
            logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
    
    async def close(self):
        """Закрытие соединения с ботом"""
        if self.bot:
            await self.bot.session.close()
            logger.info("Соединение с ботом закрыто")

# Глобальный экземпляр интеграции
bot_integration = BotIntegration()
