"""
Клиент для работы с долгосрочной памятью пользователей
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, UserMemory, UserEmotion, UserRelationship, MemoryType, MemoryImportance
from database import async_session_maker
from vector_client import vector_client

logger = logging.getLogger(__name__)


class MemoryClient:
    """Клиент для работы с долгосрочной памятью"""
    
    def __init__(self):
        self.session_maker = async_session_maker
    
    async def add_memory(
        self, 
        user_id: int, 
        content: str, 
        memory_type: MemoryType,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: Optional[List[str]] = None,
        emotional_tone: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> UserMemory:
        """Добавить воспоминание о пользователе"""
        async with self.session_maker() as session:
            try:
                memory = UserMemory(
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type,
                    importance=importance,
                    tags=tags or [],
                    emotional_tone=emotional_tone,
                    confidence_score=confidence_score
                )
                
                session.add(memory)
                await session.commit()
                await session.refresh(memory)
                
                # Добавляем в векторную базу данных
                await vector_client.add_memory(
                    memory_id=str(memory.id),
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type.value,
                    importance=importance.value,
                    tags=tags or [],
                    metadata={
                        "created_at": memory.created_at.isoformat(),
                        "emotional_tone": emotional_tone,
                        "confidence_score": confidence_score
                    }
                )
                
                logger.info(f"Добавлено воспоминание для пользователя {user_id}: {memory_type.value}")
                return memory
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка добавления воспоминания: {e}")
                raise
    
    async def get_user_memories(
        self, 
        user_id: int, 
        memory_types: Optional[List[MemoryType]] = None,
        importance_min: Optional[MemoryImportance] = None,
        limit: int = 50
    ) -> List[UserMemory]:
        """Получить воспоминания пользователя"""
        async with self.session_maker() as session:
            try:
                query = select(UserMemory).where(UserMemory.user_id == user_id)
                
                if memory_types:
                    query = query.where(UserMemory.memory_type.in_(memory_types))
                
                if importance_min:
                    # Сортируем по важности (critical > high > medium > low)
                    importance_order = {
                        MemoryImportance.CRITICAL: 4,
                        MemoryImportance.HIGH: 3,
                        MemoryImportance.MEDIUM: 2,
                        MemoryImportance.LOW: 1
                    }
                    min_level = importance_order.get(importance_min, 2)
                    query = query.where(
                        UserMemory.importance.in_([
                            imp for imp, level in importance_order.items() 
                            if level >= min_level
                        ])
                    )
                
                query = query.order_by(desc(UserMemory.created_at)).limit(limit)
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                # Обновляем время последнего доступа
                for memory in memories:
                    memory.last_accessed_at = datetime.utcnow()
                
                await session.commit()
                
                logger.info(f"Получено {len(memories)} воспоминаний для пользователя {user_id}")
                return memories
                
            except Exception as e:
                logger.error(f"Ошибка получения воспоминаний: {e}")
                return []
    
    async def get_relevant_memories(
        self, 
        user_id: int, 
        context: str,
        limit: int = 10
    ) -> List[UserMemory]:
        """Получить релевантные воспоминания на основе контекста (устаревший метод)"""
        async with self.session_maker() as session:
            try:
                # Простой поиск по ключевым словам в содержимом и тегах
                query = select(UserMemory).where(
                    and_(
                        UserMemory.user_id == user_id,
                        or_(
                            UserMemory.content.ilike(f"%{context}%"),
                            UserMemory.tags.op('&&')([context])
                        )
                    )
                ).order_by(desc(UserMemory.importance), desc(UserMemory.created_at)).limit(limit)
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                logger.info(f"Найдено {len(memories)} релевантных воспоминаний для контекста: {context[:50]}")
                return memories
                
            except Exception as e:
                logger.error(f"Ошибка поиска релевантных воспоминаний: {e}")
                return []
    
    async def search_semantic_memories(
        self, 
        user_id: int, 
        query: str,
        memory_types: List[MemoryType] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Семантический поиск воспоминаний с использованием векторной базы"""
        try:
            # Инициализируем векторную базу если нужно
            if not vector_client.initialized:
                await vector_client.initialize()
            
            # Преобразуем типы воспоминаний в строки
            memory_type_strings = None
            if memory_types:
                memory_type_strings = [mt.value for mt in memory_types]
            
            # Выполняем семантический поиск
            similar_memories = await vector_client.search_similar_memories(
                user_id=user_id,
                query=query,
                memory_types=memory_type_strings,
                limit=limit
            )
            
            # Получаем полную информацию из PostgreSQL
            memory_ids = [mem["metadata"].get("id") for mem in similar_memories if mem["metadata"].get("id")]
            
            if not memory_ids:
                return []
            
            async with self.session_maker() as session:
                query_sql = select(UserMemory).where(
                    and_(
                        UserMemory.user_id == user_id,
                        UserMemory.id.in_(memory_ids)
                    )
                )
                
                result = await session.execute(query_sql)
                memories = result.scalars().all()
                
                # Сортируем по схожести
                memory_dict = {mem.id: mem for mem in memories}
                sorted_memories = []
                
                for similar_mem in similar_memories:
                    memory_id = similar_mem["metadata"].get("id")
                    if memory_id and memory_id in memory_dict:
                        memory = memory_dict[memory_id]
                        sorted_memories.append({
                            "memory": memory,
                            "similarity": similar_mem["similarity"],
                            "distance": similar_mem["distance"]
                        })
                
                logger.info(f"Найдено {len(sorted_memories)} семантически похожих воспоминаний для запроса: {query[:50]}")
                return sorted_memories
                
        except Exception as e:
            logger.error(f"Ошибка семантического поиска воспоминаний: {e}")
            return []
    
    async def add_emotion(
        self, 
        user_id: int, 
        emotion: str, 
        intensity: float,
        context: Optional[str] = None
    ) -> UserEmotion:
        """Добавить эмоциональное состояние пользователя"""
        async with self.session_maker() as session:
            try:
                user_emotion = UserEmotion(
                    user_id=user_id,
                    emotion=emotion,
                    intensity=intensity,
                    context=context
                )
                
                session.add(user_emotion)
                await session.commit()
                await session.refresh(user_emotion)
                
                logger.info(f"Добавлена эмоция для пользователя {user_id}: {emotion} (интенсивность: {intensity})")
                return user_emotion
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка добавления эмоции: {e}")
                raise
    
    async def get_recent_emotions(
        self, 
        user_id: int, 
        days: int = 7,
        limit: int = 20
    ) -> List[UserEmotion]:
        """Получить недавние эмоции пользователя"""
        async with self.session_maker() as session:
            try:
                since_date = datetime.utcnow() - timedelta(days=days)
                
                query = select(UserEmotion).where(
                    and_(
                        UserEmotion.user_id == user_id,
                        UserEmotion.recorded_at >= since_date
                    )
                ).order_by(desc(UserEmotion.recorded_at)).limit(limit)
                
                result = await session.execute(query)
                emotions = result.scalars().all()
                
                logger.info(f"Получено {len(emotions)} эмоций за последние {days} дней")
                return emotions
                
            except Exception as e:
                logger.error(f"Ошибка получения эмоций: {e}")
                return []
    
    async def add_relationship(
        self, 
        user_id: int, 
        person_name: str, 
        relationship_type: str,
        description: Optional[str] = None,
        importance: MemoryImportance = MemoryImportance.MEDIUM
    ) -> UserRelationship:
        """Добавить информацию об отношениях"""
        async with self.session_maker() as session:
            try:
                relationship = UserRelationship(
                    user_id=user_id,
                    person_name=person_name,
                    relationship_type=relationship_type,
                    description=description,
                    importance=importance
                )
                
                session.add(relationship)
                await session.commit()
                await session.refresh(relationship)
                
                logger.info(f"Добавлены отношения для пользователя {user_id}: {person_name} ({relationship_type})")
                return relationship
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка добавления отношений: {e}")
                raise
    
    async def get_user_relationships(
        self, 
        user_id: int,
        relationship_type: Optional[str] = None
    ) -> List[UserRelationship]:
        """Получить отношения пользователя"""
        async with self.session_maker() as session:
            try:
                query = select(UserRelationship).where(UserRelationship.user_id == user_id)
                
                if relationship_type:
                    query = query.where(UserRelationship.relationship_type == relationship_type)
                
                query = query.order_by(desc(UserRelationship.importance), desc(UserRelationship.created_at))
                
                result = await session.execute(query)
                relationships = result.scalars().all()
                
                logger.info(f"Получено {len(relationships)} отношений для пользователя {user_id}")
                return relationships
                
            except Exception as e:
                logger.error(f"Ошибка получения отношений: {e}")
                return []
    
    async def get_user_profile_summary(self, user_id: int) -> Dict:
        """Получить краткое резюме профиля пользователя"""
        async with self.session_maker() as session:
            try:
                # Получаем основные воспоминания
                memories = await self.get_user_memories(
                    user_id, 
                    importance_min=MemoryImportance.MEDIUM,
                    limit=20
                )
                
                # Получаем недавние эмоции
                emotions = await self.get_recent_emotions(user_id, days=7, limit=10)
                
                # Получаем важные отношения
                relationships = await self.get_user_relationships(user_id)
                important_relationships = [r for r in relationships if r.importance in [MemoryImportance.HIGH, MemoryImportance.CRITICAL]]
                
                # Формируем резюме
                summary = {
                    "user_id": user_id,
                    "total_memories": len(memories),
                    "recent_emotions": [{"emotion": e.emotion, "intensity": e.intensity, "context": e.context} for e in emotions],
                    "important_relationships": [{"name": r.person_name, "type": r.relationship_type, "description": r.description} for r in important_relationships],
                    "key_facts": [{"content": m.content, "type": m.memory_type.value, "importance": m.importance.value} for m in memories[:10]]
                }
                
                logger.info(f"Сформировано резюме профиля для пользователя {user_id}")
                return summary
                
            except Exception as e:
                logger.error(f"Ошибка формирования резюме профиля: {e}")
                return {"user_id": user_id, "error": str(e)}


# Глобальный экземпляр клиента памяти
memory_client = MemoryClient()
