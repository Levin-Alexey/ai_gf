#!/bin/bash
# Скрипт для перезапуска сервисов AI GF на VDS

echo "🔄 Обновление кода с GitHub..."
cd /root/AI_GF || exit 1
git pull origin main

echo ""
echo "🛑 Остановка старых процессов..."

# Находим и убиваем процессы
WORKER_PID=$(ps aux | grep "run_worker.py" | grep -v grep | awk '{print $2}')
BOT_PID=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$WORKER_PID" ]; then
    echo "   Останавливаем LLM Worker (PID: $WORKER_PID)..."
    kill -9 $WORKER_PID
    sleep 2
fi

if [ ! -z "$BOT_PID" ]; then
    echo "   Останавливаем Bot (PID: $BOT_PID)..."
    kill -9 $BOT_PID
    sleep 2
fi

echo ""
echo "✅ Старые процессы остановлены"
echo ""
echo "🚀 Запуск сервисов..."

# Запускаем воркер
nohup python3 run_worker.py > logs/worker.log 2>&1 &
WORKER_NEW_PID=$!
echo "   ✅ LLM Worker запущен (PID: $WORKER_NEW_PID)"

sleep 3

# Запускаем бота
nohup python3 main.py > logs/bot.log 2>&1 &
BOT_NEW_PID=$!
echo "   ✅ Bot запущен (PID: $BOT_NEW_PID)"

echo ""
echo "📊 Проверка процессов:"
ps aux | grep -E "run_worker.py|main.py" | grep -v grep

echo ""
echo "✅ ГОТОВО! Сервисы перезапущены."
echo ""
echo "📝 Для просмотра логов используйте:"
echo "   tail -f logs/worker.log"
echo "   tail -f logs/bot.log"
