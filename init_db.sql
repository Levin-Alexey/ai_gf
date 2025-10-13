-- Скрипт для инициализации базы данных PostgreSQL
-- Запустите этот файл перед первым запуском бота:
-- psql -U your_user -d ai_gf -f init_db.sql

-- Создание enum типов
CREATE TYPE gf_tone AS ENUM (
  'gentle','friendly','neutral','sarcastic','formal'
);

CREATE TYPE gf_interest AS ENUM (
  'work','startups','sport','movies','games',
  'music','travel','self_growth','psychology','ai_tech','books'
);

CREATE TYPE gf_goal AS ENUM (
  'support','motivation','chitchat','advice','learn_english',
  'project_ideas','brainstorm','stress_relief','accountability','daily_checkin'
);

-- Таблица users будет создана автоматически через SQLAlchemy
-- Но если хотите создать её вручную:

CREATE TABLE IF NOT EXISTS users (
  id              BIGSERIAL PRIMARY KEY,
  telegram_id     BIGINT      NOT NULL UNIQUE,
  username        TEXT,
  first_name      TEXT,
  last_name       TEXT,

  display_name    TEXT,
  tone            gf_tone       NOT NULL DEFAULT 'friendly',
  interests       gf_interest[] NOT NULL DEFAULT '{}',
  goals           gf_goal[]     NOT NULL DEFAULT '{}',
  about           TEXT,

  first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_started_at TIMESTAMPTZ,
  last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_username_ci ON users (LOWER(username));
CREATE INDEX IF NOT EXISTS idx_users_tone ON users(tone);
CREATE INDEX IF NOT EXISTS idx_users_interests ON users USING GIN (interests);
CREATE INDEX IF NOT EXISTS idx_users_goals ON users USING GIN (goals);

-- Вспомогательная функция для объединения массивов без дубликатов
CREATE OR REPLACE FUNCTION array_union_distinct(anyarray, anyarray)
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT DISTINCT e FROM unnest($1 || $2) AS e);
$$ LANGUAGE sql IMMUTABLE;

-- Функция для автоматического обновления временных меток
CREATE OR REPLACE FUNCTION set_users_timestamps()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  IF TG_OP = 'UPDATE' AND NEW.last_seen_at IS NOT DISTINCT FROM OLD.last_seen_at THEN
    NEW.last_seen_at := NOW();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для обновления временных меток
DROP TRIGGER IF EXISTS trg_users_timestamps ON users;
CREATE TRIGGER trg_users_timestamps
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_users_timestamps();

