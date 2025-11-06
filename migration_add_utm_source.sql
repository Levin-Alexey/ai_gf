-- Миграция: добавление столбца utm_source в таблицу users
-- Дата создания: 2024
-- Описание: Добавляет столбец для хранения UTM метки источника привлечения пользователей
-- Пример использования: https://t.me/bot?start=vk (где vk - это utm_source)

-- Добавляем столбец utm_source для хранения UTM метки источника привлечения
-- Формат: VARCHAR(64), NULL (для обратной совместимости с существующими записями)
ALTER TABLE users
ADD COLUMN utm_source VARCHAR(64) NULL;

-- Добавляем комментарий к столбцу для документации
COMMENT ON COLUMN users.utm_source IS 'UTM метка источника привлечения пользователя (например, vk, facebook, etc.)';

-- Опционально: можно добавить индекс для быстрого поиска по UTM метке
-- CREATE INDEX idx_users_utm_source ON users(utm_source) WHERE utm_source IS NOT NULL;

