"""
Главное меню бота
"""
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
    """Создать клавиатуру фотоальбома с персонажами"""
    keyboard = ReplyKeyboardMarkup(
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
    return keyboard


def get_main_menu_keyboard():
    """Создать клавиатуру главного меню"""
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
    """Показать главное меню"""
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Рада видеть тебя! ✨\n"
        "Выбери, что хочешь сделать:",
        reply_markup=get_main_menu_keyboard()
    )


async def show_photo_album_personas(message: Message):
    """Показать персонажей в фотоальбоме для подписчиков"""
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
    """Отправить фотографии пользователю"""
    try:
        from aiogram import Bot
        from config import BOT_TOKEN

        bot = Bot(token=BOT_TOKEN)

        for i, photo_url in enumerate(photo_urls, 1):
            try:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo_url,
                    caption=f"📸 Фото {i}/{len(photo_urls)}"
                )
                logger.info(
                    f"Отправлено фото {i} пользователю {message.from_user.id}"
                )

                # Небольшая задержка между фотографиями
                import asyncio
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Ошибка отправки фото {i}: {e}")
                continue

        await bot.session.close()

    except Exception as e:
        logger.error(f"Ошибка отправки фотографий: {e}")
        await message.answer(
            "❌ Произошла ошибка при загрузке фотографий. Попробуйте позже."
        )


# Обработчик кнопки "Начать чат" перенесен в handlers/chat.py


@router.message(F.text == "📸 Фотоальбом")
async def handle_photo_album(message: Message):
    """Обработчик кнопки 'Фотоальбом'"""
    logger.info(
        f"📸 Получено сообщение 'Фотоальбом' от пользователя "
        f"{message.from_user.id}"
    )

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

    # Проверяем подписку
    from datetime import datetime
    has_active_subscription = False

    if user.subscription_expires_at:
        now = datetime.now(user.subscription_expires_at.tzinfo)
        if user.subscription_expires_at > now:
            has_active_subscription = True

    if has_active_subscription:
        # Показываем персонажей для подписчиков
        await show_photo_album_personas(message)
    else:
        # Показываем сообщение для неподписчиков
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
    """Обработчик кнопки 'Оплата'"""
    # Показать актуальное меню подписки из payment
    try:
        from .payment import send_subscription_menu_message
        await send_subscription_menu_message(message)
    except Exception:
        # fallback текст
        await message.answer(
            "💳 Оплата и подписки\n\n"
            "Скоро здесь будут тарифы! 💎"
        )


