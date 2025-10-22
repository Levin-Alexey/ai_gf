"""
Webhook сервер для обработки платежей от ЮKassa
"""
import logging
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import async_session_maker
from sqlalchemy import update, select
from models import User
from config import (
    BOT_TOKEN,
    YOOKASSA_DISABLE_SIGNATURE_CHECK,
    YOOKASSA_WEBHOOK_SECRET,
)
import aiohttp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI GF Payment Webhook")


class YookassaNotification(BaseModel):
    """Модель уведомления от ЮKassa"""
    type: str
    event: str
    object: dict


def verify_webhook_signature(body: bytes, signature: Optional[str]) -> bool:
    """
    Проверка подписи webhook от ЮKassa

    YooKassa использует отдельный секрет для вебхуков,
    который настраивается в личном кабинете.
    Мы используем YOOKASSA_WEBHOOK_SECRET.
    
    Args:
        body: Тело запроса в байтах
        signature: Подпись из заголовка
    
    Returns:
        True если подпись валидна
    """
    secret = YOOKASSA_WEBHOOK_SECRET or ""
    if not signature or not secret:
        logger.warning("Отсутствует подпись или секретный ключ вебхука")
        return False

    expected_signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


async def activate_subscription(telegram_id: int, days: int) -> Optional[datetime]:
    """
    Активировать подписку для пользователя
    
    Args:
        telegram_id: Telegram ID пользователя
        days: Количество дней подписки
    
    Returns:
        Дата окончания подписки при успехе, иначе None
    """
    try:
        async with async_session_maker() as session:
            # Проверяем существование пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"Пользователь {telegram_id} не найден")
                return None
            
            # Устанавливаем/продлеваем дату окончания подписки
            now_utc = datetime.now(timezone.utc)
            base = user.subscription_expires_at if (
                user.subscription_expires_at and user.subscription_expires_at > now_utc
            ) else now_utc
            expires_at = base + timedelta(days=days)
            
            # Обновляем подписку
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(subscription_expires_at=expires_at)
            )
            await session.execute(stmt)
            await session.commit()
            
            logger.info(
                f"✅ Подписка активирована/продлена для {telegram_id} "
                f"на {days} дней до {expires_at}"
            )
            return expires_at
            
    except Exception as e:
        logger.error(f"Ошибка активации подписки: {e}")
        return None


async def send_telegram_message(chat_id: int, text: str) -> None:
    """Отправить сообщение пользователю в Telegram через Bot API."""
    if not BOT_TOKEN:
        logger.warning("BOT_TOKEN не задан, уведомление пользователю не отправлено")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.warning(
                        f"Не удалось отправить Telegram уведомление: {resp.status} {body}"
                    )
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram уведомления: {e}")


@app.get("/")
async def root():
    """Проверка работоспособности сервера"""
    return {
        "status": "ok",
        "service": "AI GF Payment Webhook",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check для мониторинга"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


@app.post("/webhook/yookassa")
async def yookassa_webhook(
    request: Request,
    x_yookassa_signature: Optional[str] = Header(None)
):
    """
    Webhook для получения уведомлений от ЮKassa
    
    Документация: https://yookassa.ru/developers/using-api/webhooks
    """
    try:
        # Получаем тело запроса
        body = await request.body()
        
        # Определяем подпись из разных возможных заголовков
        signature = (
            x_yookassa_signature
            or request.headers.get("X-Yookassa-Signature")
            or request.headers.get("X-Webhook-Signature")
            or request.headers.get("Content-Signature")
        )

        # Проверяем подпись (ВАЖНО для безопасности!)
        if not verify_webhook_signature(body, signature):
            msg = "❌ Невалидная подпись webhook!"
            if not YOOKASSA_DISABLE_SIGNATURE_CHECK:
                logger.warning(msg)
                return JSONResponse(status_code=400, content={"error": "Invalid signature"})
            else:
                logger.warning(
                    msg + " Продолжаем по флагу YOOKASSA_DISABLE_SIGNATURE_CHECK=true"
                )
        
        # Парсим JSON
        data = await request.json()
        notification = YookassaNotification(**data)
        
        logger.info(f"📨 Получено уведомление: {notification.event}")
        
        # Обрабатываем успешный платёж
        if notification.event == "payment.succeeded":
            payment = notification.object
            
            # Извлекаем метаданные
            metadata = payment.get("metadata", {})
            telegram_id = metadata.get("telegram_id")
            plan_days = metadata.get("days")
            
            if not telegram_id or not plan_days:
                logger.error("❌ Отсутствуют telegram_id или days в metadata")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing metadata"}
                )
            
            # Активируем подписку
            expires_at = await activate_subscription(
                int(telegram_id),
                int(plan_days)
            )
            
            if expires_at:
                logger.info(f"✅ Платёж обработан для {telegram_id}")
                # Уведомление пользователю в Telegram
                try:
                    until_str = expires_at.astimezone(timezone.utc).strftime('%d.%m.%Y')
                    text = (
                        "✅ Оплата получена!\n\n"
                        f"Подписка активирована до <b>{until_str}</b>.\n"
                        "Спасибо за поддержку! 💙"
                    )
                    await send_telegram_message(int(telegram_id), text)
                except Exception as e:
                    logger.error(f"Не удалось отправить подтверждение в Telegram: {e}")
                return {"status": "success"}
            else:
                logger.error(f"❌ Не удалось активировать подписку {telegram_id}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Subscription activation failed"}
                )
        
        # Обрабатываем отмену платежа
        elif notification.event == "payment.canceled":
            payment = notification.object
            payment_id = payment.get("id")
            logger.info(f"❌ Платёж {payment_id} отменён")
            return {"status": "canceled"}
        
        # Другие события (логируем, но не обрабатываем)
        else:
            logger.info(f"ℹ️ Событие {notification.event} не требует обработки")
            return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/test")
async def test_webhook(request: Request):
    """
    Тестовый webhook для проверки без подписи
    ⚠️ Использовать только для разработки!
    """
    try:
        data = await request.json()
        
        telegram_id = data.get("telegram_id")
        days = data.get("days", 30)
        
        if not telegram_id:
            raise HTTPException(status_code=400, detail="Missing telegram_id")
        
        success = await activate_subscription(int(telegram_id), int(days))
        
        if success:
            return {"status": "success", "message": "Подписка активирована"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Не удалось активировать подписку"
            )
        
    except Exception as e:
        logger.error(f"Ошибка тестового webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Запускаем сервер
    logger.info("🚀 Запуск webhook сервера на порту 8000...")
    uvicorn.run(
        app,
        host="0.0.0.0",  # Слушаем на всех интерфейсах
        port=8000,
        log_level="info"
    )
