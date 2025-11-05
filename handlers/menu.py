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

def get_photo_album_keyboard():

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Начать чат")],
            [KeyboardButton(text="📸 Фотоальбом")],
            [KeyboardButton(text="💳 Оплата")],
            [KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

async def show_main_menu(message: Message, user_name: str):

    await message.answer(
        "📸 Фотоальбом\n\n"
        "Выбери персонажа, чьи фотографии хочешь посмотреть:\n\n"
        "👩 Эва - нежная и романтичная\n"
        "👩 Лина - энергичная и веселая\n"
        "👩 Джуди - загадочная и соблазнительная\n"
        "👩 Кира - умная и стильная\n"
        "👩 Нейра - мистическая и таинственная",
        reply_markup=get_photo_album_keyboard()
    )

async def send_photos_to_user(message: Message, photo_urls: list):

    logger.info(
        f"📸 Получено сообщение 'Фотоальбом' от пользователя "
        f"{message.from_user.id}"
    )

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

    from datetime import datetime
    has_active_subscription = False

    if user.subscription_expires_at:
        now = datetime.now(user.subscription_expires_at.tzinfo)
        if user.subscription_expires_at > now:
            has_active_subscription = True

    if has_active_subscription:

        await show_photo_album_personas(message)
    else:

        await message.answer(
            "📸 Фотоальбом\n\n"
            "💎 Этот раздел доступен только подписчикам!\n\n"
            "Подпишись, чтобы получить доступ к:\n"
            "• Эксклюзивным фотографиям 📸\n"
            "• Личным снимкам персонажей 💕\n"
            "• Новым фото каждую неделю 🆕\n\n"
            "Оформи подписку и получи полный доступ! ✨",
            reply_markup=get_main_menu_keyboard()
        )

@router.message(F.text == "💳 Оплата")
async def handle_payment(message: Message):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Настроить характер")],
            [KeyboardButton(text="🗑 Очистить историю")],
            [KeyboardButton(text="🆘 Обратиться в поддержку")],
            [KeyboardButton(text="🔙 Назад в меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

@router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):

    user_name = (
        message.from_user.first_name or "друг"
        if message.from_user else "друг"
    )
    await show_main_menu(message, user_name)

@router.message(F.text == "🎨 Настроить характер")
async def handle_character_settings_button(message: Message):

    logger.info(
        f"🆘 SUPPORT: Получено сообщение "
        f"'Обратиться в поддержку' от пользователя "
        f"{message.from_user.id}"
    )

    await message.answer(
        "🆘 Служба поддержки\n\n"
        "Для обращения в поддержку напишите:\n"
        "https://t.me/AIGFSupport"
    )

@router.message(F.text == "🔙 Назад в меню")
async def handle_back_to_main_button(message: Message):

    logger.info(
        f"👩 Получено сообщение 'Эва' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Эва\n\n"
        "Нежная и романтичная красавица 💕\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    eva_photos = [
        "https://storage.imgbly.com/imgbly/7NLa1jKFx4.png",
        "https://storage.imgbly.com/imgbly/1Jy8XffVp9.png",
        "https://storage.imgbly.com/imgbly/DlkpWwfVjl.png",
        "https://storage.imgbly.com/imgbly/3ZIbnMP6Ss.png",
        "https://storage.imgbly.com/imgbly/BnEZ6olb3e.png",
        "https://storage.imgbly.com/imgbly/q1Zlni2A6q.jpg"
    ]

    await send_photos_to_user(message, eva_photos)

@router.message(F.text == "👩 Лина")
async def handle_lina_photos(message: Message):

    logger.info(
        f"👩 Получено сообщение 'Джуди' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Джуди\n\n"
        "Загадочная и соблазнительная красотка 🔥\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    judy_photos = [
        "https://storage.imgbly.com/imgbly/YphomzgrdU.png",
        "https://storage.imgbly.com/imgbly/4aWBeN9NMQ.png",
        "https://storage.imgbly.com/imgbly/bR1SjuqnZ6.png",
        "https://storage.imgbly.com/imgbly/JI5khthvWI.png",
        "https://storage.imgbly.com/imgbly/qRPYud7xyy.png",
        "https://storage.imgbly.com/imgbly/1BQiWXJ2To.png",
        "https://storage.imgbly.com/imgbly/D8T6wty22T.jpg",
        "https://storage.imgbly.com/imgbly/J1J2XyEcRv.jpg",
        "https://storage.imgbly.com/imgbly/JMF3KfYrvv.jpg",
        "https://storage.imgbly.com/imgbly/IrKp2Jxzwr.jpg"
    ]

    await send_photos_to_user(message, judy_photos)

@router.message(F.text == "👩 Кира")
async def handle_kira_photos(message: Message):

    logger.info(
        f"👩 Получено сообщение 'Нейра' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Нейра\n\n"
        "Мистическая и таинственная волшебница ✨\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    neira_photos = [
        "https://storage.imgbly.com/imgbly/Hxrellaq4k.png",
        "https://storage.imgbly.com/imgbly/tb8AZwx5Tb.jpg",
        "https://storage.imgbly.com/imgbly/FfZIRiRDUg.png",
        "https://storage.imgbly.com/imgbly/xDoXQwiDuH.png",
        "https://storage.imgbly.com/imgbly/DLGEnraSQd.png",
        "https://storage.imgbly.com/imgbly/ktZ5HQrxQm.png",
        "https://storage.imgbly.com/imgbly/SBOLJgpSJC.jpg",
        "https://storage.imgbly.com/imgbly/WrLfSLtJ0v.jpg",
        "https://storage.imgbly.com/imgbly/PUEmSsB1HB.jpg"
    ]

    await send_photos_to_user(message, neira_photos)
