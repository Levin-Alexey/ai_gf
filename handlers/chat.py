import logging
import time
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup

from database import async_session_maker
from crud import get_user_by_telegram_id, get_user_current_persona
from redis_client import redis_client
from queue_client import queue_client
from utils import check_message_limit
from .menu import get_main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)

class ChatStates(StatesGroup):
    pass


def get_chat_keyboard():
    """Клавиатура для чата"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")],
            [KeyboardButton(text="🗑 Очистить историю")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "💬 Начать чат")
async def handle_start_chat(message: Message, state: FSMContext):
    """Обработчик кнопки 'Начать чат'"""
    try:
        user_id = message.from_user.id
        
        if not user_id:
            await message.answer(
                "❌ Ошибка: не удалось определить пользователя"
            )
            return

        # Очищаем состояние FSM
        await state.clear()
        
        # Включаем режим чата
        await redis_client.set_user_chat_state(user_id, True)

        # Получаем информацию о пользователе
        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(
                session,
                telegram_id=user_id
            )

        # Получаем текущего персонажа
        persona_name = "подруга"
        if user:
            from crud import get_user_current_persona
            current_persona = await get_user_current_persona(session, user.id)
            if current_persona:
                persona_name = current_persona.name

        # Показываем клавиатуру чата
        await message.answer(
            f"💬 Чат начат!\n\n"
            f"Привет! Я {persona_name}, готова поболтать с тобой! 💕\n\n"
            f"Напиши мне что-нибудь, и я отвечу! ✨",
            reply_markup=get_chat_keyboard()
        )

        logger.info(f"Пользователь {user_id} начал чат")

    except Exception as e:
        logger.error(f"Ошибка начала чата: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз."
        )


@router.message(F.text == "🗑 Очистить историю")
async def handle_clear_history(message: Message):
    """Обработчик кнопки 'Очистить историю'"""
    try:
        user_id = message.from_user.id

        if not user_id:
            await message.answer(
                "❌ Ошибка: не удалось определить пользователя"
            )
            return

        # Получаем пользователя для логирования
        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(session, telegram_id=user_id)
            if not user:
                await message.answer(
                    "⚠️ Сначала нужно пройти настройку. Напиши /start"
                )
                return

        # Очищаем историю чата напрямую
        await redis_client.clear_chat_history(user_id)

        logger.info(f"Пользователь {user_id} очистил историю чата")

        # Отправляем подтверждение
        await message.answer(
            "✅ История чата очищена!\n\n"
            "Новый диалог начнется с чистого листа. "
            "Я не буду помнить предыдущие сообщения. 💫"
        )

    except Exception as e:
        logger.error(f"Ошибка очистки истории чата: {e}")
        await message.answer(
            "❌ Произошла ошибка при очистке истории. Попробуйте еще раз."
        )


@router.message()
async def handle_other_messages(message: Message):
    """Обработчик обычных сообщений в чате"""
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        user_message = message.text

        if user_id:
            is_chatting = await redis_client.get_user_chat_state(user_id)
        else:
            is_chatting = False

        if not is_chatting:
            # Если пользователь не в режиме чата, игнорируем сообщение
            return

        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(session, telegram_id=user_id)
            if not user:
                await message.answer(
                    "⚠️ Сначала нужно пройти настройку. Напиши /start"
                )
                return

            can_send, messages_left = await check_message_limit(
                redis_client, user
            )

            if not can_send:
                await message.answer(
                    "😔 Вы достигли дневного лимита (10 сообщений).\n\n"
                    "💎 Оформите подписку для безлимитного общения с вашей AI-подругой!\n\n"
                    "📊 Преимущества подписки:\n"
                    "• Безлимитные сообщения\n"
                    "• Доступ ко всем персонажам\n"
                    "• Приоритетная поддержка",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(
                            text="💳 Оформить подписку",
                            callback_data="pay"
                        )
                    ]])
                )
                logger.info(
                    f"Пользователь {user_id} достиг лимита сообщений"
                )
                return

            if 0 <= messages_left <= 2:
                warning_text = (
                    f"⚠️ Осталось сообщений сегодня: {messages_left}\n"
                    "Оформите подписку для безлимитного общения! 💎"
                )
                await message.answer(warning_text)

            current_persona = await get_user_current_persona(session, user.id)

            logger.info(
                f"📋 Current persona for user {user_id}: "
                f"persona_id={current_persona.id if current_persona else None}, "
                f"name={current_persona.name if current_persona else 'None'}"
            )

        thinking_message = await message.answer(
            "Печатаю ответ...",
            reply_markup=get_chat_keyboard()
        )

        queue_message = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message": user_message,
            "timestamp": int(time.time()),
            "persona_id": current_persona.id if current_persona else None,
            "thinking_message_id": thinking_message.message_id
        }

        logger.info(
            f"📤 Sending to queue for user {user_id}: "
            f"persona_id={queue_message['persona_id']}"
        )

        await queue_client.publish_message(queue_message)

        if user_id:
            logger.info(f"Сообщение пользователя {user_id} отправлено в очередь")

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения чата: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз."
        )
