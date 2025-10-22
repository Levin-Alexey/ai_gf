from datetime import datetime
from typing import List, Optional
import enum

from sqlalchemy import (
    BigInteger, String, Text, TIMESTAMP, Index, Boolean, Integer, ForeignKey,
    Float, func, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


# =========================
# Enum классы (как в базе)
# =========================
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


class MemoryType(str, enum.Enum):
    """Типы воспоминаний"""
    FACT = 'fact'
    PREFERENCE = 'preference'
    EMOTION = 'emotion'
    EVENT = 'event'
    RELATIONSHIP = 'relationship'
    GOAL = 'goal'
    FEAR = 'fear'
    DREAM = 'dream'


class MemoryImportance(str, enum.Enum):
    """Важность воспоминания"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


# =========================
# Пользователь и связанные
# =========================
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

    # Подписка
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None
    )

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

    # Связи
    memories: Mapped[List["UserMemory"]] = relationship(
        "UserMemory", back_populates="user", cascade="all, delete-orphan"
    )
    emotions: Mapped[List["UserEmotion"]] = relationship(
        "UserEmotion", back_populates="user", cascade="all, delete-orphan"
    )
    relationships: Mapped[List["UserRelationship"]] = relationship(
        "UserRelationship", back_populates="user", cascade="all, delete-orphan"
    )
    persona_settings: Mapped[List["UserPersonaSetting"]] = relationship(
        "UserPersonaSetting", back_populates="user", cascade="all, delete-orphan"
    )
    persona_events: Mapped[List["PersonaEvent"]] = relationship(
        "PersonaEvent", back_populates="user", cascade="all, delete-orphan"
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
        tone_value = self.tone.value if self.tone else None
        return (
            f"User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username={self.username}, tone={tone_value})"
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


class UserMemory(Base):
    """Долгосрочная память о пользователе"""
    __tablename__ = 'user_memories'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Содержимое воспоминания
    content: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[MemoryType] = mapped_column(
        SQLEnum(MemoryType, name='memory_type', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    importance: Mapped[MemoryImportance] = mapped_column(
        SQLEnum(MemoryImportance, name='memory_importance', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MemoryImportance.MEDIUM
    )

    # Метаданные
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    emotional_tone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # positive, negative, neutral
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 - 1.0

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="memories")

    # Индексы
    __table_args__ = (
        Index('idx_memories_user_id', 'user_id'),
        Index('idx_memories_type', 'memory_type'),
        Index('idx_memories_importance', 'importance'),
        Index('idx_memories_created_at', 'created_at'),
        Index('idx_memories_tags', 'tags', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return f"UserMemory(id={self.id}, user_id={self.user_id}, type={self.memory_type.value}, content={self.content[:50]}...)"


class UserEmotion(Base):
    """Эмоциональное состояние пользователя"""
    __tablename__ = 'user_emotions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Эмоциональные данные
    emotion: Mapped[str] = mapped_column(Text, nullable=False)  # happy, sad, anxious, excited, etc.
    intensity: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # контекст эмоции

    # Временные метки
    recorded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="emotions")

    # Индексы
    __table_args__ = (
        Index('idx_emotions_user_id', 'user_id'),
        Index('idx_emotions_recorded_at', 'recorded_at'),
        Index('idx_emotions_emotion', 'emotion'),
    )

    def __repr__(self) -> str:
        return f"UserEmotion(id={self.id}, user_id={self.user_id}, emotion={self.emotion}, intensity={self.intensity})"


class UserRelationship(Base):
    """Информация об отношениях пользователя"""
    __tablename__ = 'user_relationships'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Информация об отношениях
    person_name: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_type: Mapped[str] = mapped_column(Text, nullable=False)  # family, friend, colleague, partner, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    importance: Mapped[MemoryImportance] = mapped_column(
        SQLEnum(MemoryImportance, name='relationship_importance', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MemoryImportance.MEDIUM
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
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

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="relationships")

    # Индексы
    __table_args__ = (
        Index('idx_relationships_user_id', 'user_id'),
        Index('idx_relationships_type', 'relationship_type'),
        Index('idx_relationships_importance', 'importance'),
    )

    def __repr__(self) -> str:
        return f"UserRelationship(id={self.id}, user_id={self.user_id}, person={self.person_name}, type={self.relationship_type})"


# =========================
# Персонажи и выбор
# =========================
class Persona(Base):
    """Справочник персонажей (архетипы)"""
    __tablename__ = 'personas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # 'astra', 'fox', 'ella', 'runa', ...
    name: Mapped[str] = mapped_column(String(128), nullable=False)             # Отображаемое имя

    short_desc: Mapped[str] = mapped_column(Text, nullable=False)              # 1–2 строки для меню
    long_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # карточка персонажа
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)     # URL аватара персонажа

    reply_style: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)   # pace/length/structure/signatures
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)               # system/preamble
    guardrails: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)    # ограничения/политики
    rituals: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)       # ритуалы (утро/неделя/символ)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Связи
    user_settings: Mapped[List["UserPersonaSetting"]] = relationship(
        "UserPersonaSetting", back_populates="persona", cascade="all, delete-orphan"
    )
    events: Mapped[List["PersonaEvent"]] = relationship(
        "PersonaEvent", back_populates="persona"
    )

    __table_args__ = (
        Index('idx_personas_active', 'is_active'),
        Index('idx_personas_version', 'version'),
        Index('idx_personas_reply_style_gin', 'reply_style', postgresql_using='gin'),
        Index('idx_personas_guardrails_gin', 'guardrails', postgresql_using='gin'),
        Index('idx_personas_rituals_gin', 'rituals', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return f"Persona(id={self.id}, key={self.key}, name={self.name}, ver={self.version}, active={self.is_active})"


class UserPersonaSetting(Base):
    """
    Текущий выбор персонажа у пользователя + история переключений.
    Ровно одна запись с is_current = TRUE на пользователя.
    """
    __tablename__ = 'user_persona_settings'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    persona_id: Mapped[int] = mapped_column(Integer, ForeignKey('personas.id', ondelete='RESTRICT'), nullable=False)

    overrides: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # локальные правки стиля/фраз
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    selected_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="persona_settings")
    persona: Mapped["Persona"] = relationship("Persona", back_populates="user_settings")

    __table_args__ = (
        # один текущий персонаж на пользователя
        Index(
            'uq_user_current_persona',
            'user_id',
            unique=True,
            postgresql_where=(is_current.is_(True))
        ),
        Index('idx_user_persona_history', 'user_id', 'selected_at'),
    )

    def __repr__(self) -> str:
        return f"UserPersonaSetting(id={self.id}, user_id={self.user_id}, persona_id={self.persona_id}, current={self.is_current})"


class PersonaEvent(Base):
    """Ивенты/аналитика по персонажам"""
    __tablename__ = 'persona_events'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    persona_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('personas.id', ondelete='SET NULL'), nullable=True)

    event: Mapped[str] = mapped_column(String(64), nullable=False)  # 'selected','greet_shown','ritual_triggered','switch','ab_bucket_assigned'
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="persona_events")
    persona: Mapped[Optional["Persona"]] = relationship("Persona", back_populates="events")

    __table_args__ = (
        Index('idx_persona_events_user_time', 'user_id', 'created_at'),
        Index('idx_persona_events_persona', 'persona_id'),
        Index('idx_persona_events_event', 'event'),
    )

    def __repr__(self) -> str:
        return f"PersonaEvent(id={self.id}, user_id={self.user_id}, persona_id={self.persona_id}, event={self.event})"