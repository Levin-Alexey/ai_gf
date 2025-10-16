"""
Обработчик настроек характера
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from database import async_session_maker
from crud import (
    get_user_by_telegram_id, 
    get_active_personas, 
    get_user_current_persona, 
    set_user_persona,
    get_persona_by_id
)

router = Router()
logger = logging.getLogger(__name__)


async def send_persona_images(message: Message, personas):
    """Отправляет изображения персонажей"""
    try:
        # Словарь с URL изображений персонажей (можно заменить на реальные URL)
        persona_images = {
            'Нейра': 'https://example.com/neira.jpg',  # Заменить на реальные URL
            'Фокс': 'https://example.com/fox.jpg',
            'Лина': 'https://example.com/lina.jpg', 
            'Эва': 'https://example.com/eva.jpg',
            'Рейна': 'https://example.com/reyna.jpg'
        }
        
        # Отправляем изображения для персонажей, у которых есть URL
        for persona in personas:
            if persona.avatar_url:
                try:
                    await message.answer_photo(
                        photo=persona.avatar_url,
                        caption=f"👤 **{persona.name}**\n{persona.short_desc}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить изображение для {persona.name}: {e}")
                    
    except Exception as e:
        logger.error(f"Ошибка при отправке изображений персонажей: {e}")


def get_character_settings_keyboard():
    """Создать клавиатуру настроек характера"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Выбрать личность")],
            [KeyboardButton(text="🎨 Изменить тон общения")],
            [KeyboardButton(text="🎯 Настроить интересы")],
            [KeyboardButton(text="🎯 Настроить цели")],
            [KeyboardButton(text="📝 Изменить информацию о себе")],
            [KeyboardButton(text="🔙 Назад к настройкам")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "🎨 Настроить характер")
async def handle_character_settings(message: Message):
    """Обработчик кнопки 'Настроить характер'"""
    logger.info(f"🎨 Получено сообщение 'Настроить характер' от пользователя {message.from_user.id}")
    await _show_character_settings(message)




async def _show_character_settings(message: Message, from_user=None):
    """Общая функция для показа настроек характера"""
    if not message:
        return
    user_id = from_user.id if from_user else message.from_user.id
    
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(session, telegram_id=user_id)

    if user:
        # Получаем текущую личность
        async with async_session_maker() as session:
            current_persona = await get_user_current_persona(session, user.id)
        
        # Формируем информацию о текущих настройках характера
        tone_text = user.tone.value if user.tone else "Не установлен"
        interests_count = len(user.interests) if user.interests else 0
        goals_count = len(user.goals) if user.goals else 0
        persona_text = current_persona.name if current_persona else "Не выбрана"

        character_text = (
            f"🎨 Настройки характера:\n\n"
            f"👤 Личность: {persona_text}\n"
            f"🎨 Тон общения: {tone_text}\n"
            f"🎯 Интересов: {interests_count}\n"
            f"🎯 Целей: {goals_count}\n"
            f"📝 О себе: {'Заполнено' if user.about else 'Не заполнено'}\n\n"
            f"Выбери, что хочешь изменить:"
        )
        await message.answer(
            character_text,
            reply_markup=get_character_settings_keyboard()
        )
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )


@router.message(F.text == "🎨 Изменить тон общения")
async def handle_change_tone(message: Message):
    """Обработчик кнопки 'Изменить тон общения'"""
    await message.answer(
        "🎨 Изменение тона общения\n\n"
        "Функция в разработке... Скоро здесь можно будет выбрать тон! 💫"
    )


@router.message(F.text == "🎯 Настроить интересы")
async def handle_setup_interests(message: Message):
    """Обработчик кнопки 'Настроить интересы'"""
    await message.answer(
        "🎯 Настройка интересов\n\n"
        "Функция в разработке... Скоро здесь можно будет настроить интересы! ✨"
    )


@router.message(F.text == "🎯 Настроить цели")
async def handle_setup_goals(message: Message):
    """Обработчик кнопки 'Настроить цели'"""
    await message.answer(
        "🎯 Настройка целей\n\n"
        "Функция в разработке... Скоро здесь можно будет настроить цели! 🎯"
    )


