"""
Главное меню бота
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from database import async_session_maker
from crud import get_user_by_telegram_id

router = Router()
logger = logging.getLogger(__name__)


def get_main_menu_keyboard():
    """Создать клавиатуру главного меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Начать чат")],
            [KeyboardButton(text="💳 Оплата")],
            [KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


async def show_main_menu(message: Message, user_name: str):
    """Показать главное меню"""
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Рада видеть тебя! ✨\n"
        "Выбери, что хочешь сделать:",
        reply_markup=get_main_menu_keyboard()
    )


# Обработчик кнопки "Начать чат" перенесен в handlers/chat.py


@router.message(F.text == "💳 Оплата")
async def handle_payment(message: Message):
    """Обработчик кнопки 'Оплата'"""
    await message.answer(
        "💳 Оплата и подписки\n\n"
        "Функция в разработке... Скоро здесь будут тарифы! 💎"
    )


@router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):
    """Обработчик кнопки 'Настройки'"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session,
            telegram_id=message.from_user.id
        )

    if user:
        # Формируем информацию о настройках
        tone_text = user.tone.value if user.tone else "Не установлен"
        interests_count = len(user.interests) if user.interests else 0
        goals_count = len(user.goals) if user.goals else 0

        settings_text = (
            f"⚙️ Твои настройки:\n\n"
            f"🎨 Тон общения: {tone_text}\n"
            f"🎯 Интересов: {interests_count}\n"
            f"🎯 Целей: {goals_count}\n"
            f"📝 О себе: {'Заполнено' if user.about else 'Не заполнено'}\n\n"
            f"Функция редактирования в разработке..."
        )
        await message.answer(settings_text)
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )