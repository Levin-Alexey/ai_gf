#!/usr/bin/env python3
"""
Тест проверки потока передачи личности в LLM
"""
import asyncio
import logging
from sqlalchemy import text
from database import async_session_maker, init_db
from crud import get_persona_by_id, get_user_persona_setting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_persona_flow():
    """Тестирование потока передачи личности"""
    try:
        await init_db()
        
        logger.info("=" * 80)
        logger.info("🧪 ТЕСТ: Проверка потока передачи личности в LLM")
        logger.info("=" * 80)
        
        async with async_session_maker() as session:
            # Шаг 1: Получаем Эву по ID
            logger.info("\n📍 ШАГ 1: Получение персонажа Эва по ключу")
            result = await session.execute(
                text("SELECT id, key, name FROM personas WHERE key = 'Eva'")
            )
            row = result.fetchone()
            
            if not row:
                logger.error("❌ Персонаж Эва не найден!")
                return
            
            eva_id = row[0]
            logger.info(f"✅ Найден персонаж: ID={eva_id}, key={row[1]}, name={row[2]}")
            
            # Шаг 2: Получаем персонажа через функцию (как в коде)
            logger.info(f"\n📍 ШАГ 2: Получение через get_persona_by_id({eva_id})")
            persona = await get_persona_by_id(session, eva_id)
            
            if not persona:
                logger.error("❌ Функция get_persona_by_id вернула None!")
                return
            
            logger.info(f"✅ Персонаж получен: {persona.name}")
            logger.info(f"   - Key: {persona.key}")
            logger.info(f"   - Active: {persona.is_active}")
            logger.info(f"   - Reply style emojis: {persona.reply_style.get('emojis')}")
            logger.info(f"   - Signatures: {persona.reply_style.get('signatures')}")
            
            # Шаг 3: Проверяем промпт
            logger.info("\n📍 ШАГ 3: Проверка prompt_template")
            prompt = persona.prompt_template
            
            # Проверяем ключевые слова нового промпта
            checks = {
                "соблазнительная": "соблазнительная" in prompt,
                "влюблённая девушка": "влюблённая девушка" in prompt,
                "флиртуй": "флиртуй" in prompt.lower(),
                "эротический": "эротический" in prompt,
                "герой": "герой" in prompt,
                "AI запрет": "НИКОГДА не называй себя AI" in prompt,
                "эмодзи 💋": "💋" in prompt,
                "эмодзи 🔥": "🔥" in prompt,
            }
            
            all_passed = True
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                logger.info(f"   {status} {check_name}: {'найдено' if passed else 'НЕ НАЙДЕНО'}")
                if not passed:
                    all_passed = False
            
            # Шаг 4: Симуляция использования в _build_system_message
            logger.info("\n📍 ШАГ 4: Симуляция использования в _build_system_message")
            
            if persona:
                base_prompt = persona.prompt_template + "\n\n"
                logger.info(f"✅ Промпт будет использован (длина: {len(base_prompt)} символов)")
                logger.info(f"   Первые 150 символов: {base_prompt[:150]}...")
                
                # Проверяем reply_style
                if persona.reply_style:
                    logger.info(f"✅ Reply style будет применён")
                    logger.info(f"   - Emojis: {persona.reply_style.get('emojis')}")
                    logger.info(f"   - Pace: {persona.reply_style.get('pace')}")
                    logger.info(f"   - Signatures: {persona.reply_style.get('signatures')}")
            else:
                logger.error("❌ Персонаж None, будет использован дефолтный промпт")
            
            # Итоговый результат
            logger.info("\n" + "=" * 80)
            if all_passed and persona:
                logger.info("🎉 УСПЕХ: Все проверки пройдены!")
                logger.info("✅ Поток передачи личности работает корректно")
                logger.info("✅ Новый сексуализированный промпт будет использоваться")
                logger.info("✅ Reply style с романтическими эмодзи активен")
            else:
                logger.error("❌ ОШИБКА: Некоторые проверки не прошли!")
                logger.error("⚠️ Поток передачи личности может работать некорректно")
            logger.info("=" * 80)
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}", exc_info=True)
        raise


async def test_flow_with_user():
    """Тест с реальным пользователем"""
    try:
        await init_db()
        
        logger.info("\n" + "=" * 80)
        logger.info("🧪 ТЕСТ: Проверка с реальным пользователем")
        logger.info("=" * 80)
        
        async with async_session_maker() as session:
            # Проверяем наличие пользователей
            result = await session.execute(
                text("SELECT id, telegram_id, username FROM users LIMIT 1")
            )
            user_row = result.fetchone()
            
            if not user_row:
                logger.warning("⚠️ Нет пользователей в базе для полного теста")
                return
            
            user_id = user_row[0]
            logger.info(f"✅ Найден пользователь: ID={user_id}, telegram_id={user_row[1]}")
            
            # Проверяем настройки персонажа пользователя
            persona_setting = await get_user_persona_setting(session, user_id)
            
            if persona_setting:
                logger.info(f"✅ У пользователя есть активный персонаж:")
                logger.info(f"   - Persona ID: {persona_setting.persona_id}")
                logger.info(f"   - Is current: {persona_setting.is_current}")
                logger.info(f"   - Overrides: {persona_setting.overrides}")
                
                # Получаем сам персонаж
                persona = await get_persona_by_id(session, persona_setting.persona_id)
                if persona:
                    logger.info(f"✅ Персонаж загружен: {persona.name}")
                    logger.info(f"   - Промпт (первые 100 символов): {persona.prompt_template[:100]}...")
            else:
                logger.info("ℹ️ У пользователя нет активного персонажа (будет дефолтный)")
            
            logger.info("=" * 80)
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)


async def main():
    """Главная функция"""
    await test_persona_flow()
    await test_flow_with_user()


if __name__ == "__main__":
    asyncio.run(main())
