"""
Главное меню бота
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
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


def get_settings_keyboard():
    """Создать клавиатуру настроек"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Настроить характер")],
            [KeyboardButton(text="🤖 Настройки бота")],
            [KeyboardButton(text="🔙 Назад в меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):
    """Обработчик кнопки 'Настройки'"""
    logger.info(f"⚙️ Получено сообщение 'Настройки' от пользователя {message.from_user.id}")
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
            f"Выбери, что хочешь настроить:"
        )
        
        # Создаем inline клавиатуру
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎨 Настроить характер", callback_data="character_settings")],
                [InlineKeyboardButton(text="🤖 Настройки бота", callback_data="bot_settings")],
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
            ]
        )
        
        await message.answer(
            settings_text,
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )


@router.message(F.text == "🔙 Назад в меню")
async def handle_back_to_menu(message: Message):
    """Обработчик кнопки 'Назад в меню'"""
    user_name = (
        message.from_user.first_name or "друг"
        if message.from_user else "друг"
    )
    await show_main_menu(message, user_name)


# Обработчики inline кнопок
@router.callback_query(F.data == "character_settings")
async def handle_character_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Настроить характер'"""
    logger.info(f"🎨 Получен callback 'character_settings' от пользователя {callback.from_user.id}")
    
    # Создаем новый объект Message с правильным from_user
    from aiogram.types import Message
    message = Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,  # Используем from_user из callback
        chat=callback.message.chat,
        date=callback.message.date,
        content_type=callback.message.content_type,
        text=callback.message.text,
        reply_markup=callback.message.reply_markup
    )
    
    # Импортируем функцию из character_settings
    from .character_settings import handle_character_settings
    await handle_character_settings(message)
    await callback.answer()


@router.callback_query(F.data == "bot_settings")
async def handle_bot_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Настройки бота'"""
    logger.info(f"🤖 Получен callback 'bot_settings' от пользователя {callback.from_user.id}")
    
    # Создаем новый объект Message с правильным from_user
    from aiogram.types import Message
    message = Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,  # Используем from_user из callback
        chat=callback.message.chat,
        date=callback.message.date,
        content_type=callback.message.content_type,
        text=callback.message.text,
        reply_markup=callback.message.reply_markup
    )
    
    # Импортируем функцию из bot_settings
    from .bot_settings import handle_bot_settings
    await handle_bot_settings(message)
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def handle_back_to_main_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад в меню'"""
    logger.info(f"🔙 Получен callback 'back_to_main' от пользователя {callback.from_user.id}")
    
    # Удаляем сообщение с inline кнопками
    await callback.message.delete()
    
    # Создаем новый объект Message с правильным from_user
    from aiogram.types import Message
    message = Message(
        message_id=callback.message.message_id,
        from_user=callback.from_user,  # Используем from_user из callback
        chat=callback.message.chat,
        date=callback.message.date,
        content_type=callback.message.content_type,
        text=callback.message.text,
        reply_markup=callback.message.reply_markup
    )
    
    # Показываем главное меню
    user_name = callback.from_user.first_name or "друг"
    await show_main_menu(message, user_name)
    await callback.answer()
