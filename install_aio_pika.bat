@echo off
echo 🔧 Миграция на aio-pika (асинхронный RabbitMQ)
echo ================================================

REM Активируем виртуальное окружение
if exist "venv\Scripts\activate.bat" (
    echo Активируем виртуальное окружение...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено!
    echo Создайте его командой: python -m venv venv
    pause
    exit /b 1
)

echo.
echo 📦 Удаляем старую библиотеку pika...
pip uninstall pika -y

echo.
echo 📦 Устанавливаем aio-pika...
pip install aio-pika==9.4.3

echo.
echo ✅ Установка завершена!
echo.
echo 🧪 Запускаем тест RabbitMQ...
python test_rabbitmq.py

echo.
echo ================================================
echo ✨ Готово! Теперь можете запустить бота:
echo    python main.py
pause

