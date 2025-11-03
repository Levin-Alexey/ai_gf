"""
Обработчик настроек характера
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InaccessibleMessage
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from crud import (
    get_user_by_telegram_id,
    get_active_personas,
    get_user_current_persona,
    set_user_persona,
    get_persona_by_id,
    update_user_tone,
    update_user_interests,
    update_user_goals,
    update_user_about,
    update_flirt_level,
    get_user_persona_setting
)
from models import GFTone, GFInterest, GFGoal

router = Router()
logger = logging.getLogger(__name__)


class CharacterSettingsStates(StatesGroup):
    """Состояния настроек характера"""
    editing_about = State()


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
        
        # Получаем уровень флирта
        async with async_session_maker() as session:
            persona_setting = await get_user_persona_setting(session, user.id)

        flirt_level = (
            persona_setting.overrides.get('flirt_level', 'moderate')
            if persona_setting and persona_setting.overrides
            else 'moderate'
        )

        # Названия уровней флирта
        flirt_level_names = {
            'minimal': 'Минимальный',
            'moderate': 'Умеренный',
            'intense': 'Интенсивный'
        }
        flirt_level_text = flirt_level_names.get(flirt_level, 'Умеренный')

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
            f"💕 Уровень флирта: {flirt_level_text}\n"
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
                        text="💕 Уровень флирта",
                        callback_data="change_flirt_level"
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
                        text="🆘 Обратиться в поддержку",
                        callback_data="support"
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


async def show_flirt_level_selection_for_settings(
    callback: CallbackQuery
):
    """Показать выбор уровня флирта в настройках"""
    # Получаем текущий уровень флирта
    async with async_session_maker() as session:
        persona_setting = await get_user_persona_setting(
            session, user_id=callback.from_user.id
        )

    current_flirt_level = 'moderate'
    if persona_setting and persona_setting.overrides:
        current_flirt_level = persona_setting.overrides.get(
            'flirt_level', 'moderate'
        )

    # Названия уровней флирта
    flirt_level_info = {
        'minimal': (
            '😊', 'Минимальный',
            'Лёгкий флирт, дружелюбный тон без интенсивных намеков'
        ),
        'moderate': (
            '💕', 'Умеренный',
            'Баланс между дружелюбием и романтикой (как сейчас)'
        ),
        'intense': (
            '💋', 'Интенсивный',
            'Активный флирт, игривость и романтичные намеки'
        )
    }

    # Создаем кнопки
    keyboard_buttons = []
    for level_key, (emoji, name, desc) in flirt_level_info.items():
        # Если уровень выбран, добавляем галочку
        check = "✅ " if level_key == current_flirt_level else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{check}{emoji} {name}",
                callback_data=f"flirt_level_settings:{level_key}"
            )
        ])

    # Добавляем кнопку управления
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🔙 Назад к настройкам",
            callback_data="back_to_character_settings"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "💕 Выбери уровень флирта:\n\n"
            "😊 Минимальный — лёгкий флирт, дружелюбный тон\n"
            "💕 Умеренный — баланс между дружелюбием и романтикой\n"
            "💋 Интенсивный — активный флирт, игривость и намеки\n\n"
            "После смены уровня флирта, обязательно нажми кнопку 'Очистить историю' при старте диалога! (Сброс диалога удалит последние сообщения которые помнит бот)",
            reply_markup=keyboard
        )


async def show_interests_selection_for_settings(callback: CallbackQuery):
    """Показать выбор интересов в настройках"""
    # Получаем текущие интересы пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    current_interests = []
    if user and user.interests:
        # Преобразуем enum в строки для сравнения
        current_interests = [interest.value for interest in user.interests]
    # Все доступные интересы с эмодзи
    interests_info = {
        'work': ('💼', 'Работа'),
        'startups': ('🚀', 'Стартапы'),
        'sport': ('⚽', 'Спорт'),
        'movies': ('🎬', 'Фильмы'),
        'games': ('🎮', 'Игры'),
        'music': ('🎵', 'Музыка'),
        'travel': ('✈️', 'Путешествия'),
        'self_growth': ('📈', 'Саморазвитие'),
        'psychology': ('🧠', 'Психология'),
        'ai_tech': ('🤖', 'AI и технологии'),
        'books': ('📚', 'Книги'),
    }

    # Создаем кнопки
    keyboard_buttons = []
    for interest_key, (emoji, name) in interests_info.items():
        # Если интерес выбран, добавляем галочку
        check = "✅ " if interest_key in current_interests else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{check}{emoji} {name}",
                callback_data=f"interest_settings:{interest_key}"
            )
        ])

    # Добавляем кнопки управления
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="✨ Сохранить",
            callback_data="interests_settings_done"
        )
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🔙 Назад к настройкам",
            callback_data="back_to_character_settings"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "🎯 Выбери свои интересы:\n\n"
            "Можешь выбрать несколько вариантов.\n"
            "Нажми на интерес, чтобы отметить или снять галочку.\n\n"
            "Когда закончишь — нажми «Сохранить» ✨",
            reply_markup=keyboard
        )


async def show_goals_selection_for_settings(callback: CallbackQuery):
    """Показать выбор целей в настройках"""
    # Получаем текущие цели пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    current_goals = []
    if user and user.goals:
        # Преобразуем enum в строки для сравнения
        current_goals = [goal.value for goal in user.goals]

    # Все доступные цели с эмодзи
    goals_info = {
        'support': ('🤗', 'Поддержка'),
        'motivation': ('💪', 'Мотивация'),
        'chitchat': ('💬', 'Общение'),
        'advice': ('💡', 'Советы'),
        # 'learn_english': ('🇬🇧', 'Изучение английского'),
        'project_ideas': ('🚀', 'Идеи для проектов'),
        'brainstorm': ('🧠', 'Мозговой штурм'),
        'stress_relief': ('😌', 'Снятие стресса'),
        # 'accountability': ('✅', 'Ответственность'),
        # 'daily_checkin': ('📅', 'Ежедневный чекин'),
    }

    # Создаем кнопки
    keyboard_buttons = []
    for goal_key, (emoji, name) in goals_info.items():
        # Если цель выбрана, добавляем галочку
        check = "✅ " if goal_key in current_goals else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{check}{emoji} {name}",
                callback_data=f"goal_settings:{goal_key}"
            )
        ])

    # Добавляем кнопки управления
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="✨ Сохранить",
            callback_data="goals_settings_done"
        )
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🔙 Назад к настройкам",
            callback_data="back_to_character_settings"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "🎯 Для чего ты хочешь использовать бота?\n\n"
            "Можешь выбрать несколько целей.\n"
            "Нажми на цель, чтобы отметить или снять галочку.\n\n"
            "Когда закончишь — нажми «Сохранить» ✨",
            reply_markup=keyboard
        )


async def show_about_edit_for_settings(callback: CallbackQuery):
    """Показать редактирование информации о себе в настройках"""
    # Получаем текущую информацию о пользователе
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    if not user:
        await callback.answer("⚠️ Пользователь не найден", show_alert=True)
        return

    current_about = user.about or ""

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data="edit_about_text"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Очистить",
                    callback_data="clear_about_text"
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
        if current_about:
            message_text = (
                f"📝 Информация о себе:\n\n"
                f"{current_about}\n\n"
                f"Выбери действие:"
            )
        else:
            message_text = (
                "📝 Информация о себе:\n\n"
                "Пока не заполнено.\n\n"
                "Расскажи о себе, чтобы я могла лучше понимать тебя! 💫"
            )

        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )


async def handle_select_persona(message: Message):
    """Функция для выбора личности"""
    logger.info(
        f"Пользователь {message.from_user.id} запросил выбор личности"
    )

    async with async_session_maker() as session:
        # Получаем всех активных персонажей
        personas = await get_active_personas(session)

        # Получаем текущего пользователя и его выбранную личность
        try:
            user = await get_user_by_telegram_id(
                session, telegram_id=message.from_user.id
            )
        except Exception:
            user = None
        current_persona = None
        if user:
            try:
                current_persona = await get_user_current_persona(
                    session, user.id
                )
            except Exception:
                current_persona = None

        logger.info(f"Найдено {len(personas)} активных персонажей")

        if not personas:
            logger.warning("Нет активных персонажей в базе данных")
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
            "Нажми на кнопку под картинкой, чтобы выбрать:\n\n"
            "После смены личности, обязательно нажми кнопку 'Очистить историю' при старте диалога! (Сброс диалога удалит последние сообщения которые помнит бот)",
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
            logger.info(
                f"Отправляем персонажа: {persona.name} (ID: {persona.id})"
            )

            # Создаем кнопки для выбора/индикации выбранной личности
            keyboard_buttons = [[
                InlineKeyboardButton(
                    text=f"{emoji} Выбрать {persona.name}",
                    callback_data=f"select_persona_{persona.id}"
                )
            ]]

            # Если эта личность уже выбрана у пользователя — добавляем нижнюю кнопку-индикатор
            if current_persona and current_persona.id == persona.id:
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text="✅ Выбрана эта личность",
                        callback_data="current_persona"
                    )
                ])

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

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
                    logger.info(f"Отправлено фото для {persona.name}")
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
    await show_interests_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("interest_settings:"))
async def toggle_interest_for_settings(callback: CallbackQuery):
    """Переключить выбор интереса в настройках"""
    if not callback.data:
        return

    interest_value = callback.data.split(":")[1]

    # Получаем текущие интересы пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    if not user:
        await callback.answer("⚠️ Пользователь не найден", show_alert=True)
        return

    current_interests = []
    if user.interests:
        current_interests = [interest.value for interest in user.interests]

    # Переключаем выбор
    if interest_value in current_interests:
        current_interests.remove(interest_value)
    else:
        current_interests.append(interest_value)

    # Обновляем интересы пользователя
    interest_map = {
        'work': GFInterest.WORK,
        'startups': GFInterest.STARTUPS,
        'sport': GFInterest.SPORT,
        'movies': GFInterest.MOVIES,
        'games': GFInterest.GAMES,
        'music': GFInterest.MUSIC,
        'travel': GFInterest.TRAVEL,
        'self_growth': GFInterest.SELF_GROWTH,
        'psychology': GFInterest.PSYCHOLOGY,
        'ai_tech': GFInterest.AI_TECH,
        'books': GFInterest.BOOKS,
    }

    # Преобразуем в enum
    interests_enums = [
        interest_map[key] for key in current_interests if key in interest_map
    ]

    # Сохраняем изменения
    async with async_session_maker() as session:
        await update_user_interests(
            session, callback.from_user.id, interests_enums
        )
        await session.commit()

    # Обновляем клавиатуру
    await show_interests_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data == "interests_settings_done")
async def save_interests_for_settings(callback: CallbackQuery):
    """Сохранить выбранные интересы в настройках"""
    # Получаем текущие интересы пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    if not user:
        await callback.answer("⚠️ Пользователь не найден", show_alert=True)
        return

    # Формируем список выбранных интересов
    interests_list = []
    if user.interests:
        interest_names = {
            'work': 'Работа',
            'startups': 'Стартапы',
            'sport': 'Спорт',
            'movies': 'Фильмы',
            'games': 'Игры',
            'music': 'Музыка',
            'travel': 'Путешествия',
            'self_growth': 'Саморазвитие',
            'psychology': 'Психология',
            'ai_tech': 'AI и технологии',
            'books': 'Книги',
        }

        interests_list = [
            interest_names.get(interest.value, interest.value)
            for interest in user.interests
        ]

    if interests_list:
        interests_text = "• " + "\n• ".join(interests_list)
        message_text = (
            f"✅ Интересы обновлены!\n\n"
            f"📋 Твои интересы:\n{interests_text}\n\n"
            f"Теперь я буду учитывать их в наших разговорах! 💫"
        )
    else:
        message_text = (
            "✅ Интересы обновлены!\n\n"
            "📋 У тебя пока нет выбранных интересов.\n"
            "Можешь добавить их позже в настройках! 💫"
        )

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            message_text,
            parse_mode="Markdown"
        )

    await callback.answer("Интересы сохранены!")


@router.callback_query(F.data == "my_goals")
async def handle_my_goals_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои цели'"""
    await show_goals_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("goal_settings:"))
