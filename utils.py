"""
Вспомогательные функции
"""
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
