"""
Обработчик настроек характера
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
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
    get_persona_by_id,
    update_user_tone
)
from models import GFTone

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🤖 Настройки")
async def handle_character_settings(message: Message):
    """Обработчик кнопки 'Настроить характер'"""
    logger.info(
        f"🎨 Получено сообщение 'Настроить характер' "
        f"от пользователя {message.from_user.id}"
    )
    await _show_character_settings(message)


async def _show_character_settings(message: Message, from_user=None):
    """Общая функция для показа настроек характера"""
    if not message:
        return
    user_id = from_user.id if from_user else message.from_user.id

    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=user_id
        )

    if user:
        # Получаем текущую личность
        async with async_session_maker() as session:
            current_persona = await get_user_current_persona(
                session, user.id
            )

        # Формируем информацию о текущих настройках характера
        tone_text = user.tone.value if user.tone else "Не установлен"
        interests_count = len(user.interests) if user.interests else 0
        goals_count = len(user.goals) if user.goals else 0
        persona_text = (
            current_persona.name if current_persona else "Не выбрана"
        )

        character_text = (
            f"🎨 Настройки характера:\n\n"
            f"👤 Личность: {persona_text}\n"
            f"🎨 Тон общения: {tone_text}\n"
            f"🎯 Интересов: {interests_count}\n"
            f"🎯 Целей: {goals_count}\n"
            f"📝 О себе: "
            f"{'Заполнено' if user.about else 'Не заполнено'}\n\n"
            f"Выбери, что хочешь изменить:"
        )
        # Создаем inline клавиатуру
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👤 Выбрать личность",
                        callback_data="select_persona"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎨 Изменить тон общения",
                        callback_data="change_tone"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎯 Мои интересы",
                        callback_data="my_interests"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎯 Мои цели",
                        callback_data="my_goals"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📝 О себе",
                        callback_data="about_me"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Назад к настройкам",
                        callback_data="back_to_settings"
                    )
                ]
            ]
        )
        await message.answer(character_text, reply_markup=keyboard)
    else:
        await message.answer(
            "⚠️ Сначала нужно пройти настройку. Напиши /start"
        )


async def show_tone_selection_for_settings(callback: CallbackQuery):
    """Показать выбор тона общения в настройках"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="😊 Дружелюбный",
                    callback_data="tone_settings:friendly"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💖 Нежный",
                    callback_data="tone_settings:gentle"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😎 Нейтральный",
                    callback_data="tone_settings:neutral"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😏 Саркастичный",
                    callback_data="tone_settings:sarcastic"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎩 Формальный",
                    callback_data="tone_settings:formal"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад к настройкам",
                    callback_data="back_to_character_settings"
                )
            ]
        ]
    )

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "🎨 Выбери новый тон общения:\n\n"
            "😊 Дружелюбный — тёплый и позитивный\n"
            "💖 Нежный — мягкий и заботливый\n"
            "😎 Нейтральный — спокойный и сдержанный\n"
            "😏 Саркастичный — с юмором и иронией\n"
            "🎩 Формальный — вежливый и официальный",
            reply_markup=keyboard
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
                "Функция в разработке... "
                "Скоро здесь можно будет выбрать личность! ✨"
            )
            return

        # Отправляем заголовок
        await message.answer(
            "👤 Выбери личность для общения:\n\n"
            "Нажми на кнопку под картинкой, чтобы выбрать:",
            parse_mode="Markdown"
        )

        # Эмодзи-аватары для каждого персонажа
        persona_emojis = {
            'Нейра': '🌌',  # космос
            'Фокс': '🕵️',   # детектив
            'Лина': '☕',    # уют
            'Эва': '📚',     # книги/культура
            'Рейна': '💻'    # хакер
        }

        # Отправляем каждую личность отдельным сообщением
        for persona in personas:
            emoji = persona_emojis.get(persona.name, '👤')

            # Создаем кнопку для выбора этой личности
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{emoji} Выбрать {persona.name}",
                            callback_data=f"select_persona_{persona.id}"
                        )
                    ]
                ]
            )

            # Формируем описание
            caption = (
                f"👤 **{persona.name}**\n\n{persona.short_desc}"
            )

            # Если есть аватар, отправляем фото с описанием и кнопкой
            if persona.avatar_url:
                try:
                    await message.answer_photo(
                        photo=persona.avatar_url,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(
                        f"Не удалось отправить изображение "
                        f"для {persona.name}: {e}"
                    )
                    # Если не удалось отправить фото, отправляем текст
                    await message.answer(
                        caption,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
            else:
                # Если нет аватара, отправляем только текст с кнопкой
                await message.answer(
                    caption,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )

        # Добавляем кнопку "Назад"
        back_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Назад к настройкам",
                        callback_data="back_to_character_settings"
                    )
                ]
            ]
        )
        await message.answer(
            "Или вернись назад:", reply_markup=back_keyboard
        )


