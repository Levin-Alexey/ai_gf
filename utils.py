"""
Вспомогательные функции
"""
from datetime import datetime
from typing import Tuple

from models import User


def is_profile_complete(user: User) -> bool:
    """
    Проверить, заполнен ли профиль пользователя полностью.

    Профиль считается заполненным, если у пользователя есть:
    - tone (тон общения)
    - about (информация о себе)

    interests и goals могут быть пустыми массивами.
    """
    if not user:
        return False

    # Проверяем обязательные поля (tone и about)
    return all([
        user.tone is not None,
        user.about is not None and user.about.strip() != ""
    ])


async def check_message_limit(
    redis,
    user: User,
    daily_limit: int = 10
) -> Tuple[bool, int]:
    """
    Проверить лимит сообщений для пользователя.
    
    Логика:
    - Если есть активная подписка → безлимит
    - Если нет подписки → проверяем счётчик в Redis
    
    Args:
        redis: Redis клиент (redis_client.py)
        user: Объект пользователя из БД
        daily_limit: Дневной лимит сообщений (по умолчанию 10)
    
    Returns:
        Tuple[can_send, messages_left]:
            - can_send: bool - можно ли отправить сообщение
            - messages_left: int - сколько осталось (-1 = безлимит)
    
    Example:
        >>> can_send, left = await check_message_limit(redis, user)
        >>> if not can_send:
        >>>     await message.reply("Лимит исчерпан!")
    """
    # 1. Проверяем подписку
    if user.subscription_expires_at:
        # Проверяем, что подписка ещё активна
        now = datetime.now(user.subscription_expires_at.tzinfo)
        if user.subscription_expires_at > now:
            return (True, -1)  # -1 означает безлимит
    
    # 2. Проверяем счётчик в Redis
    today = datetime.utcnow().date().isoformat()  # "2025-10-22"
    key = f"msg_limit:{user.telegram_id}:{today}"
    
    # Инкрементируем счётчик
    count = await redis.incr(key)
    
    # Устанавливаем TTL только при первом сообщении
    if count == 1:
        await redis.expire(key, 86400)  # 24 часа
    
    # 3. Проверяем лимит
    if count > daily_limit:
        return (False, 0)  # Лимит превышен
    
    # Осталось сообщений
    messages_left = daily_limit - count
    return (True, messages_left)


async def get_subscription_status(user: User) -> dict:
    """
    Получить статус подписки пользователя.
    
    Args:
        user: Объект пользователя из БД
    
    Returns:
        dict с информацией о подписке:
            - has_subscription: bool
            - expires_at: datetime | None
            - days_left: int | None
            - is_expired: bool
    """
    if not user.subscription_expires_at:
        return {
            "has_subscription": False,
            "expires_at": None,
            "days_left": None,
            "is_expired": False
        }
    
    expires_at = user.subscription_expires_at
    now = datetime.now(expires_at.tzinfo)
    is_active = expires_at > now
    
    if is_active:
        days_left = (expires_at - now).days
        return {
            "has_subscription": True,
            "expires_at": expires_at,
            "days_left": days_left,
            "is_expired": False
        }
    else:
        return {
            "has_subscription": False,
            "expires_at": expires_at,
            "days_left": 0,
            "is_expired": True
        }