async def toggle_goal_for_settings(callback: CallbackQuery):
    """Переключить выбор цели в настройках"""
    if not callback.data:
        return

    goal_value = callback.data.split(":")[1]

    # Получаем текущие цели пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    if not user:
        await callback.answer("⚠️ Пользователь не найден", show_alert=True)
        return

    current_goals = []
    if user.goals:
        current_goals = [goal.value for goal in user.goals]

    # Переключаем выбор
    if goal_value in current_goals:
        current_goals.remove(goal_value)
    else:
        current_goals.append(goal_value)

    # Обновляем цели пользователя
    goal_map = {
        'support': GFGoal.SUPPORT,
        'motivation': GFGoal.MOTIVATION,
        'chitchat': GFGoal.CHITCHAT,
        'advice': GFGoal.ADVICE,
        # 'learn_english': GFGoal.LEARN_ENGLISH,
        'project_ideas': GFGoal.PROJECT_IDEAS,
        'brainstorm': GFGoal.BRAINSTORM,
        'stress_relief': GFGoal.STRESS_RELIEF,
        # 'accountability': GFGoal.ACCOUNTABILITY,
        # 'daily_checkin': GFGoal.DAILY_CHECKIN,
    }

    # Преобразуем в enum
    goals_enums = [
        goal_map[key] for key in current_goals if key in goal_map
    ]

    # Сохраняем изменения
    async with async_session_maker() as session:
        await update_user_goals(
            session, callback.from_user.id, goals_enums
        )
        await session.commit()

    # Обновляем клавиатуру
    await show_goals_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data == "goals_settings_done")
