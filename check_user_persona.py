#!/usr/bin/env python3
"""
Быстрая проверка персонажа пользователя
"""
import asyncio
import sys
from sqlalchemy import text
from database import async_session_maker, init_db


async def check_user_persona(telegram_id: int):
    """Проверить персонажа пользователя"""
    try:
        await init_db()
        
        print(f"\n{'='*70}")
        print(f"🔍 ПРОВЕРКА ПЕРСОНАЖА ДЛЯ ПОЛЬЗОВАТЕЛЯ telegram_id={telegram_id}")
        print(f"{'='*70}\n")
        
        async with async_session_maker() as session:
            # Получаем текущего персонажа пользователя
            query = text("""
                SELECT 
                    u.id as user_id,
                    u.telegram_id,
                    u.username,
                    ups.id as setting_id,
                    ups.persona_id,
                    p.key as persona_key,
                    p.name as persona_name,
                    p.version,
                    ups.is_current,
                    ups.selected_at,
                    LEFT(p.prompt_template, 150) as prompt_preview
                FROM users u
                LEFT JOIN user_persona_settings ups ON ups.user_id = u.id AND ups.is_current = TRUE
                LEFT JOIN personas p ON p.id = ups.persona_id
                WHERE u.telegram_id = :telegram_id
            """)
            
            result = await session.execute(query, {"telegram_id": telegram_id})
            row = result.fetchone()
            
            if not row:
                print(f"❌ Пользователь с telegram_id={telegram_id} НЕ НАЙДЕН!")
                return
            
            print(f"✅ Пользователь найден:")
            print(f"   • User ID (внутренний): {row.user_id}")
            print(f"   • Telegram ID: {row.telegram_id}")
            print(f"   • Username: {row.username or 'не указан'}")
            print()
            
            if row.persona_id:
                print(f"✅ Активный персонаж:")
                print(f"   • Persona ID: {row.persona_id}")
                print(f"   • Key: {row.persona_key}")
                print(f"   • Name: {row.persona_name}")
                print(f"   • Version: {row.version}")
                print(f"   • Is Current: {row.is_current}")
                print(f"   • Selected At: {row.selected_at}")
                print(f"   • Prompt Preview: {row.prompt_preview}...")
            else:
                print(f"⚠️  У пользователя НЕТ активного персонажа!")
            
            print()
            
            # Показываем историю выборов персонажей
            history_query = text("""
                SELECT 
                    ups.id,
                    ups.persona_id,
                    p.name as persona_name,
                    ups.is_current,
                    ups.selected_at
                FROM user_persona_settings ups
                JOIN personas p ON p.id = ups.persona_id
                WHERE ups.user_id = :user_id
                ORDER BY ups.selected_at DESC
                LIMIT 10
            """)
            
            history_result = await session.execute(
                history_query, 
                {"user_id": row.user_id}
            )
            history_rows = history_result.fetchall()
            
            if history_rows:
                print(f"📜 История выбора персонажей (последние 10):")
                print(f"{'='*70}")
                for h in history_rows:
                    current_mark = " ← ТЕКУЩИЙ" if h.is_current else ""
                    print(
                        f"   ID: {h.id:3d} | "
                        f"Persona ID: {h.persona_id:2d} | "
                        f"Name: {h.persona_name:15s} | "
                        f"Current: {h.is_current} | "
                        f"Selected: {h.selected_at}"
                        f"{current_mark}"
                    )
            
            print(f"{'='*70}\n")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_user_persona.py <telegram_id>")
        print("Example: python check_user_persona.py 525944420")
        sys.exit(1)
    
    telegram_id = int(sys.argv[1])
    asyncio.run(check_user_persona(telegram_id))
