"""
Обработчик настроек характера
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
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
        # Создаем inline клавиатуру
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👤 Выбрать личность", callback_data="select_persona")],
                [InlineKeyboardButton(text="🎨 Изменить тон общения", callback_data="change_tone")],
                [InlineKeyboardButton(text="🎯 Мои интересы", callback_data="my_interests")],
                [InlineKeyboardButton(text="🎯 Мои цели", callback_data="my_goals")],
                [InlineKeyboardButton(text="📝 О себе", callback_data="about_me")],
                [InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="back_to_settings")]
            ]
        )
        await message.answer(character_text, reply_markup=keyboard)
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )




async def handle_select_persona(message: Message):
    """Функция для выбора личности"""
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
        
        # Создаем inline клавиатуру с персонажами
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
                InlineKeyboardButton(
                    text=f"{emoji} {persona.name}",
                    callback_data=f"select_persona_{persona.id}"
                )
            ])
        
        # Добавляем кнопку "Назад"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="🔙 Назад к настройкам",
                callback_data="back_to_character_settings"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
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






# Callback обработчики
@router.callback_query(F.data == "select_persona")
async def handle_select_persona_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Выбрать личность'"""
    await handle_select_persona(callback.message)
    await callback.answer()


@router.callback_query(F.data == "change_tone")
async def handle_change_tone_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Изменить тон общения'"""
    await callback.message.answer("🎨 Изменение тона общения - функция в разработке!")
    await callback.answer()


@router.callback_query(F.data == "my_interests")
async def handle_my_interests_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои интересы'"""
    await callback.message.answer("🎯 Мои интересы - функция в разработке!")
    await callback.answer()


@router.callback_query(F.data == "my_goals")
async def handle_my_goals_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои цели'"""
    await callback.message.answer("🎯 Мои цели - функция в разработке!")
    await callback.answer()


@router.callback_query(F.data == "about_me")
async def handle_about_me_callback(callback: CallbackQuery):
    """Обработчик кнопки 'О себе'"""
    await callback.message.answer("📝 О себе - функция в разработке!")
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def handle_back_to_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад к настройкам'"""
    from .menu import handle_settings
    await handle_settings(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("select_persona_"))
async def handle_persona_selection_callback(callback: CallbackQuery):
    """Обработчик выбора конкретной личности через callback"""
    persona_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        # Получаем персонажа по ID
        selected_persona = await get_persona_by_id(session, persona_id)
        
        if not selected_persona:
            await callback.answer("❌ Персонаж не найден", show_alert=True)
            return
        
        # Получаем пользователя
        user = await get_user_by_telegram_id(
            session,
            telegram_id=callback.from_user.id
        )
        
        if not user:
            await callback.answer("⚠️ Сначала нужно пройти настройку", show_alert=True)
            return
        
        # Устанавливаем персонажа для пользователя
        await set_user_persona(session, user.id, selected_persona.id)
        await session.commit()
        
        # Обновляем сообщение
        await callback.message.edit_text(
            f"✅ Личность **{selected_persona.name}** выбрана!\n\n"
            f"Теперь я буду общаться с тобой в образе {selected_persona.name}.\n\n"
            f"**{selected_persona.short_desc}**\n\n"
            f"Можешь начать чат и почувствовать разницу! 💫",
            parse_mode="Markdown"
        )
        
        await callback.answer(f"Выбрана личность: {selected_persona.name}")


@router.callback_query(F.data == "back_to_character_settings")
async def handle_back_to_character_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад к настройкам'"""
    await callback.message.delete()
    await handle_character_settings(callback.message)
    await callback.answer()


