"""
Обработчик команды поддержки
"""
import logging
from aiogram import Router, F
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text.startswith("/support"))
async def handle_support_command(message: Message):
    """Обработчик команды /support"""
    logger.info(
        f"🆘 SUPPORT: Получена команда /support от пользователя "
        f"{message.from_user.id}"
    )

    await message.answer(
        "🆘 Служба поддержки\n\n"
        "Для обращения в поддержку напишите:\n"
        "https://t.me/AIGFSupport"
    )


# Дополнительный обработчик для случая, если команда не сработала
@router.message(F.text == "support")
async def handle_support_text(message: Message):
    """Обработчик текста 'support'"""
    logger.info(
        f"🆘 SUPPORT: Получен текст 'support' от пользователя "
        f"{message.from_user.id}"
    )
    await handle_support_command(message)


# Обработчик для русского текста "поддержка"
@router.message(F.text == "поддержка")
async def handle_support_russian(message: Message):
    """Обработчик текста 'поддержка'"""
    logger.info(
        f"🆘 SUPPORT: Получен текст 'поддержка' от пользователя "
        f"{message.from_user.id}"
    )
    await handle_support_command(message)
