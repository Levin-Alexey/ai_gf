"""
Обработчик настроек бота
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from database import async_session_maker
from crud import get_user_by_telegram_id

router = Router()
logger = logging.getLogger(__name__)


def get_bot_settings_keyboard():
    """Создать клавиатуру настроек бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔔 Уведомления")],
            [KeyboardButton(text="🌙 Режим работы")],
            [KeyboardButton(text="🔒 Приватность")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🔙 Назад к настройкам")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "🤖 Настройки бота")
async def handle_bot_settings(message: Message):
    """Обработчик кнопки 'Настройки бота'"""
    await _show_bot_settings(message)




async def _show_bot_settings(message: Message, from_user=None):
    """Общая функция для показа настроек бота"""
    if not message:
        return
    user_id = from_user.id if from_user else message.from_user.id
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, telegram_id=user_id)

    if user:
        bot_settings_text = (
            "🤖 Настройки бота:\n\n"
            "🔔 Уведомления: Включены\n"
            "🌙 Режим работы: 24/7\n"
            "🔒 Приватность: Стандартная\n"
            "📊 Статистика: Доступна\n\n"
            "Выбери, что хочешь настроить:"
        )
        # Создаем inline клавиатуру
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
                [InlineKeyboardButton(text="🌙 Режим работы", callback_data="work_mode")],
                [InlineKeyboardButton(text="🔒 Приватность", callback_data="privacy")],
                [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")],
                [InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="back_to_settings")]
            ]
        )
        await message.answer(bot_settings_text, reply_markup=keyboard)
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )


@router.message(F.text == "🔔 Уведомления")
async def handle_notifications(message: Message):
    """Обработчик кнопки 'Уведомления'"""
    await message.answer(
        "🔔 Настройки уведомлений\n\n"
        "Функция в разработке... Скоро здесь можно настроить уведомления! 🔔"
    )


@router.message(F.text == "🌙 Режим работы")
async def handle_work_mode(message: Message):
    """Обработчик кнопки 'Режим работы'"""
    await message.answer(
        "🌙 Режим работы\n\n"
        "Функция в разработке... Скоро здесь можно настроить режим работы! 🌙"
    )


@router.message(F.text == "🔒 Приватность")
async def handle_privacy(message: Message):
    """Обработчик кнопки 'Приватность'"""
    await message.answer(
        "🔒 Настройки приватности\n\n"
        "Функция в разработке... Скоро здесь можно настроить приватность! 🔒"
    )


@router.message(F.text == "📊 Статистика")
async def handle_statistics(message: Message):
    """Обработчик кнопки 'Статистика'"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session,
            telegram_id=message.from_user.id
        )

    if user:
        # Здесь можно добавить реальную статистику
        stats_text = (
            "📊 Твоя статистика:\n\n"
            "💬 Сообщений отправлено: 0\n"
            "⏰ Время в боте: 0 минут\n"
            "🎯 Целей достигнуто: 0\n"
            "📅 Дата регистрации: Неизвестно\n\n"
            "Статистика будет обновляться по мере использования бота! 📈"
        )
        await message.answer(stats_text)
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )


# Callback обработчики
@router.callback_query(F.data == "notifications")
async def handle_notifications_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Уведомления'"""
    await callback.message.answer(
        "🔔 Настройки уведомлений\n\n"
        "Функция в разработке... Скоро здесь можно настроить уведомления! 🔔"
    )
    await callback.answer()


@router.callback_query(F.data == "work_mode")
async def handle_work_mode_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Режим работы'"""
    await callback.message.answer(
        "🌙 Режим работы\n\n"
        "Функция в разработке... Скоро здесь можно настроить режим работы! 🌙"
    )
    await callback.answer()


@router.callback_query(F.data == "privacy")
async def handle_privacy_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Приватность'"""
    await callback.message.answer(
        "🔒 Настройки приватности\n\n"
        "Функция в разработке... Скоро здесь можно настроить приватность! 🔒"
    )
    await callback.answer()


@router.callback_query(F.data == "statistics")
async def handle_statistics_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Статистика'"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session,
            telegram_id=callback.from_user.id
        )

    if user:
        # Здесь можно добавить реальную статистику
        stats_text = (
            "📊 Твоя статистика:\n\n"
            "💬 Сообщений отправлено: 0\n"
            "⏰ Время в боте: 0 минут\n"
            "🎯 Целей достигнуто: 0\n"
            "📅 Дата регистрации: Неизвестно\n\n"
            "Статистика будет обновляться по мере использования бота! 📈"
        )
        await callback.message.answer(stats_text)
    else:
        await callback.message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def handle_back_to_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад к настройкам'"""
    from .menu import handle_settings
    await handle_settings(callback.message)
    await callback.answer()
