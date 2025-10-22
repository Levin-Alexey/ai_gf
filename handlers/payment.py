"""
Обработчики оплаты и подписки
"""
import logging
import uuid
from datetime import datetime, timezone
from requests.exceptions import HTTPError

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from yookassa import Configuration, Payment
from config import (
    PAYMENT_SHOP_ID,
    PAYMENT_SECRET_KEY,
    PAYMENT_RETURN_URL,
    PAYMENT_RECEIPT_EMAIL,
    PAYMENT_RECEIPT_PHONE,
)

router = Router()
logger = logging.getLogger(__name__)

# Настройка ЮKassa
Configuration.account_id = PAYMENT_SHOP_ID
Configuration.secret_key = PAYMENT_SECRET_KEY


async def send_subscription_menu_message(target: Message):
    """Отправить меню подписки (1 месяц — 10₽)."""
    await target.answer(
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
    
    logger.info("Показано меню подписки (1м/10₽)")


@router.message(Command("pay"))
async def cmd_pay(message: Message):
    """Команда /pay — открыть меню подписки."""
    await send_subscription_menu_message(message)


@router.callback_query(lambda c: c.data == "pay")
async def handle_pay_button(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Оформить подписку'."""
    await callback.answer()
    await send_subscription_menu_message(callback.message)
    logger.info(f"Пользователь {callback.from_user.id} открыл меню подписки")


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
        
        # Формируем сумму в формате XX.XX (требование ЮKassa)
        amount_value = f"{plan['price']:.2f}"

        # Подготовка блока receipt.customer
        receipt_customer = {}
        if PAYMENT_RECEIPT_EMAIL:
            receipt_customer["email"] = PAYMENT_RECEIPT_EMAIL
        if PAYMENT_RECEIPT_PHONE and "phone" not in receipt_customer:
            # ЮKassa требует хотя бы одно поле: email или phone
            receipt_customer["phone"] = PAYMENT_RECEIPT_PHONE

        # Если ничего не задано в .env, используем безопасный дефолт email
        if not receipt_customer:
            receipt_customer["email"] = "billing@aigirlfriendbot.ru"

        payment_payload = {
            "amount": {
                "value": amount_value,
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
            },
            # Фискальный чек для магазинов с подключённой кассой (54‑ФЗ)
            "receipt": {
                "items": [
                    {
                        "description": f"Подписка AI GF — {plan['name']}",
                        "quantity": "1.00",
                        "amount": {"value": amount_value, "currency": "RUB"},
                        "vat_code": 1,  # 1 — без НДС
                        "payment_subject": "service",
                        "payment_mode": "full_payment"
                    }
                ],
                "customer": receipt_customer
            }
        }

        logger.info(
            "Создание платежа в ЮKassa: %s",
            {k: (v if k != 'amount' else v) for k, v in payment_payload.items()}
        )

        payment = Payment.create(payment_payload, idempotence_key)
        
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
        
    except HTTPError as e:
        err_body = ""
        try:
            err_body = e.response.text
        except Exception:
            pass
        logger.error(
            f"ЮKassa HTTPError: {e} | body={err_body}",
            exc_info=True
        )
        await callback.message.answer(
            "❌ Платёж не создан (ошибка 400). Попробуйте ещё раз позже." \
            "\nЕсли ошибка повторяется — напишите в поддержку.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🏠 Вернуться в меню",
                    callback_data="cancel_payment"
                )
            ]])
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
