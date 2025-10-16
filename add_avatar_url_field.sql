-- Добавление поля avatar_url в таблицу personas
ALTER TABLE personas 
ADD COLUMN avatar_url TEXT;

-- Добавление комментария к полю
COMMENT ON COLUMN personas.avatar_url IS 'URL аватара персонажа';
