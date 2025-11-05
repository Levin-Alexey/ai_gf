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
    """Клавиатура для фотоальбома"""
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


def get_main_menu_keyboard():
    """Главное меню клавиатура"""
    return get_photo_album_keyboard()

async def show_main_menu(message: Message, user_name: str):
    """Показать главное меню"""
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Я твоя AI подруга, готова поболтать и поддержать тебя! 💕\n\n"
        "Выбери, что хочешь сделать:",
        reply_markup=get_main_menu_keyboard()
    )

async def send_photos_to_user(message: Message, photo_urls: list):
    """Отправить фотографии пользователю или показать меню выбора персонажей"""
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

    # Если переданы URL фотографий, отправляем их
    if photo_urls:
        from aiogram.types import InputMediaPhoto
        from aiogram import Bot
        
        try:
            # Отправляем фотографии группами по 10 (лимит Telegram)
            for i in range(0, len(photo_urls), 10):
                batch = photo_urls[i:i+10]
                if len(batch) == 1:
                    # Одна фотография
                    await message.answer_photo(photo=batch[0])
                else:
                    # Несколько фотографий - используем медиагруппу
                    media = [InputMediaPhoto(media=url) for url in batch]
                    await message.answer_media_group(media=media)
        except Exception as e:
            logger.error(f"Ошибка отправки фотографий: {e}")
            await message.answer(
                "❌ Произошла ошибка при отправке фотографий. Попробуйте позже."
            )
        return

    # Если фото не переданы, показываем меню выбора персонажей
    if has_active_subscription:
        # Показываем меню выбора персонажей для фотоальбома
        photo_album_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👩 Эва")],
                [KeyboardButton(text="👩 Лина")],
                [KeyboardButton(text="👩 Джуди")],
                [KeyboardButton(text="👩 Кира")],
                [KeyboardButton(text="👩 Нейра")],
                [KeyboardButton(text="🔙 Назад в меню")],
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer(
            "📸 Фотоальбом\n\n"
            "Выбери персонажа, чьи фотографии хочешь посмотреть:\n\n"
            "👩 Эва - нежная и романтичная\n"
            "👩 Лина - энергичная и веселая\n"
            "👩 Джуди - загадочная и соблазнительная\n"
            "👩 Кира - умная и стильная\n"
            "👩 Нейра - мистическая и таинственная",
            reply_markup=photo_album_keyboard
        )
    else:
        await message.answer(
            "📸 Фотоальбом\n\n"
            "💎 Этот раздел доступен только подписчикам!\n\n"
            "Подпишись, чтобы получить доступ к:\n"
            "• Эксклюзивным фотографиям 📸\n"
            "• Личным снимкам персонажей 💕\n"
            "Оформи подписку и получи полный доступ! ✨",
            reply_markup=get_main_menu_keyboard()
        )

@router.message(F.text == "💳 Оплата")
async def handle_payment(message: Message):
    """Обработчик кнопки Оплата"""
    from .payment import send_subscription_menu_message
    await send_subscription_menu_message(message)

@router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):
    """Обработчик кнопки Настройки"""
    from .character_settings import _show_character_settings
    await _show_character_settings(message)

@router.message(F.text == "🎨 Настроить характер")
async def handle_character_settings(message: Message):
    """Обработчик кнопки Настроить характер"""
    from .character_settings import _show_character_settings
    await _show_character_settings(message)

@router.message(F.text == "📸 Фотоальбом")
async def handle_photo_album(message: Message):
    """Обработчик кнопки Фотоальбом"""
    await send_photos_to_user(message, [])

@router.message(F.text == "🔙 Назад в меню")
async def handle_back_to_main_button(message: Message):
    """Обработчик кнопки Назад в меню"""
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session,
            telegram_id=message.from_user.id
        )
    
    if user:
        await show_main_menu(message, user.get_display_name())
    else:
        user_name = (
            message.from_user.first_name or "друг"
            if message.from_user else "друг"
        )
        await show_main_menu(message, user_name)

@router.message(F.text == "👩 Эва")
async def handle_eva_photos(message: Message):
    """Обработчик кнопки Эва"""
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
    """Обработчик кнопки Лина"""
    logger.info(
        f"👩 Получено сообщение 'Лина' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Лина\n\n"
        "Энергичная и веселая красотка ⚡\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    lina_photos = [
        "https://storage.imgbly.com/imgbly/YphomzgrdU.png",
        "https://storage.imgbly.com/imgbly/4aWBeN9NMQ.png",
        "https://storage.imgbly.com/imgbly/bR1SjuqnZ6.png",
    ]

    await send_photos_to_user(message, lina_photos)

@router.message(F.text == "👩 Джуди")
async def handle_judy_photos(message: Message):
    """Обработчик кнопки Джуди"""
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
    """Обработчик кнопки Кира"""
    logger.info(
        f"👩 Получено сообщение 'Кира' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Кира\n\n"
        "Умная и стильная красотка 💼\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    kira_photos = [
        "https://storage.imgbly.com/imgbly/Hxrellaq4k.png",
        "https://storage.imgbly.com/imgbly/tb8AZwx5Tb.jpg",
        "https://storage.imgbly.com/imgbly/FfZIRiRDUg.png",
    ]

    await send_photos_to_user(message, kira_photos)

@router.message(F.text == "👩 Нейра")
async def handle_neira_photos(message: Message):
    """Обработчик кнопки Нейра"""
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
