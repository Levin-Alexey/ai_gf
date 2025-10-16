# 🔧 Быстрое исправление проблемы с RabbitMQ

## Проблема
Сообщения не отправляются в очередь RabbitMQ из-за блокировки event loop.

## Причина
Использование **синхронной** библиотеки `pika` в **асинхронном** коде aiogram.

## Решение

### На VDS (Linux):
```bash
cd /root/ai_gf
source venv/bin/activate
bash install_aio_pika.sh
```

### На Windows:
```cmd
cd E:\dev\python\AI_GF
install_aio_pika.bat
```

### Или вручную:
```bash
# Linux/Mac
source venv/bin/activate
pip uninstall pika -y
pip install aio-pika==9.4.3
python test_rabbitmq.py

# Windows
venv\Scripts\activate
pip uninstall pika -y
pip install aio-pika==9.4.3
python test_rabbitmq.py
```

## Проверка
После установки запустите тест:
```bash
python test_rabbitmq.py
```

Вы должны увидеть:
```
✅ Подключение к RabbitMQ успешно!
✅ Тестовое сообщение отправлено в очередь!
✅ Отключение от RabbitMQ успешно!
🎉 RabbitMQ работает корректно!
```

## Что дальше?
Запустите бота и воркера:
```bash
# Терминал 1 - Бот
python main.py

# Терминал 2 - Воркер (LLM обработчик)
python run_worker.py
```

## Подробности
См. файл `MIGRATION_TO_AIO_PIKA.md` для полной информации о всех изменениях.

