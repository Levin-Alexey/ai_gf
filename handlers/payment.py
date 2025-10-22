"""
Обработчики оплаты и подписки
"""
import logging
import uuid
from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from yookassa import Configuration, Payment
from config import PAYMENT_SHOP_ID, PAYMENT_SECRET_KEY, PAYMENT_RETURN_URL

router = Router()
logger = logging.getLogger(__name__)

# Настройка ЮKassa
Configuration.account_id = PAYMENT_SHOP_ID
Configuration.secret_key = PAYMENT_SECRET_KEY


@router.callback_query(lambda c: c.data == "pay")
async def handle_pay_button(callback: CallbackQuery):
    """Обработчик кнопки 'Оформить подписку'"""
    await callback.answer()
    
    await callback.message.answer(
        "💎 <b>Подписка</b>\n\n"
        "С подпиской вы получите:\n"
        "• ♾️ Безлимитные сообщения\n"
        "• 🎭 Доступ ко всем персонажам\n"
        "• ⚡ Быстрые ответы\n"
        "• 💬 Приоритетная поддержка\n\n"
        "<i>1 месяц доступа — всего 10₽</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📅 1 месяц — 10₽",
                callback_data="subscribe_1m"
            )],
            [InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_payment"
            )]
        ])
    )
    
    logger.info(
        f"Пользователь {callback.from_user.id} открыл меню подписки"
    )


@router.callback_query(lambda c: c.data.startswith("subscribe_"))
async def handle_subscribe(callback: CallbackQuery):
    """Обработчик выбора тарифа подписки"""
    await callback.answer()
    
    period = callback.data.replace("subscribe_", "")
    
    # Определяем параметры тарифа
    plans = {
        "1m": {"name": "1 месяц", "price": 10, "days": 30}
    }
    
    plan = plans.get(period)
    if not plan:
        await callback.message.answer("❌ Неизвестный тариф")
        return
    
    telegram_id = callback.from_user.id
    
    try:
        # Создаём платёж в ЮKassa
        idempotence_key = str(uuid.uuid4())
        
        payment = Payment.create({
            "amount": {
                "value": str(plan['price']),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": PAYMENT_RETURN_URL
            },
            "capture": True,
            "description": f"Подписка AI GF: {plan['name']}",
            "metadata": {
                "telegram_id": str(telegram_id),
                "days": str(plan['days']),
                "plan": period
            }
        }, idempotence_key)
        
        # Получаем ссылку на оплату
        payment_url = payment.confirmation.confirmation_url
        
        # Отправляем пользователю
        await callback.message.answer(
            f"💳 <b>Оплата подписки</b>\n\n"
            f"Тариф: <b>{plan['name']}</b>\n"
            f"Сумма: <b>{plan['price']}₽</b>\n\n"
            f"Нажмите кнопку ниже для перехода к оплате.\n"
            f"После успешной оплаты подписка активируется автоматически! ✨",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💳 Перейти к оплате",
                    url=payment_url
                )],
                [InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_payment"
                )]
            ])
        )
        
        logger.info(
            f"Создан платёж для {telegram_id}: "
            f"ID={payment.id}, тариф={period}, сумма={plan['price']}₽"
        )
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}", exc_info=True)
        await callback.message.answer(
            "❌ Произошла ошибка при создании платежа.\n"
            "Попробуйте позже или свяжитесь с поддержкой.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🏠 Вернуться в меню",
                    callback_data="cancel_payment"
                )
            ]])
        )


@router.callback_query(lambda c: c.data == "cancel_payment")
async def handle_cancel_payment(callback: CallbackQuery):
    """Обработчик отмены оплаты"""
    await callback.answer("Отменено")
    
    await callback.message.edit_text(
        "❌ Оплата отменена.\n\n"
        "Вы можете вернуться к подписке в любое время!",
        reply_markup=None
    )
    
    logger.info(
        f"Пользователь {callback.from_user.id} отменил оплату"
    )
