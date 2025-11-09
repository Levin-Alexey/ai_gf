"""
Клиент для работы с векторной базой данных воспоминаний
"""
import logging
import asyncio
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from config import (
    VECTOR_DB_PATH, 
    EMBEDDING_MODEL, 
    VECTOR_SEARCH_LIMIT, 
    VECTOR_SIMILARITY_THRESHOLD
)

logger = logging.getLogger(__name__)


class VectorClient:
    """Клиент для работы с векторной базой данных"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.initialized = False
    
    async def initialize(self):
        """Инициализация векторной базы данных"""
        try:
            # Инициализируем ChromaDB
            self.client = chromadb.PersistentClient(
                path=VECTOR_DB_PATH,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Создаем или получаем коллекцию
            self.collection = self.client.get_or_create_collection(
                name="user_memories",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Загружаем модель для эмбеддингов
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            
            self.initialized = True
            logger.info("✅ Векторная база данных ChromaDB инициализирована!")
            logger.info(f"📁 Путь к векторной БД: {VECTOR_DB_PATH}")
            logger.info(f"🤖 Модель эмбеддингов: {EMBEDDING_MODEL}")
            logger.info(f"📊 Коллекция: {self.collection.name}")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации векторной базы: {e}")
            raise
    
    async def add_memory(
        self, 
        memory_id: str, 
        user_id: int, 
        content: str, 
        memory_type: str,
        importance: str,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> bool:
        """Добавить воспоминание в векторную базу"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Создаем эмбеддинг для содержимого
            embedding = self.embedding_model.encode(content).tolist()
            
            # Подготавливаем метаданные и удаляем значения None,
            # так как ChromaDB не принимает None в метаданных
            base_metadata = {
                "user_id": user_id,
                "memory_type": memory_type,
                "importance": importance,
                "tags": ",".join(tags) if tags else ""
            }
            extra_metadata = {
                key: value
                for key, value in (metadata or {}).items()
                if value is not None
            }
            memory_metadata = {
                key: value
                for key, value in {**base_metadata, **extra_metadata}.items()
                if value is not None
            }
            
            # Добавляем в коллекцию
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[memory_metadata]
            )
            
            logger.info(f"Добавлено воспоминание {memory_id} в векторную базу")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления воспоминания в векторную базу: {e}")
            return False
    
    async def search_similar_memories(
        self, 
        user_id: int, 
        query: str, 
        memory_types: List[str] = None,
        limit: int = None
    ) -> List[Dict]:
        """Поиск похожих воспоминаний по запросу"""
        try:
            if not self.initialized:
                await self.initialize()
            
            if limit is None:
                limit = VECTOR_SEARCH_LIMIT
            
            # Создаем эмбеддинг для запроса
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Подготавливаем фильтр
            where_filter = {"user_id": user_id}
            if memory_types:
                where_filter["memory_type"] = {"$in": memory_types}
            
            # Выполняем поиск
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Формируем результат
            similar_memories = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Преобразуем расстояние в схожесть (1 - distance)
                    similarity = 1 - distance
                    
                    # Фильтруем по порогу схожести
                    if similarity >= VECTOR_SIMILARITY_THRESHOLD:
                        similar_memories.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "distance": distance
                        })
            
            logger.info(f"Найдено {len(similar_memories)} похожих воспоминаний для запроса: {query[:50]}")
            return similar_memories
            
        except Exception as e:
            logger.error(f"Ошибка поиска похожих воспоминаний: {e}")
            return []
    
    async def get_user_memories_by_type(
        self, 
        user_id: int, 
        memory_type: str,
        limit: int = None
    ) -> List[Dict]:
        """Получить воспоминания пользователя по типу"""
        try:
            if not self.initialized:
                await self.initialize()
            
            if limit is None:
                limit = VECTOR_SEARCH_LIMIT
            
            # Получаем все воспоминания пользователя определенного типа
            results = self.collection.get(
                where={
                    "user_id": user_id,
                    "memory_type": memory_type
                },
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["documents"]:
                for doc, metadata in zip(results["documents"], results["metadatas"]):
                    memories.append({
                        "content": doc,
                        "metadata": metadata
                    })
            
            logger.info(f"Получено {len(memories)} воспоминаний типа {memory_type} для пользователя {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Ошибка получения воспоминаний по типу: {e}")
            return []
    
    async def get_important_memories(
        self, 
        user_id: int, 
        importance_levels: List[str] = None,
        limit: int = None
    ) -> List[Dict]:
        """Получить важные воспоминания пользователя"""
        try:
            if not self.initialized:
                await self.initialize()
            
            if limit is None:
                limit = VECTOR_SEARCH_LIMIT
            
            if importance_levels is None:
                importance_levels = ["high", "critical"]
            
            # Получаем важные воспоминания
            results = self.collection.get(
                where={
                    "user_id": user_id,
                    "importance": {"$in": importance_levels}
                },
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["documents"]:
                for doc, metadata in zip(results["documents"], results["metadatas"]):
                    memories.append({
                        "content": doc,
                        "metadata": metadata
                    })
            
            logger.info(f"Получено {len(memories)} важных воспоминаний для пользователя {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Ошибка получения важных воспоминаний: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Удалить воспоминание из векторной базы"""
        try:
            if not self.initialized:
                await self.initialize()
            
            self.collection.delete(ids=[memory_id])
            logger.info(f"Удалено воспоминание {memory_id} из векторной базы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления воспоминания: {e}")
            return False
    
    async def update_memory(
        self, 
        memory_id: str, 
        content: str = None,
        metadata: Dict = None
    ) -> bool:
        """Обновить воспоминание в векторной базе"""
        try:
            if not self.initialized:
                await self.initialize()
            
            update_data = {}
            
            if content:
                # Обновляем эмбеддинг
                embedding = self.embedding_model.encode(content).tolist()
                update_data["embeddings"] = [embedding]
                update_data["documents"] = [content]
            
            if metadata:
                update_data["metadatas"] = [metadata]
            
            if update_data:
                self.collection.update(
                    ids=[memory_id],
                    **update_data
                )
                logger.info(f"Обновлено воспоминание {memory_id} в векторной базе")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления воспоминания: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict:
        """Получить статистику коллекции"""
        try:
            if not self.initialized:
                await self.initialize()
            
            count = self.collection.count()
            
            stats = {
                "total_memories": count,
                "collection_name": self.collection.name,
                "embedding_model": EMBEDDING_MODEL
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}


# Глобальный экземпляр векторного клиента
vector_client = VectorClient()
