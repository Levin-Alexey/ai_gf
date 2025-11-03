"""
Обработчик опросника для настройки профиля пользователя
"""
import logging
from aiogram import Router, F, types
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from crud import (
    update_user_tone,
    get_user_by_telegram_id,
    add_user_interests,
    add_user_goals,
    update_user_about
)
from models import GFTone, GFInterest, GFGoal
from .menu import show_main_menu

router = Router()
logger = logging.getLogger(__name__)


class QuestionnaireStates(StatesGroup):
    """Состояния опросника"""
    choosing_tone = State()
    choosing_interests = State()
    choosing_goals = State()
    waiting_about = State()


async def show_tone_selection(callback: CallbackQuery):
    """Показать выбор тона общения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="😊 Дружелюбный",
                    callback_data="tone:friendly"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💖 Нежный",
                    callback_data="tone:gentle"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😎 Нейтральный",
                    callback_data="tone:neutral"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😏 Саркастичный",
                    callback_data="tone:sarcastic"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎩 Формальный",
                    callback_data="tone:formal"
                )
            ],
        ]
    )

    if callback.message:
        await callback.message.edit_text(
            "🎨 Выбери тон общения, который тебе не нравится:\n\n"
            "😊 Дружелюбный — тёплый и позитивный\n"
            "💖 Нежный — мягкий и заботливый\n"
            "😎 Нейтральный — спокойный и сдержанный\n"
            "😏 Саркастичный — с юмором и иронией\n"
            "🎩 Формальный — вежливый и официальный",
            reply_markup=keyboard
        )


@router.callback_query(F.data == "start_questionnaire")
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Начать опросник"""
    await state.set_state(QuestionnaireStates.choosing_tone)
    await show_tone_selection(callback)


@router.callback_query(F.data.startswith("tone:"))
async def process_tone_selection(callback: CallbackQuery, state: FSMContext):
    """Обработать выбор тона общения"""
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
            f"выбрал тон: {tone_value}"
        )

        # Переходим к выбору интересов
        await state.update_data(selected_interests=[])
        await state.set_state(QuestionnaireStates.choosing_interests)
        await show_interests_selection(callback, [])

        await callback.answer("Тон сохранён!")
    else:
        await callback.answer("Произошла ошибка, попробуй ещё раз")


async def show_interests_selection(
    callback: CallbackQuery,
    selected: list
):
    """Показать выбор интересов"""
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
        check = "✅ " if interest_key in selected else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{check}{emoji} {name}",
                callback_data=f"interest:{interest_key}"
            )
        ])

    # Добавляем кнопку "Готово"
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="✨ ГОТОВО",
            callback_data="interests_done"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if callback.message:
        await callback.message.edit_text(
            "🎯 Выбери свои интересы:\n\n"
            "Можешь выбрать несколько вариантов.\n"
            "Нажми на интерес, чтобы отметить или снять галочку.\n\n"
            "Когда закончишь — нажми «Готово» ✨",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("interest:"))
async def toggle_interest(callback: CallbackQuery, state: FSMContext):
    """Переключить выбор интереса"""
    if not callback.data:
        return

    interest_value = callback.data.split(":")[1]

    # Получаем текущие выбранные интересы
    data = await state.get_data()
    selected = data.get('selected_interests', [])

    # Переключаем выбор
    if interest_value in selected:
        selected.remove(interest_value)
    else:
        selected.append(interest_value)

    # Сохраняем обновленный список
    await state.update_data(selected_interests=selected)

    # Обновляем клавиатуру
    await show_interests_selection(callback, selected)
    await callback.answer()


@router.callback_query(F.data == "interests_done")
async def save_interests(callback: CallbackQuery, state: FSMContext):
    """Сохранить выбранные интересы"""
    data = await state.get_data()
    selected = data.get('selected_interests', [])

    # Преобразуем в enum
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

    interests_enums = [
        interest_map[key] for key in selected if key in interest_map
    ]

    # Сохраняем в базу данных
    async with async_session_maker() as session:
        if interests_enums:
            await add_user_interests(
                session,
                telegram_id=callback.from_user.id,
                interests=interests_enums
            )
        await session.commit()

    logger.info(
        f"Пользователь {callback.from_user.id} "
        f"выбрал интересы: {selected}"
    )

    # Переходим к выбору целей
    await state.update_data(selected_goals=[])
    await state.set_state(QuestionnaireStates.choosing_goals)
    await show_goals_selection(callback, [])

    await callback.answer("Интересы сохранены!")


