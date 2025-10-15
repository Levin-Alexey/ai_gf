# Обновление базы данных для долгосрочной памяти

## 🚨 ВАЖНО! Выполните эти команды перед запуском системы!

### 1. Подключитесь к вашей PostgreSQL базе данных:

```bash
psql -h 72.56.69.63 -U admingf -d gfdb
```

### 2. Выполните SQL скрипт обновления:

```sql
\i update_db_memory.sql
```

Или скопируйте и вставьте содержимое файла `update_db_memory.sql` в psql.

### 3. Проверьте создание таблиц:

```sql
\dt user_memories
\dt user_emotions  
\dt user_relationships
```

### 4. Проверьте enum типы:

```sql
\dT memory_type
\dT memory_importance
```

## 📋 Что создается:

### **Новые таблицы:**
- ✅ `user_memories` - долгосрочная память
- ✅ `user_emotions` - эмоциональные состояния
- ✅ `user_relationships` - информация об отношениях

### **Новые enum типы:**
- ✅ `memory_type` - типы воспоминаний
- ✅ `memory_importance` - уровни важности

### **Индексы и оптимизация:**
- ✅ Индексы для быстрого поиска
- ✅ GIN индексы для массивов тегов
- ✅ Триггеры для автоматического обновления

## 🔧 Альтернативный способ (если psql недоступен):

### Через Python скрипт:

```python
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def update_database():
    # Подключение к базе данных
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Чтение SQL файла
    with open('update_db_memory.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Выполнение скрипта
    await conn.execute(sql_script)
    
    print("База данных успешно обновлена!")
    await conn.close()

# Запуск
asyncio.run(update_database())
```

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ:

1. **Сделайте бэкап** базы данных перед обновлением
2. **Проверьте права доступа** пользователя admingf
3. **Убедитесь**, что база данных gfdb существует
4. **После обновления** можно запускать систему

## 🚀 После обновления:

1. Установите новые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите бота:
   ```bash
   python main.py
   ```

3. Запустите воркер:
   ```bash
   python run_worker.py
   ```

## 📊 Проверка работы:

После запуска система автоматически:
- ✅ Создаст векторную базу данных ChromaDB
- ✅ Загрузит модель для эмбеддингов
- ✅ Начнет сохранять воспоминания в PostgreSQL
- ✅ Создаст векторные эмбеддинги в ChromaDB
