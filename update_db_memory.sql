-- Обновление базы данных для долгосрочной памяти
-- Выполните этот скрипт в вашей PostgreSQL базе данных

-- Создание enum типов для новых таблиц
CREATE TYPE memory_type AS ENUM (
    'fact',
    'preference', 
    'emotion',
    'event',
    'relationship',
    'goal',
    'fear',
    'dream'
);

CREATE TYPE memory_importance AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Создание таблицы воспоминаний пользователей
CREATE TABLE user_memories (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    memory_type memory_type NOT NULL,
    importance memory_importance NOT NULL DEFAULT 'medium',
    tags TEXT[],
    emotional_tone TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Создание таблицы эмоций пользователей
CREATE TABLE user_emotions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    emotion TEXT NOT NULL,
    intensity FLOAT NOT NULL,
    context TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Создание таблицы отношений пользователей
CREATE TABLE user_relationships (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    person_name TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    description TEXT,
    importance memory_importance NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Создание индексов для оптимизации
CREATE INDEX idx_memories_user_id ON user_memories(user_id);
CREATE INDEX idx_memories_type ON user_memories(memory_type);
CREATE INDEX idx_memories_importance ON user_memories(importance);
CREATE INDEX idx_memories_created_at ON user_memories(created_at);
CREATE INDEX idx_memories_tags ON user_memories USING GIN(tags);

CREATE INDEX idx_emotions_user_id ON user_emotions(user_id);
CREATE INDEX idx_emotions_recorded_at ON user_emotions(recorded_at);
CREATE INDEX idx_emotions_emotion ON user_emotions(emotion);

CREATE INDEX idx_relationships_user_id ON user_relationships(user_id);
CREATE INDEX idx_relationships_type ON user_relationships(relationship_type);
CREATE INDEX idx_relationships_importance ON user_relationships(importance);

-- Создание триггера для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_memories_updated_at 
    BEFORE UPDATE ON user_memories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_relationships_updated_at 
    BEFORE UPDATE ON user_relationships 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Добавление комментариев к таблицам
COMMENT ON TABLE user_memories IS 'Долгосрочная память о пользователях';
COMMENT ON TABLE user_emotions IS 'Эмоциональные состояния пользователей';
COMMENT ON TABLE user_relationships IS 'Информация об отношениях пользователей';

COMMENT ON COLUMN user_memories.content IS 'Содержимое воспоминания';
COMMENT ON COLUMN user_memories.memory_type IS 'Тип воспоминания';
COMMENT ON COLUMN user_memories.importance IS 'Важность воспоминания';
COMMENT ON COLUMN user_memories.tags IS 'Теги для категоризации';
COMMENT ON COLUMN user_memories.emotional_tone IS 'Эмоциональный тон (positive/negative/neutral)';
COMMENT ON COLUMN user_memories.confidence_score IS 'Уровень уверенности в информации (0.0-1.0)';

COMMENT ON COLUMN user_emotions.emotion IS 'Тип эмоции (happy, sad, anxious, etc.)';
COMMENT ON COLUMN user_emotions.intensity IS 'Интенсивность эмоции (0.0-1.0)';
COMMENT ON COLUMN user_emotions.context IS 'Контекст эмоции';

COMMENT ON COLUMN user_relationships.person_name IS 'Имя человека';
COMMENT ON COLUMN user_relationships.relationship_type IS 'Тип отношений (family, friend, colleague, etc.)';
COMMENT ON COLUMN user_relationships.description IS 'Описание отношений';
COMMENT ON COLUMN user_relationships.importance IS 'Важность отношений';

-- Проверка создания таблиц
SELECT 'user_memories table created' as status;
SELECT 'user_emotions table created' as status;
SELECT 'user_relationships table created' as status;