async def save_goals_for_settings(callback: CallbackQuery):
    """Сохранить выбранные цели в настройках"""
    # Получаем текущие цели пользователя
    async with async_session_maker() as session:
        user = await get_user_by_telegram_id(
            session, telegram_id=callback.from_user.id
        )

    if not user:
        await callback.answer("⚠️ Пользователь не найден", show_alert=True)
        return

    # Формируем список выбранных целей
    goals_list = []
    if user.goals:
        goal_names = {
            'support': 'Поддержка',
            'motivation': 'Мотивация',
            'chitchat': 'Общение',
            'advice': 'Советы',
            # 'learn_english': 'Изучение английского',
            'project_ideas': 'Идеи для проектов',
            'brainstorm': 'Мозговой штурм',
            'stress_relief': 'Снятие стресса',
            # 'accountability': 'Ответственность',
            # 'daily_checkin': 'Ежедневный чекин',
        }

        goals_list = [
            goal_names.get(goal.value, goal.value)
            for goal in user.goals
        ]

    if goals_list:
        goals_text = "• " + "\n• ".join(goals_list)
        message_text = (
            f"✅ Цели обновлены!\n\n"
            f"🎯 Твои цели:\n{goals_text}\n\n"
            f"Теперь я буду помогать тебе в этих направлениях! 💫"
        )
    else:
        message_text = (
            "✅ Цели обновлены!\n\n"
            "🎯 У тебя пока нет выбранных целей.\n"
            "Можешь добавить их позже в настройках! 💫"
        )

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            message_text,
            parse_mode="Markdown"
        )

    await callback.answer("Цели сохранены!")


