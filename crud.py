"""
CRUD операции для работы с базой данных
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    User, GFTone, GFInterest, GFGoal, Persona, UserPersonaSetting
)


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Получить пользователя по telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> User:
    """Создать нового пользователя (только базовая информация)"""
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        interests=[],  # Пустой массив вместо None
        goals=[],      # Пустой массив вместо None
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> tuple[User, bool]:
    """
    Получить пользователя или создать, если не существует.
    Возвращает (user, created), где created=True если пользователь был создан.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is not None:
        # Обновляем информацию о пользователе
        if username and user.username != username:
            user.username = username
        if first_name and user.first_name != first_name:
            user.first_name = first_name
        if last_name and user.last_name != last_name:
            user.last_name = last_name
        return user, False

    # Создаем нового пользователя
    new_user = await create_user(
        session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
    return new_user, True


async def update_user_last_started(
    session: AsyncSession,
    telegram_id: int,
) -> None:
    """Обновить время последнего /start"""
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_started_at=datetime.utcnow())
    )


async def update_user_tone(
    session: AsyncSession,
    telegram_id: int,
    tone: GFTone,
) -> None:
    """Изменить тон общения пользователя"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        user.tone = tone
        await session.flush()


async def add_user_interests(
    session: AsyncSession,
    telegram_id: int,
    interests: List[GFInterest],
) -> None:
    """Добавить интересы пользователю"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        # Объединяем старые и новые интересы без дубликатов
        current = set(user.interests) if user.interests else set()
        new_interests = current.union(set(interests))
        user.interests = list(new_interests)
        await session.flush()


async def update_user_interests(
    session: AsyncSession,
    telegram_id: int,
    interests: List[GFInterest],
) -> None:
    """Обновить интересы пользователя (полная замена)"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        user.interests = interests
        await session.flush()


async def add_user_goals(
    session: AsyncSession,
    telegram_id: int,
    goals: List[GFGoal],
) -> None:
    """Добавить цели пользователю"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        # Объединяем старые и новые цели без дубликатов
        current = set(user.goals) if user.goals else set()
        new_goals = current.union(set(goals))
        user.goals = list(new_goals)
        await session.flush()


async def update_user_about(
    session: AsyncSession,
    telegram_id: int,
    about: str,
) -> None:
    """Обновить описание пользователя"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        user.about = about
        await session.flush()


async def get_all_users(session: AsyncSession) -> List[User]:
    """Получить всех пользователей"""
    result = await session.execute(select(User))
    return list(result.scalars().all())


async def get_users_by_tone(
    session: AsyncSession,
    tone: GFTone
) -> List[User]:
    """Получить пользователей с определенным тоном"""
    result = await session.execute(
        select(User).where(User.tone == tone)
    )
    return list(result.scalars().all())


# =========================
# CRUD функции для персонажей
# =========================

async def get_active_personas(session: AsyncSession) -> List[Persona]:
    """Получить всех активных персонажей"""
    result = await session.execute(
        select(Persona).where(Persona.is_active.is_(True))
    )
    return list(result.scalars().all())


async def get_persona_by_key(session: AsyncSession, key: str) -> Optional[Persona]:
    """Получить персонажа по ключу"""
    result = await session.execute(
        select(Persona).where(
            Persona.key == key, Persona.is_active.is_(True)
        )
    )
    return result.scalar_one_or_none()


async def get_persona_by_id(
    session: AsyncSession, persona_id: int
) -> Optional[Persona]:
    """Получить персонажа по ID"""
    result = await session.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    return result.scalar_one_or_none()


async def get_user_current_persona(
    session: AsyncSession, user_id: int
) -> Optional[Persona]:
    """Получить текущего персонажа пользователя"""
    result = await session.execute(
        select(Persona)
        .join(UserPersonaSetting)
        .where(
            UserPersonaSetting.user_id == user_id,
            UserPersonaSetting.is_current.is_(True)
        )
    )
    return result.scalar_one_or_none()


async def get_user_persona_setting(
    session: AsyncSession, user_id: int
) -> Optional[UserPersonaSetting]:
    """Получить настройки персонажа пользователя"""
    result = await session.execute(
        select(UserPersonaSetting)
        .where(
            UserPersonaSetting.user_id == user_id,
            UserPersonaSetting.is_current.is_(True)
        )
    )
    return result.scalar_one_or_none()


async def set_user_persona(
    session: AsyncSession,
    user_id: int,
    persona_id: int,
    overrides: Optional[dict] = None
) -> UserPersonaSetting:
    """Установить персонажа для пользователя"""
    # Сначала сбрасываем текущий персонаж
    await session.execute(
        update(UserPersonaSetting)
        .where(
            UserPersonaSetting.user_id == user_id,
            UserPersonaSetting.is_current.is_(True)
        )
        .values(is_current=False)
    )
    
    # Создаем новую запись с выбранным персонажем
    new_setting = UserPersonaSetting(
        user_id=user_id,
        persona_id=persona_id,
        overrides=overrides or {},
        is_current=True
    )
    
    session.add(new_setting)
    await session.flush()
    await session.refresh(new_setting)
    return new_setting


async def update_persona_overrides(
    session: AsyncSession,
    user_id: int,
    overrides: dict
) -> None:
    """Обновить кастомизации персонажа пользователя"""
    await session.execute(
        update(UserPersonaSetting)
        .where(
            UserPersonaSetting.user_id == user_id,
            UserPersonaSetting.is_current.is_(True)
        )
        .values(overrides=overrides)
    )
