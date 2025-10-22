@echo off
REM Скрипт установки зависимостей для платёжной системы (Windows)

echo 📦 Установка зависимостей для ЮKassa и webhook...
echo.

.\venv\Scripts\pip.exe install yookassa==3.3.0
.\venv\Scripts\pip.exe install fastapi==0.115.4
.\venv\Scripts\pip.exe install uvicorn[standard]==0.32.0
.\venv\Scripts\pip.exe install pydantic==2.9.2

echo.
echo ✅ Зависимости установлены!
echo.
echo 📝 Следующие шаги:
echo 1. Добавьте WEBHOOK_URL в .env файл
echo 2. Запустите webhook сервер: python webhook_server.py
echo 3. Настройте webhook в ЮKassa: https://yookassa.ru/my/shop-settings
echo.
pause