async def show_goals_selection(callback: CallbackQuery, selected: list):
    """Показать выбор целей"""
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
        check = "✅ " if goal_key in selected else ""
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{check}{emoji} {name}",
                callback_data=f"goal:{goal_key}"
            )
        ])

    # Добавляем кнопку "Готово"
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="✨ ГОТОВО",
            callback_data="goals_done"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if callback.message:
        await callback.message.edit_text(
            "🎯 Для чего ты хочешь использовать бота?\n\n"
            "Можешь выбрать несколько целей.\n"
            "Нажми на цель, чтобы отметить или снять галочку.\n\n"
            "Когда закончишь — нажми «Готово» ✨",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("goal:"))
async def toggle_goal(callback: CallbackQuery, state: FSMContext):
    """Переключить выбор цели"""
    if not callback.data:
        return

    goal_value = callback.data.split(":")[1]

    # Получаем текущие выбранные цели
    data = await state.get_data()
    selected = data.get('selected_goals', [])

    # Переключаем выбор
    if goal_value in selected:
        selected.remove(goal_value)
    else:
        selected.append(goal_value)

    # Сохраняем обновленный список
    await state.update_data(selected_goals=selected)

    # Обновляем клавиатуру
    await show_goals_selection(callback, selected)
    await callback.answer()


@router.callback_query(F.data == "goals_done")
async def save_goals(callback: CallbackQuery, state: FSMContext):
    """Сохранить выбранные цели"""
    data = await state.get_data()
    selected = data.get('selected_goals', [])

    # Преобразуем в enum
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

    goals_enums = [
        goal_map[key] for key in selected if key in goal_map
    ]

    # Сохраняем в базу данных
    async with async_session_maker() as session:
        if goals_enums:
            await add_user_goals(
                session,
                telegram_id=callback.from_user.id,
                goals=goals_enums
            )
        await session.commit()

    logger.info(
        f"Пользователь {callback.from_user.id} "
        f"выбрал цели: {selected}"
    )

    # Переходим к запросу информации о себе
    await state.set_state(QuestionnaireStates.waiting_about)

    if callback.message:
        await callback.message.edit_text(
            "📝 Последний шаг!\n\n"
            "Расскажи кратко о себе. Чем занимаешься? "
            "Что тебя вдохновляет?\n\n"
            "Это поможет мне лучше понять тебя и общаться более персонально. 💫"
        )

    await callback.answer("Цели сохранены!")


@router.message(QuestionnaireStates.waiting_about)
async def save_about(message: types.Message, state: FSMContext):
    """Сохранить информацию о пользователе"""
    about_text = message.text

    if not about_text:
        await message.answer(
            "Пожалуйста, напиши текстом о себе 😊"
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

        # Получаем обновленного пользователя
        user = await get_user_by_telegram_id(
            session,
            telegram_id=message.from_user.id
        )

    logger.info(
        f"Пользователь {message.from_user.id} "
        f"рассказал о себе ({len(about_text)} символов)"
    )

    # Завершаем опросник
    await state.clear()

    # Финальное сообщение после завершения всего опросника
    if user:
        await message.answer(
            f"🎉 Отлично, {user.get_display_name()}!\n\n"
            "Теперь я знаю тебя намного лучше:\n"
            "✅ Твой тон общения\n"
            "✅ Твои интересы\n"
            "✅ Твои цели\n"
            "✅ Информацию о тебе\n\n"
            "Я готова помочь тебе именно так, как тебе нужно! 💫"
        )

        # Сразу показываем главное меню
        await show_main_menu(message, user.get_display_name())
    else:
        await message.answer(
            "✅ Настройка завершена!\n\n"
            "Теперь можем общаться! Напиши мне что-нибудь 😊"
        )