# Callback обработчики
@router.callback_query(F.data == "select_persona")
async def handle_select_persona_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Выбрать личность'"""
    if callback.message and hasattr(callback.message, 'answer'):
        await handle_select_persona(callback.message)
    await callback.answer()


@router.callback_query(F.data == "change_tone")
async def handle_change_tone_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Изменить тон общения'"""
    await show_tone_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("tone_settings:"))
async def process_tone_selection_for_settings(callback: CallbackQuery):
    """Обработать выбор тона общения в настройках"""
    if not callback.data:
        return

    tone_value = callback.data.split(":")[1]

    # Словарь для перевода значений в enum
    tone_map = {
        'friendly': GFTone.FRIENDLY,
        'gentle': GFTone.GENTLE,
        'neutral': GFTone.NEUTRAL,
        'sarcastic': GFTone.SARCASTIC,
        'formal': GFTone.FORMAL,
    }

    selected_tone = tone_map.get(tone_value)

    if selected_tone and callback.message:
        # Сохраняем в базу данных
        async with async_session_maker() as session:
            await update_user_tone(
                session,
                telegram_id=callback.from_user.id,
                tone=selected_tone
            )
            await session.commit()

        logger.info(
            f"Пользователь {callback.from_user.id} "
            f"изменил тон на: {tone_value}"
        )

        # Показываем подтверждение и возвращаемся к настройкам
        tone_names = {
            'friendly': 'Дружелюбный',
            'gentle': 'Нежный',
            'neutral': 'Нейтральный',
            'sarcastic': 'Саркастичный',
            'formal': 'Формальный',
        }

        if hasattr(callback.message, 'edit_text'):
            await callback.message.edit_text(
                f"✅ Тон общения изменён на **{tone_names[tone_value]}**!\n\n"
                f"Теперь я буду общаться с тобой в этом стиле. "
                f"Можешь начать чат и почувствовать разницу! 💫",
                parse_mode="Markdown"
            )

        await callback.answer("Тон общения изменён!")
    else:
        await callback.answer("Произошла ошибка, попробуй ещё раз")


@router.callback_query(F.data == "my_interests")
async def handle_my_interests_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои интересы'"""
    if callback.message:
        await callback.message.answer(
            "🎯 Мои интересы - функция в разработке!"
        )
    await callback.answer()


@router.callback_query(F.data == "my_goals")
async def handle_my_goals_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои цели'"""
    if callback.message:
        await callback.message.answer(
            "🎯 Мои цели - функция в разработке!"
        )
    await callback.answer()


@router.callback_query(F.data == "about_me")
async def handle_about_me_callback(callback: CallbackQuery):
    """Обработчик кнопки 'О себе'"""
    if callback.message:
        await callback.message.answer(
            "📝 О себе - функция в разработке!"
        )
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def handle_back_to_settings_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад к настройкам'"""
    from .menu import handle_settings
    if callback.message:
        await handle_settings(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("select_persona_"))
async def handle_persona_selection_callback(callback: CallbackQuery):
    """Обработчик выбора конкретной личности через callback"""
    if not callback.data:
        return

    persona_id = int(callback.data.split("_")[2])

    async with async_session_maker() as session:
        # Получаем персонажа по ID
        selected_persona = await get_persona_by_id(session, persona_id)

        if not selected_persona:
            await callback.answer(
                "❌ Персонаж не найден", show_alert=True
            )
            return

        # Получаем пользователя
        user = await get_user_by_telegram_id(
            session,
            telegram_id=callback.from_user.id
        )

        if not user:
            await callback.answer(
                "⚠️ Сначала нужно пройти настройку", show_alert=True
            )
            return

        # Устанавливаем персонажа для пользователя
        await set_user_persona(session, user.id, selected_persona.id)
        await session.commit()

        # Обновляем сообщение
        if callback.message and hasattr(callback.message, 'edit_text'):
            await callback.message.edit_text(
                f"✅ Личность **{selected_persona.name}** выбрана!\n\n"
                f"Теперь я буду общаться с тобой в образе "
                f"{selected_persona.name}.\n\n"
                f"**{selected_persona.short_desc}**\n\n"
                f"Можешь начать чат и почувствовать разницу! 💫",
                parse_mode="Markdown"
            )

        await callback.answer(
            f"Выбрана личность: {selected_persona.name}"
        )


@router.callback_query(F.data == "back_to_character_settings")
async def handle_back_to_character_settings_callback(
    callback: CallbackQuery
):
    """Обработчик кнопки 'Назад к настройкам'"""
    if callback.message and hasattr(callback.message, 'delete'):
        await callback.message.delete()
        await handle_character_settings(callback.message)
    await callback.answer()
