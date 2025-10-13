# Быстрый старт AI_GF Bot

## 🚀 За 3 минуты

### 1. Активация окружения и установка зависимостей

**Git Bash:**
```bash
# Активировать venv
source venv/Scripts/activate

# Установить зависимости
python -m pip install -r requirements.txt
```

**CMD:**
```cmd
rem Активировать venv
venv\Scripts\activate.bat

rem Установить зависимости
python -m pip install -r requirements.txt
```

### 2. Примените SQL схему на сервере

**Если база данных ещё не создана:**
```bash
# Подключитесь к вашему серверу PostgreSQL
psql -h ваш_хост -U ваш_пользователь -d postgres

# Создайте базу данных
CREATE DATABASE ai_gf;
\q

# Примените схему
psql -h ваш_хост -U ваш_пользователь -d ai_gf -f init_db.sql
```

**Или через pgAdmin/DBeaver** - просто выполните содержимое файла `init_db.sql`

### 3. Настройка бота

Создайте файл `.env` с данными ВАШЕГО сервера:
```env
BOT_TOKEN=ваш_токен_от_BotFather

# Замените на данные ВАШЕГО сервера PostgreSQL:
DATABASE_URL=postgresql+asyncpg://пользователь:пароль@хост:порт/ai_gf

# Пример:
# DATABASE_URL=postgresql+asyncpg://myuser:mypassword@192.168.1.100:5432/ai_gf
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@server.example.com:5432/ai_gf
```

### 4. Запуск

```bash
python main.py
```

Если всё настроено правильно, вы увидите:
```
INFO - Запуск бота...
INFO - База данных инициализирована
INFO - Бот запущен и готов к работе! 🚀
```

## ❓ Проблемы?

- **pip не работает?** → Используйте `python -m pip` вместо `pip`
- **PostgreSQL не подключается?** → Проверьте DATABASE_URL, хост и порт
- **Ошибка enum типов?** → Убедитесь что выполнили `init_db.sql` на сервере
- **Ошибка соединения?** → Проверьте файрвол и что PostgreSQL принимает удалённые подключения

Полная документация в [README.md](README.md)