@router.callback_query(F.data == "about_me")
async def handle_about_me_callback(callback: CallbackQuery):
    """Обработчик кнопки 'О себе'"""
    await show_about_edit_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data == "edit_about_text")
async def handle_edit_about_text_callback(
    callback: CallbackQuery, state: FSMContext
):
    """Обработчик кнопки 'Редактировать' информацию о себе"""
    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "✏️ Расскажи о себе:\n\n"
            "Чем занимаешься? Что тебя вдохновляет?\n"
            "Какие у тебя планы и мечты?\n\n"
            "Просто напиши текстом, и я сохраню эту информацию! 💫"
        )

    # Устанавливаем состояние ожидания текста
    await state.set_state(CharacterSettingsStates.editing_about)
    await callback.answer()


@router.callback_query(F.data == "clear_about_text")
async def handle_clear_about_text_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Очистить' информацию о себе"""
    # Очищаем информацию о себе
    async with async_session_maker() as session:
        await update_user_about(session, callback.from_user.id, "")
        await session.commit()

    logger.info(
        f"Пользователь {callback.from_user.id} очистил информацию о себе"
    )

    if callback.message and hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(
            "🗑 Информация о себе очищена!\n\n"
            "Если захочешь рассказать о себе снова, "
            "можешь использовать кнопку «Редактировать» 💫"
        )

    await callback.answer("Информация очищена!")


