"""
Обработчик команды /start
"""
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database import async_session_maker
from crud import get_or_create_user, update_user_last_started
from utils import is_profile_complete
from .menu import show_main_menu

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    async with async_session_maker() as session:
        # Получаем или создаём пользователя
        user, created = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

        # Обновляем время последнего /start
        await update_user_last_started(session, message.from_user.id)
        await session.commit()

        # Проверяем, заполнен ли профиль
        profile_complete = is_profile_complete(user)

        if created or not profile_complete:
            # Новый пользователь или профиль не заполнен - запускаем опросник
            logger.info(
                f"Новый пользователь: {user.telegram_id} "
                f"(@{user.username})"
            )

            # Кнопка для начала опросника
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✨ Начать настройку",
                            callback_data="start_questionnaire"
                        )
                    ]
                ]
            )

            # Приветственное сообщение для нового пользователя
            await message.answer(
                f"Привет, {user.get_display_name()}! 👋\n\n"
                "Я твоя AI друга. Рада познакомиться! ✨\n\n"
                "Я здесь, чтобы поддержать тебя, помочь с мотивацией "
                "или просто поболтать. Расскажи о себе больше:",
                reply_markup=keyboard
            )
        else:
            # Пользователь вернулся и профиль заполнен - показываем меню
            logger.info(
                f"Возвращение пользователя с заполненным профилем: "
                f"{user.telegram_id} (@{user.username})"
            )
            await show_main_menu(message, user.get_display_name())
