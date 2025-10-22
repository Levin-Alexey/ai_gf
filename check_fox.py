#!/usr/bin/env python3
"""
Проверка персонажа Фокс
"""
import asyncio
import logging
from sqlalchemy import text
from database import async_session_maker, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_fox():
    """Проверка персонажа Фокс"""
    try:
        await init_db()
        
        async with async_session_maker() as session:
            result = await session.execute(
                text("""
                    SELECT 
                        key, 
                        name, 
                        short_desc,
                        reply_style,
                        prompt_template
                    FROM personas 
                    WHERE key = 'fox'
                """)
            )
            row = result.fetchone()
            
            if row:
                logger.info("=" * 80)
                logger.info(f"🔑 Key: {row[0]}")
                logger.info(f"👤 Name: {row[1]}")
                logger.info(f"📝 Short desc: {row[2]}")
                logger.info("=" * 80)
                logger.info("💬 Reply style:")
                logger.info(f"{row[3]}")
                logger.info("=" * 80)
                logger.info("🎭 Prompt template:")
                logger.info(f"{row[4]}")
                logger.info("=" * 80)
            else:
                logger.warning("Персонаж Фокс не найден!")
                
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(check_fox())