@router.message(CharacterSettingsStates.editing_about)
async def save_about_for_settings(message: Message, state: FSMContext):
    """Сохранить информацию о себе в настройках"""
    about_text = message.text

    if not about_text:
        await message.answer(
            "Пожалуйста, напиши текстом о себе 😊"
        )
        return

    # Проверяем длину текста
    if len(about_text) > 1000:
        await message.answer(
            "Текст слишком длинный! Пожалуйста, сократи до 1000 символов 😊"
        )
        return

    # Сохраняем в базу данных
    async with async_session_maker() as session:
        await update_user_about(
            session,
            telegram_id=message.from_user.id,
            about=about_text
        )
        await session.commit()

    logger.info(
        f"Пользователь {message.from_user.id} "
        f"обновил информацию о себе ({len(about_text)} символов)"
    )

    # Завершаем состояние
    await state.clear()

    # Показываем подтверждение
    await message.answer(
        f"✅ Информация о себе обновлена!\n\n"
        f"📝 Твоя информация:\n{about_text}\n\n"
        f"Теперь я буду лучше понимать тебя! 💫"
    )


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
        logger.error("Получен пустой callback_data")
        return

    try:
        persona_id = int(callback.data.split("_")[2])
        logger.info(
            f"Пользователь {callback.from_user.id} выбирает "
            f"персонажа ID: {persona_id}"
        )
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка парсинга persona_id из {callback.data}: {e}")
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    async with async_session_maker() as session:
        # Получаем персонажа по ID
        selected_persona = await get_persona_by_id(session, persona_id)

        if not selected_persona:
            logger.warning(f"Персонаж с ID {persona_id} не найден")
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
            logger.warning(f"Пользователь {callback.from_user.id} не найден")
            await callback.answer(
                "⚠️ Сначала нужно пройти настройку", show_alert=True
            )
            return

        try:
            # Устанавливаем персонажа для пользователя
            await set_user_persona(session, user.id, selected_persona.id)
            await session.commit()
            
            logger.info(
                f"Пользователь {callback.from_user.id} успешно выбрал "
                f"персонажа {selected_persona.name}"
            )

            # Обновляем сообщение
            if callback.message and not isinstance(
                callback.message, InaccessibleMessage
            ):
                success_text = (
                    f"✅ Личность **{selected_persona.name}** выбрана!\n\n"
                    f"Теперь я буду общаться с тобой в образе "
                    f"{selected_persona.name}.\n\n"
                    f"**{selected_persona.short_desc}**\n\n"
                    f"Можешь начать чат и почувствовать разницу! 💫"
                )

                # Проверяем тип сообщения
                if (hasattr(callback.message, 'photo') and
                        callback.message.photo):
                    # Если это фото, используем edit_caption
                    try:
                        await callback.message.edit_caption(
                            caption=success_text,
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Не удалось изменить caption: {e}"
                        )
                        # Если не получилось, удаляем и отправляем
                        # новое сообщение
                        try:
                            await callback.message.delete()
                        except Exception:
                            pass
                        await callback.message.answer(
                            success_text,
                            parse_mode="Markdown"
                        )
                elif hasattr(callback.message, 'edit_text'):
                    # Если это текстовое сообщение, редактируем его
                    await callback.message.edit_text(
                        success_text,
                        parse_mode="Markdown"
                    )
                else:
                    # Если ничего не получилось, просто удаляем и
                    # отправляем новое
                    try:
                        await callback.message.delete()
                    except Exception:
                        pass
                    await callback.message.answer(
                        success_text,
                        parse_mode="Markdown"
                    )

            await callback.answer(
                f"Выбрана личность: {selected_persona.name}"
            )

        except Exception as e:
            logger.error(
                f"Ошибка при установке персонажа {selected_persona.name} "
                f"для пользователя {callback.from_user.id}: {e}"
            )
            await callback.answer(
                "❌ Произошла ошибка при выборе личности", show_alert=True
            )


