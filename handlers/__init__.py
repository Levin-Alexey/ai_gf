"""
Пакет с обработчиками событий бота
"""
from aiogram import Router

from .start import router as start_router
from .questionnaire import router as questionnaire_router
from .menu import router as menu_router
from .chat import router as chat_router
from .character_settings import router as character_settings_router
from .bot_settings import router as bot_settings_router
from .payment import router as payment_router
from .messages import router as messages_router
from .support import router as support_router

# Главный роутер, объединяющий все обработчики
main_router = Router()
main_router.include_router(support_router)  # Поддержка в начале
main_router.include_router(start_router)
main_router.include_router(questionnaire_router)
main_router.include_router(menu_router)
main_router.include_router(chat_router)
main_router.include_router(character_settings_router)
main_router.include_router(bot_settings_router)
main_router.include_router(payment_router)
main_router.include_router(messages_router)  # messages в конце (catch-all)

__all__ = ['main_router']
