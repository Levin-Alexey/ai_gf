from datetime import datetime
from typing import List, Optional
import enum

from sqlalchemy import (
    BigInteger, String, Text, TIMESTAMP, Index,
    func, Enum as SQLEnum, ARRAY, ForeignKey, Float
)
from sqlalchemy.orm import relationship
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


class MemoryType(str, enum.Enum):
    """Типы воспоминаний"""
    FACT = 'fact'  # Факт о пользователе
    PREFERENCE = 'preference'  # Предпочтение
    EMOTION = 'emotion'  # Эмоциональное состояние
    EVENT = 'event'  # Важное событие
    RELATIONSHIP = 'relationship'  # Информация об отношениях
    GOAL = 'goal'  # Цель пользователя
    FEAR = 'fear'  # Страх или беспокойство
    DREAM = 'dream'  # Мечта или желание


class MemoryImportance(str, enum.Enum):
    """Важность воспоминания"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


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


class UserMemory(Base):
    """Долгосрочная память о пользователе"""
    __tablename__ = 'user_memories'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    
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
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    
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
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    
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


# Добавляем связи к модели User
User.memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
User.emotions = relationship("UserEmotion", back_populates="user", cascade="all, delete-orphan")
User.relationships = relationship("UserRelationship", back_populates="user", cascade="all, delete-orphan")