@router.callback_query(F.data == "change_flirt_level")
async def handle_change_flirt_level_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Изменить уровень флирта'"""
    await show_flirt_level_selection_for_settings(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("flirt_level_settings:"))
async def process_flirt_level_selection_for_settings(
    callback: CallbackQuery
):
    """Обработать выбор уровня флирта в настройках"""
    if not callback.data:
        return

    flirt_level = callback.data.split(":")[1]

    # Проверяем корректность уровня
    if flirt_level not in ['minimal', 'moderate', 'intense']:
        await callback.answer(
            "Ошибка: неверный уровень флирта", show_alert=True
        )
        return

    if callback.message:
        # Получаем пользователя
        async with async_session_maker() as session:
            user = await get_user_by_telegram_id(
                session,
                telegram_id=callback.from_user.id
            )

        if not user:
            await callback.answer(
                "⚠️ Пользователь не найден", show_alert=True
            )
            return

        # Сохраняем в базу данных
        async with async_session_maker() as session:
            await update_flirt_level(session, user.id, flirt_level)
            await session.commit()

        logger.info(
            f"Пользователь {callback.from_user.id} "
            f"изменил уровень флирта на: {flirt_level}"
        )

        # Названия уровней для отображения
        flirt_level_names = {
            'minimal': 'Минимальный',
            'moderate': 'Умеренный',
            'intense': 'Интенсивный'
        }

        flirt_level_emoji = {
            'minimal': '😊',
            'moderate': '💕',
            'intense': '💋'
        }

        # Показываем подтверждение
        if hasattr(callback.message, 'edit_text'):
            await callback.message.edit_text(
                f"{flirt_level_emoji[flirt_level]} Уровень флирта "
                f"изменён на **{flirt_level_names[flirt_level]}**!\n\n"
                f"Теперь я буду общаться с тобой на этом уровне. "
                f"Можешь начать чат и почувствовать разницу! 💫",
                parse_mode="Markdown"
            )

        await callback.answer("Уровень флирта изменён!")


@router.callback_query(F.data == "back_to_character_settings")
async def handle_back_to_character_settings_callback(
    callback: CallbackQuery
):
    """Обработчик кнопки 'Назад к настройкам'"""
    if callback.message and hasattr(callback.message, 'delete'):
        await callback.message.delete()
        await handle_character_settings(callback.message)
    await callback.answer()


@router.callback_query(F.data == "current_persona")
async def handle_current_persona_callback(callback: CallbackQuery):
    """Информируем, что эта личность уже выбрана"""
    await callback.answer("У тебя уже выбрана эта личность")


@router.callback_query(F.data == "support")
async def handle_support_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Обратиться в поддержку'"""
    logger.info(
        f"🆘 SUPPORT: Получен callback поддержки от пользователя "
        f"{callback.from_user.id}"
    )

    if callback.message:
        await callback.message.answer(
            "🆘 Служба поддержки\n\n"
            "Для обращения в поддержку напишите:\n"
            "https://t.me/AIGFSupport"
        )

    await callback.answer()
