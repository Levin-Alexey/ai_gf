from datetime import datetime
from typing import List, Optional
import enum

from sqlalchemy import (
    BigInteger, String, Text, TIMESTAMP, Index,
    func, Enum as SQLEnum, ARRAY
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


# Enum классы для типов PostgreSQL
class GFTone(str, enum.Enum):
    """Тон общения с пользователем"""
    GENTLE = 'gentle'
    FRIENDLY = 'friendly'
    NEUTRAL = 'neutral'
    SARCASTIC = 'sarcastic'
    FORMAL = 'formal'


class GFInterest(str, enum.Enum):
    """Интересы пользователя"""
    WORK = 'work'
    STARTUPS = 'startups'
    SPORT = 'sport'
    MOVIES = 'movies'
    GAMES = 'games'
    MUSIC = 'music'
    TRAVEL = 'travel'
    SELF_GROWTH = 'self_growth'
    PSYCHOLOGY = 'psychology'
    AI_TECH = 'ai_tech'
    BOOKS = 'books'


class GFGoal(str, enum.Enum):
    """Цели использования бота"""
    SUPPORT = 'support'
    MOTIVATION = 'motivation'
    CHITCHAT = 'chitchat'
    ADVICE = 'advice'
    LEARN_ENGLISH = 'learn_english'
    PROJECT_IDEAS = 'project_ideas'
    BRAINSTORM = 'brainstorm'
    STRESS_RELIEF = 'stress_relief'
    ACCOUNTABILITY = 'accountability'
    DAILY_CHECKIN = 'daily_checkin'


class User(Base):
    """Модель пользователя Telegram бота"""
    __tablename__ = 'users'

    # Основные поля
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Настройки пользователя (заполняются после опросника)
    display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tone: Mapped[Optional[GFTone]] = mapped_column(
        SQLEnum(GFTone, name='gf_tone', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        default=None
    )
    interests: Mapped[Optional[List[GFInterest]]] = mapped_column(
        ARRAY(SQLEnum(GFInterest, name='gf_interest', create_type=False, values_callable=lambda x: [e.value for e in x])),
        nullable=True,
        default=None
    )
    goals: Mapped[Optional[List[GFGoal]]] = mapped_column(
        ARRAY(SQLEnum(GFGoal, name='gf_goal', create_type=False, values_callable=lambda x: [e.value for e in x])),
        nullable=True,
        default=None
    )
    about: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Временные метки
    first_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    last_started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Индексы
    __table_args__ = (
        Index('idx_users_telegram_id', 'telegram_id'),
        Index('idx_users_username_ci', func.lower(username)),
        Index('idx_users_tone', 'tone'),
        Index('idx_users_interests', 'interests', postgresql_using='gin'),
        Index('idx_users_goals', 'goals', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username}, tone={self.tone.value})"
        )

    def get_display_name(self) -> str:
        """Получить отображаемое имя пользователя"""
        if self.display_name:
            return self.display_name
        if self.first_name:
            return self.first_name
        if self.username:
            return self.username
        return f"User {self.telegram_id}"