def get_settings_keyboard():
    """Создать клавиатуру настроек"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Настроить характер")],
            # [KeyboardButton(text="🤖 Настройки бота")],  # Временно
            # закомментировано
            [KeyboardButton(text="🔙 Назад в меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):
    """Обработчик кнопки 'Настройки'"""
    logger.info(
        f"⚙️ Получено сообщение 'Настройки' от пользователя "
        f"{message.from_user.id}"
    )
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

        # Создаем обычную клавиатуру
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎨 Настроить характер")],
                # [KeyboardButton(text="🤖 Настройки бота")],  # Временно
                # закомментировано
                [KeyboardButton(text="🔙 Назад в меню")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
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


# Обработчики кнопок настроек
@router.message(F.text == "🎨 Настроить характер")
async def handle_character_settings_button(message: Message):
    """Обработчик кнопки 'Настроить характер'"""
    logger.info(
        f"🎨 Получено сообщение 'Настроить характер' от пользователя "
        f"{message.from_user.id}"
    )

    # Импортируем функцию из character_settings
    from .character_settings import handle_character_settings
    await handle_character_settings(message)


# @router.message(F.text == "🤖 Настройки бота")
# async def handle_bot_settings_button(message: Message):
#     """Обработчик кнопки 'Настройки бота'"""
#     logger.info(
#         f"🤖 Получено сообщение 'Настройки бота' от пользователя "
#         f"{message.from_user.id}"
#     )
#
#     # Импортируем функцию из bot_settings
#     from .bot_settings import handle_bot_settings
#     await handle_bot_settings(message)


@router.message(F.text == "🔙 Назад в меню")
async def handle_back_to_main_button(message: Message):
    """Обработчик кнопки 'Назад в меню'"""
    logger.info(
        f"🔙 Получено сообщение 'Назад в меню' от пользователя "
        f"{message.from_user.id}"
    )

    # Показываем главное меню
    user_name = message.from_user.first_name or "друг"
    await show_main_menu(message, user_name)


# Обработчики персонажей в фотоальбоме
@router.message(F.text == "👩 Эва")
async def handle_eva_photos(message: Message):
    """Обработчик кнопки 'Эва' в фотоальбоме"""
    logger.info(
        f"👩 Получено сообщение 'Эва' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Эва\n\n"
        "Нежная и романтичная красавица 💕\n\n"
        "Скоро здесь будут фотографии Эвы!\n"
        "Функция в разработке... 🔧",
        reply_markup=get_photo_album_keyboard()
    )


@router.message(F.text == "👩 Лина")
async def handle_lina_photos(message: Message):
    """Обработчик кнопки 'Лина' в фотоальбоме"""
    logger.info(
        f"👩 Получено сообщение 'Лина' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Лина\n\n"
        "Энергичная и веселая девушка ⚡\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    # Список фотографий Лины
    lina_photos = [
        "https://storage.imgbly.com/imgbly/pntzM4WPG5.png",
        "https://storage.imgbly.com/imgbly/7tjIeYwgxN.png",
        "https://storage.imgbly.com/imgbly/SiuhCoWNm0.jpg",
        "https://storage.imgbly.com/imgbly/VrUeAgY9w8.jpg",
        "https://storage.imgbly.com/imgbly/Gzpn0H7n6H.jpg"
    ]

    # Отправляем фотографии
    await send_photos_to_user(message, lina_photos)


@router.message(F.text == "👩 Джуди")
async def handle_judy_photos(message: Message):
    """Обработчик кнопки 'Джуди' в фотоальбоме"""
    logger.info(
        f"👩 Получено сообщение 'Джуди' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Джуди\n\n"
        "Загадочная и соблазнительная красотка 🔥\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    # Список фотографий Джуди
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

    # Отправляем фотографии
    await send_photos_to_user(message, judy_photos)


@router.message(F.text == "👩 Кира")
async def handle_kira_photos(message: Message):
    """Обработчик кнопки 'Кира' в фотоальбоме"""
    logger.info(
        f"👩 Получено сообщение 'Кира' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Кира\n\n"
        "Умная и стильная интеллектуалка 🧠\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    # Список фотографий Киры
    kira_photos = [
        "https://storage.imgbly.com/imgbly/6vd8OEA4R8.png",
        "https://storage.imgbly.com/imgbly/mG6EdNHd6t.png",
        "https://storage.imgbly.com/imgbly/mUF96a8NBz.jpg",
        "https://storage.imgbly.com/imgbly/IfraukBSVO.jpg",
        "https://storage.imgbly.com/imgbly/q2TBIHRw2r.png",
        "https://storage.imgbly.com/imgbly/oU44ChD9EE.jpg",
        "https://storage.imgbly.com/imgbly/2qtySqcH84.jpg",
        "https://storage.imgbly.com/imgbly/DqK1fbR0Ld.jpg"
    ]

    # Отправляем фотографии
    await send_photos_to_user(message, kira_photos)


@router.message(F.text == "👩 Нейра")
async def handle_neira_photos(message: Message):
    """Обработчик кнопки 'Нейра' в фотоальбоме"""
    logger.info(
        f"👩 Получено сообщение 'Нейра' от пользователя {message.from_user.id}"
    )

    await message.answer(
        "👩 Нейра\n\n"
        "Мистическая и таинственная волшебница ✨\n\n"
        "Вот мои фотографии для тебя... 💕",
        reply_markup=get_photo_album_keyboard()
    )

    # Список фотографий Нейры
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

    # Отправляем фотографии
    await send_photos_to_user(message, neira_photos)
