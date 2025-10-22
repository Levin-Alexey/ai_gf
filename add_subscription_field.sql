-- Миграция: добавление поля подписки для пользователей
-- Дата: 2025-10-22
-- Описание: Добавляет поле subscription_expires_at для управления подписками

-- Добавить колонку для хранения даты окончания подписки
ALTER TABLE users 
ADD COLUMN subscription_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Добавить индекс для быстрой проверки активных подписок
CREATE INDEX idx_users_subscription ON users(subscription_expires_at) 
WHERE subscription_expires_at IS NOT NULL;

-- Комментарий к колонке
COMMENT ON COLUMN users.subscription_expires_at IS 
'Дата и время окончания платной подписки. NULL = нет подписки, прошедшая дата = истёкшая подписка';
