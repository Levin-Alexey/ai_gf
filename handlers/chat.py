"""
Обработчик чата с AI
"""
import logging
import time
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from crud import get_user_by_telegram_id
from redis_client import redis_client
from queue_client import queue_client
from .menu import get_main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)

class ChatStates(StatesGroup):
    """Состояния чата"""
    chatting = State()

def get_chat_keyboard():
    """Создать клавиатуру для чата"""
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
        # Получаем пользователя из БД
        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(
                session,
                telegram_id=message.from_user.id
            )

        if not user:
            await message.answer(
                "⚠️ Сначала нужно пройти настройку. Напиши /start"
            )
            return

        # Устанавливаем состояние чата
        await state.set_state(ChatStates.chatting)
        
        # Устанавливаем состояние в Redis
        if message.from_user.id:
            await redis_client.set_user_chat_state(message.from_user.id, True)
        
        # Получаем историю чата
        if message.from_user.id:
            chat_history = await redis_client.get_chat_history(message.from_user.id)
        else:
            chat_history = []
        
        if chat_history:
            welcome_message = (
                f"💬 Чат с {user.get_display_name()}\n\n"
                "Продолжаем нашу беседу! Напиши что-нибудь 😊"
            )
        else:
            welcome_message = (
                f"💬 Чат с {user.get_display_name()}\n\n"
                "Привет! Я твой AI-помощник. Можешь писать мне что угодно - "
                "задать вопрос, поделиться мыслями или просто поболтать! 🤖✨"
            )

        await message.answer(
            welcome_message,
            reply_markup=get_chat_keyboard()
        )
        
        if message.from_user.id:
            logger.info(f"Пользователь {message.from_user.id} начал чат")
        
    except Exception as e:
        logger.error(f"Ошибка начала чата: {e}")
        await message.answer(
            "❌ Произошла ошибка при запуске чата. Попробуйте еще раз."
        )

@router.message(F.text == "🏠 Главное меню")
async def handle_back_to_menu(message: Message, state: FSMContext):
    """Обработчик кнопки 'Главное меню'"""
    try:
        # Сбрасываем состояние чата
        await state.clear()
        if message.from_user.id:
            await redis_client.set_user_chat_state(message.from_user.id, False)
        
        # Получаем пользователя для отображения имени
        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(
                session,
                telegram_id=message.from_user.id
            )
        
        if user:
            from .menu import show_main_menu
            await show_main_menu(message, user.get_display_name())
        else:
            await message.answer(
                "🏠 Главное меню",
                reply_markup=get_main_menu_keyboard()
            )
            
        if message.from_user.id:
            logger.info(f"Пользователь {message.from_user.id} вернулся в главное меню")
        
    except Exception as e:
        logger.error(f"Ошибка возврата в меню: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте еще раз."
        )

@router.message(F.text == "🗑 Очистить историю")
async def handle_clear_history(message: Message):
    """Обработчик кнопки 'Очистить историю'"""
    try:
        # Очищаем историю чата в Redis
        if message.from_user.id:
            await redis_client.clear_chat_history(message.from_user.id)
        
        await message.answer(
            "🗑 История чата очищена!\n\n"
            "Теперь мы начинаем с чистого листа! 😊"
        )
        
        if message.from_user.id:
            logger.info(f"Пользователь {message.from_user.id} очистил историю чата")
        
    except Exception as e:
        logger.error(f"Ошибка очистки истории: {e}")
        await message.answer(
            "❌ Произошла ошибка при очистке истории. Попробуйте еще раз."
        )

@router.message(ChatStates.chatting)
async def handle_chat_message(message: Message):
    """Обработчик сообщений в режиме чата"""
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        user_message = message.text
        
        # Проверяем, что пользователь в режиме чата
        if user_id:
            is_chatting = await redis_client.get_user_chat_state(user_id)
        else:
            is_chatting = False
            
        if not is_chatting:
            await message.answer(
                "💬 Для начала чата нажмите кнопку 'Начать чат' в главном меню"
            )
            return
        
        # Отправляем сообщение в очередь для обработки LLM
        queue_message = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message": user_message,
            "timestamp": int(time.time())
        }
        
        queue_client.publish_message(queue_message)
        
        # Отправляем подтверждение пользователю
        await message.answer(
            "🤔 Думаю над ответом...",
            reply_markup=get_chat_keyboard()
        )
        
        if user_id:
            logger.info(f"Сообщение пользователя {user_id} отправлено в очередь")
        
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения чата: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз."
        )

@router.message()
async def handle_other_messages(message: Message):
    """Обработчик всех остальных сообщений"""
    # Если пользователь не в режиме чата, игнорируем сообщения
    # (они будут обработаны другими обработчиками)
    pass
