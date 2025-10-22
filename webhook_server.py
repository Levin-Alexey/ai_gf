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
from config import PAYMENT_SECRET_KEY

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
    
    Args:
        body: Тело запроса в байтах
        signature: Подпись из заголовка
    
    Returns:
        True если подпись валидна
    """
    if not signature or not PAYMENT_SECRET_KEY:
        logger.warning("Отсутствует подпись или секретный ключ")
        return False
    
    # ЮKassa использует SHA-256 HMAC
    expected_signature = hmac.new(
        PAYMENT_SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


async def activate_subscription(telegram_id: int, days: int) -> bool:
    """
    Активировать подписку для пользователя
    
    Args:
        telegram_id: Telegram ID пользователя
        days: Количество дней подписки
    
    Returns:
        True если успешно
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
                return False
            
            # Устанавливаем дату окончания подписки
            expires_at = datetime.now(timezone.utc) + timedelta(days=days)
            
            # Обновляем подписку
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(subscription_expires_at=expires_at)
            )
            await session.execute(stmt)
            await session.commit()
            
            logger.info(
                f"✅ Подписка активирована для {telegram_id} "
                f"на {days} дней до {expires_at}"
            )
            return True
            
    except Exception as e:
        logger.error(f"Ошибка активации подписки: {e}")
        return False


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
        
        # Проверяем подпись (ВАЖНО для безопасности!)
        if not verify_webhook_signature(body, x_yookassa_signature):
            logger.warning("❌ Невалидная подпись webhook!")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
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
            success = await activate_subscription(
                int(telegram_id),
                int(plan_days)
            )
            
            if success:
                logger.info(f"✅ Платёж обработан для {telegram_id}")
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
