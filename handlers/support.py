"""
Обработчик команды поддержки
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import BOT_TOKEN
from aiogram import Bot

router = Router()
logger = logging.getLogger(__name__)

# ID получателя поддержки
SUPPORT_RECIPIENT_ID = 525944420


class SupportStates(StatesGroup):
    """Состояния для поддержки"""
    waiting_for_message = State()


def get_support_keyboard():
    """Создать клавиатуру для поддержки"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text.startswith("/support"))
async def handle_support_command(message: Message, state: FSMContext):
    """Обработчик команды /support"""
    logger.info(
        f"🆘 SUPPORT: Получена команда /support от пользователя {message.from_user.id}"
    )
    logger.info(f"🆘 SUPPORT: Текст сообщения: '{message.text}'")

    await message.answer(
        "🆘 Служба поддержки\n\n"
        "Опиши свою проблему или вопрос, и мы обязательно поможем! 💬\n\n"
        "Можешь прикрепить скриншот или файл, если это поможет "
        "объяснить проблему.\n\n"
        "Напиши сообщение или нажми 'Отменить' для выхода.",
        reply_markup=get_support_keyboard()
    )

    # Устанавливаем состояние ожидания сообщения
    await state.set_state(SupportStates.waiting_for_message)


# Дополнительный обработчик для случая, если команда не сработала
@router.message(F.text == "support")
async def handle_support_text(message: Message, state: FSMContext):
    """Обработчик текста 'support'"""
    logger.info(f"🆘 SUPPORT: Получен текст 'support' от пользователя {message.from_user.id}")
    await handle_support_command(message, state)


# Обработчик для русского текста "поддержка"
@router.message(F.text == "поддержка")
async def handle_support_russian(message: Message, state: FSMContext):
    """Обработчик текста 'поддержка'"""
    logger.info(f"🆘 SUPPORT: Получен текст 'поддержка' от пользователя {message.from_user.id}")
    await handle_support_command(message, state)


@router.message(F.text == "❌ Отменить")
async def handle_cancel_support(message: Message, state: FSMContext):
    """Обработчик отмены поддержки"""
    logger.info(f"Отмена поддержки от пользователя {message.from_user.id}")
    
    await state.clear()
    await message.answer(
        "❌ Обращение в поддержку отменено.\n\n"
        "Если у тебя возникнут вопросы, просто напиши /support",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
            resize_keyboard=True
        )
    )


@router.message(SupportStates.waiting_for_message)
async def handle_support_message(message: Message, state: FSMContext):
    """Обработчик сообщения в поддержку"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Не указан"
        first_name = message.from_user.first_name or "Не указано"
        
        logger.info(f"Получено сообщение в поддержку от пользователя {user_id}")
        
        # Формируем сообщение для канала
        support_text = (
            f"🆘 Новое обращение в поддержку\n\n"
            f"👤 Пользователь: {first_name}\n"
            f"🆔 ID: {user_id}\n"
            f"📝 Username: @{username}\n\n"
            f"💬 Сообщение:\n{message.text or 'Медиа-сообщение'}"
        )
        
        # Отправляем в канал поддержки
        await send_to_support_channel(message, support_text)
        
        # Подтверждаем пользователю
        await message.answer(
            "✅ Ваше сообщение отправлено в службу поддержки!\n\n"
            "Мы рассмотрим ваше обращение и ответим в ближайшее время. 💬\n\n"
            "Спасибо за обращение! 🙏",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
                resize_keyboard=True
            )
        )
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения поддержки: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке сообщения в поддержку.\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )


async def send_to_support_channel(message: Message, support_text: str):
    """Отправить сообщение в поддержку"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        logger.info(f"🆘 SUPPORT: Отправляем сообщение получателю {SUPPORT_RECIPIENT_ID}")
        
        # Если есть медиа (фото, документ, видео и т.д.)
        if message.photo:
            await bot.send_photo(
                chat_id=SUPPORT_RECIPIENT_ID,
                photo=message.photo[-1].file_id,
                caption=support_text
            )
        elif message.document:
            await bot.send_document(
                chat_id=SUPPORT_RECIPIENT_ID,
                document=message.document.file_id,
                caption=support_text
            )
        elif message.video:
            await bot.send_video(
                chat_id=SUPPORT_RECIPIENT_ID,
                video=message.video.file_id,
                caption=support_text
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=SUPPORT_RECIPIENT_ID,
                voice=message.voice.file_id,
                caption=support_text
            )
        elif message.video_note:
            await bot.send_video_note(
                chat_id=SUPPORT_RECIPIENT_ID,
                video_note=message.video_note.file_id
            )
            await bot.send_message(
                chat_id=SUPPORT_RECIPIENT_ID,
                text=support_text
            )
        else:
            await bot.send_message(
                chat_id=SUPPORT_RECIPIENT_ID,
                text=support_text
            )
        
        logger.info(f"✅ SUPPORT: Сообщение успешно отправлено получателю {SUPPORT_RECIPIENT_ID}")
        
    except Exception as e:
        logger.error(f"❌ SUPPORT: Ошибка отправки получателю {SUPPORT_RECIPIENT_ID}: {e}")
        logger.error(f"❌ SUPPORT: Тип ошибки: {type(e).__name__}")
        raise
    finally:
        await bot.session.close()
