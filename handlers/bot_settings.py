"""
Обработчик настроек бота
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
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


@router.callback_query(F.data == "bot_settings")
async def handle_bot_settings_callback(callback: CallbackQuery):
    """Обработчик callback кнопки 'Настройки бота'"""
    logger.info(f"🤖 Получен callback 'bot_settings' от пользователя {callback.from_user.id}")
    if callback.message:
        await _show_bot_settings(callback.message, callback.from_user)
    await callback.answer()


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
        await message.answer(
            bot_settings_text,
            reply_markup=get_bot_settings_keyboard()
        )
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


@router.message(F.text == "🔙 Назад к настройкам")
async def handle_back_to_settings(message: Message):
    """Обработчик кнопки 'Назад к настройкам'"""
    from .menu import handle_settings
    await handle_settings(message)
