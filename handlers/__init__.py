"""
Пакет с обработчиками событий бота
"""
from aiogram import Router

from .start import router as start_router
from .questionnaire import router as questionnaire_router
from .menu import router as menu_router
from .messages import router as messages_router

# Главный роутер, объединяющий все обработчики
main_router = Router()
main_router.include_router(start_router)
main_router.include_router(questionnaire_router)
main_router.include_router(menu_router)
main_router.include_router(messages_router)  # messages в конце (catch-all)

__all__ = ['main_router']