@router.message(F.text == "📝 Изменить информацию о себе")
async def handle_change_about(message: Message):
    """Обработчик кнопки 'Изменить информацию о себе'"""
    await message.answer(
        "📝 Изменение информации о себе\n\n"
        "Функция в разработке... Скоро здесь можно изменить информацию! 📝"
    )


@router.message(F.text == "👤 Выбрать личность")
async def handle_select_persona(message: Message):
    """Обработчик кнопки 'Выбрать личность'"""
    async with async_session_maker() as session:
        # Получаем всех активных персонажей
        personas = await get_active_personas(session)
        
        if not personas:
            await message.answer(
                "👤 Выбор личности\n\n"
                "К сожалению, пока нет доступных личностей. "
                "Функция в разработке... Скоро здесь можно будет выбрать личность! ✨"
            )
            return
        
        # Создаем обычную клавиатуру с персонажами
        keyboard_buttons = []
        
        # Эмодзи-аватары для каждого персонажа
        persona_emojis = {
            'Нейра': '🌌',  # космос
            'Фокс': '🕵️',   # детектив
            'Лина': '☕',    # уют
            'Эва': '📚',     # книги/культура
            'Рейна': '💻'    # хакер
        }
        
        for persona in personas:
            emoji = persona_emojis.get(persona.name, '👤')
            keyboard_buttons.append([
                KeyboardButton(text=f"{emoji} {persona.name}")
            ])
        
        # Добавляем кнопку "Назад"
        keyboard_buttons.append([
            KeyboardButton(text="🔙 Назад к настройкам")
        ])
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        # Формируем описание персонажей
        personas_text = "👤 Выбери личность для общения:\n\n"
        for persona in personas:
            personas_text += f"👤 **{persona.name}**\n{persona.short_desc}\n\n"
        
        # Отправляем сообщение с кнопками
        await message.answer(
            personas_text, 
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        # Отправляем изображения персонажей (если есть)
        await send_persona_images(message, personas)




@router.message(F.text == "🔙 Назад к настройкам характера")
async def handle_back_to_character_settings(message: Message):
    """Обработчик кнопки 'Назад к настройкам характера'"""
    await handle_character_settings(message)


@router.message(F.text == "🔙 Назад к настройкам")
async def handle_back_to_settings(message: Message):
    """Обработчик кнопки 'Назад к настройкам'"""
    from .menu import handle_settings
    await handle_settings(message)


# Обработчики выбора персонажей
@router.message(F.text == "🌌 Нейра")
async def handle_select_neira(message: Message):
    """Обработчик выбора Нейры"""
    await _select_persona_by_name(message, "Нейра")


@router.message(F.text == "🕵️ Фокс")
async def handle_select_fox(message: Message):
    """Обработчик выбора Фокса"""
    await _select_persona_by_name(message, "Фокс")


@router.message(F.text == "☕ Лина")
async def handle_select_lina(message: Message):
    """Обработчик выбора Лины"""
    await _select_persona_by_name(message, "Лина")


@router.message(F.text == "📚 Эва")
async def handle_select_eva(message: Message):
    """Обработчик выбора Эвы"""
    await _select_persona_by_name(message, "Эва")


@router.message(F.text == "💻 Рейна")
async def handle_select_reyna(message: Message):
    """Обработчик выбора Рейны"""
    await _select_persona_by_name(message, "Рейна")


async def _select_persona_by_name(message: Message, persona_name: str):
    """Общая функция для выбора персонажа по имени"""
    async with async_session_maker() as session:
        # Получаем персонажа по имени
        persona = await get_persona_by_key(session, persona_name.lower())
        
        if not persona:
            await message.answer("❌ Персонаж не найден")
            return
        
        # Получаем пользователя
        user = await get_user_by_telegram_id(session, telegram_id=message.from_user.id)
        
        if not user:
            await message.answer("⚠️ Сначала нужно пройти настройку")
            return
        
        # Устанавливаем персонажа для пользователя
        await set_user_persona(session, user.id, persona.id)
        await session.commit()
        
        # Отправляем подтверждение
        await message.answer(
            f"✅ Личность **{persona.name}** выбрана!\n\n"
            f"Теперь я буду общаться с тобой в образе {persona.name}.\n\n"
            f"**{persona.short_desc}**\n\n"
            f"Можешь начать чат и почувствовать разницу! 💫",
            parse_mode="Markdown",
            reply_markup=get_character_settings_keyboard()
        )
