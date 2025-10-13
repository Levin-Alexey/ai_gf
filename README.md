# AI_GF - Telegram Bot

Telegram бот на основе Aiogram 3.x с поддержкой PostgreSQL через SQLAlchemy.

## Установка

### 1. Активация виртуального окружения

**Git Bash:**
```bash
source venv/Scripts/activate
```

**CMD (Windows):**
```cmd
venv\Scripts\activate.bat
```

### 2. Установка зависимостей

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Настройка базы данных PostgreSQL

### Подключение к серверу PostgreSQL

Если у вас уже есть PostgreSQL на сервере:

1. **Создайте базу данных (если ещё не создана):**
   ```bash
   # Подключитесь к вашему серверу
   psql -h ваш_хост -U ваш_пользователь -d postgres
   
   # Создайте базу данных
   CREATE DATABASE ai_gf;
   \q
   ```

2. **Примените SQL схему:**
   ```bash
   # Через командную строку
   psql -h ваш_хост -U ваш_пользователь -d ai_gf -f init_db.sql
   ```
   
   Или откройте `init_db.sql` в pgAdmin/DBeaver и выполните его содержимое.

3. **Настройте DATABASE_URL** в файле `.env` (см. ниже)

### Локальная установка (опционально)

Если нужна локальная база данных для разработки:

1. Установите PostgreSQL:
   - Windows: https://www.postgresql.org/download/windows/
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`

2. Создайте БД и примените схему (см. команды выше)

## Настройка бота

### 1. Получите токен бота
- Найдите [@BotFather](https://t.me/BotFather) в Telegram
- Создайте нового бота командой `/newbot`
- Скопируйте полученный токен

### 2. Создайте файл .env
Создайте файл `.env` в корне проекта (используйте `env_example.txt` как шаблон):

```env
# Токен Telegram бота
BOT_TOKEN=ваш_токен_от_BotFather

# URL подключения к PostgreSQL на ВАШЕМ сервере
DATABASE_URL=postgresql+asyncpg://пользователь:пароль@хост:порт/ai_gf
```

**Примеры DATABASE_URL:**
```env
# Локальный PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_gf

# Удалённый сервер по IP
DATABASE_URL=postgresql+asyncpg://myuser:mypass123@192.168.1.100:5432/ai_gf

# Удалённый сервер по домену
DATABASE_URL=postgresql+asyncpg://dbuser:secretpass@db.example.com:5432/ai_gf
```

## Запуск бота

```bash
python main.py
```

При успешном запуске вы увидите:
```
2025-10-13 10:00:00 - __main__ - INFO - Запуск бота...
2025-10-13 10:00:00 - __main__ - INFO - База данных инициализирована
2025-10-13 10:00:00 - __main__ - INFO - Бот запущен и готов к работе! 🚀
```

## Структура проекта

```
AI_GF/
├── venv/                 # Виртуальное окружение
├── main.py              # Главный файл бота
├── models.py            # SQLAlchemy модели
├── database.py          # Подключение к БД
├── crud.py              # CRUD операции
├── init_db.sql          # SQL схема базы данных
├── requirements.txt     # Зависимости проекта
├── env_example.txt      # Пример .env файла
├── .env                 # Конфигурация (не в git)
├── .gitignore          # Игнорируемые файлы
└── README.md           # Документация
```

## Используемые технологии

- **Aiogram 3.13.1** - асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0.36** - ORM для работы с базами данных
- **asyncpg 0.30.0** - асинхронный драйвер для PostgreSQL
- **psycopg2-binary** - PostgreSQL адаптер
- **python-dotenv** - управление переменными окружения
- **Alembic** - миграции базы данных

## База данных

### Модель User

Основные поля:
- `telegram_id` - ID пользователя в Telegram (уникальный)
- `username`, `first_name`, `last_name` - информация о пользователе
- `display_name` - отображаемое имя
- `tone` - тон общения (gentle, friendly, neutral, sarcastic, formal)
- `interests` - массив интересов (work, startups, sport, movies, games и др.)
- `goals` - массив целей (support, motivation, chitchat, advice и др.)
- `about` - описание пользователя
- Временные метки: `first_seen_at`, `last_started_at`, `last_seen_at`, `updated_at`

### CRUD операции

Доступные функции в `crud.py`:
- `get_user_by_telegram_id()` - получить пользователя
- `create_user()` - создать нового пользователя
- `get_or_create_user()` - получить или создать
- `update_user_tone()` - изменить тон общения
- `add_user_interests()` - добавить интересы
- `add_user_goals()` - добавить цели
- `update_user_about()` - обновить описание

## Команды бота

- `/start` - Стартовое приветствие и регистрация пользователя

## Разработка

### Миграции базы данных

Для управления миграциями используется Alembic:

```bash
# Инициализация (только первый раз)
alembic init alembic

# Создание новой миграции
alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head
```

## Устранение неполадок

**Проблема:** `Fatal error in launcher: Unable to create process`
- **Решение:** Используйте `python -m pip` вместо просто `pip`

**Проблема:** Ошибка подключения к PostgreSQL
- Проверьте, что PostgreSQL запущен
- Проверьте правильность DATABASE_URL в .env
- Убедитесь, что база данных `ai_gf` создана

**Проблема:** Ошибка при создании таблиц
- Убедитесь, что вы выполнили `init_db.sql` для создания enum типов
- Enum типы должны существовать до создания таблиц

