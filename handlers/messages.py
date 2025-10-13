"""
Обработчики обычных сообщений
"""
from aiogram import Router, types

from database import async_session_maker
from crud import get_or_create_user

router = Router()


@router.message()
async def echo_message(message: types.Message):
    """Эхо-обработчик для всех остальных сообщений"""
    async with async_session_maker() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        await session.commit()

    await message.answer(
        f"Ты написал: {message.text}\n\nЯ тебя слышу! 💕"
    )
