"""
Вспомогательные функции
"""
from models import User


def is_profile_complete(user: User) -> bool:
    """
    Проверить, заполнен ли профиль пользователя полностью.

    Профиль считается заполненным, если у пользователя есть:
    - tone (тон общения)
    - interests (хотя бы пустой массив, не NULL)
    - goals (хотя бы пустой массив, не NULL)
    - about (информация о себе)
    """
    if not user:
        return False

    # Проверяем все обязательные поля
    return all([
        user.tone is not None,
        user.interests is not None,
        user.goals is not None,
        user.about is not None and user.about.strip() != ""
    ])
