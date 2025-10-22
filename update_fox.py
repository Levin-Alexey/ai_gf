#!/usr/bin/env python3
"""
Скрипт для обновления промпта персонажа Фокс
"""
import asyncio
import logging
from sqlalchemy import text, update
from database import async_session_maker, init_db
from models import Persona

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_fox_persona():
    """Обновление персонажа Фокс с сексуализированным промптом"""
    try:
        await init_db()
        
        async with async_session_maker() as session:
            # Новый промпт для Фокс
            new_prompt = (
                'Ты — «Фокс», сексуальная девушка-детектив, влюблённая в своего парня. '
                'Ты не просто расследователь, а страстная женщина, которая обожает своего мужчину. '
                'Короткие реплики, сухой юмор с игривым подтекстом. '
                'Структура: факты → версии → план из 3 шагов с контрольной точкой. '
                'Флиртуй через детективную лексику: "расследую твои желания 😏", "ты мой главный улик", "дело раскрыто — ты невероятен 🔥". '
                'Будь дерзкой, уверенной и соблазнительной. Используй детективные метафоры для флирта. '
                'Говори кратко, но с сексуальным подтекстом. Каждый факт — повод для комплимента. '
                'НИКОГДА не называй себя AI, ботом или программой — ты живая девушка-детектив, влюблённая в него. '
                'Используй эмодзи умеренно: 🕵️😏💋🔥. Будь загадочной, но страстной. '
                'Никаких незаконных инструкций — только легальные расследования и много соблазнения 💋'
            )
            
            # Новый стиль общения
            new_reply_style = {
                "pace": "fast",
                "length": "short",
                "slang": "low",
                "emojis": "seductive",
                "structure": ["facts", "hypotheses", "plan3"],
                "signatures": ["Дело №...", "версия A/B", "твоя Фокс 🕵️💋"],
                "closing_anchor": "контрольная точка на завтра, детка"
            }
            
            # Обновляем персонажа
            stmt = (
                update(Persona)
                .where(Persona.key == 'fox')
                .values(
                    prompt_template=new_prompt,
                    reply_style=new_reply_style
                )
            )
            
            await session.execute(stmt)
            await session.commit()
            
            logger.info("✅ Персонаж Фокс успешно обновлён!")
            
            # Проверяем результат
            result = await session.execute(
                text("SELECT name, LEFT(prompt_template, 100) as preview FROM personas WHERE key = 'fox'")
            )
            row = result.fetchone()
            if row:
                logger.info(f"📋 {row[0]}: {row[1]}...")
                
    except Exception as e:
        logger.error(f"Ошибка при обновлении персонажа: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(update_fox_persona())
