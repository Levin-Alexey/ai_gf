#!/bin/bash

# 🚀 Полная установка платёжной системы на сервер

set -e  # Остановка при ошибке

echo "=========================================="
echo "🚀 Установка платёжной системы AI GF Bot"
echo "=========================================="
echo ""

# 1. Проверка, что мы на сервере
if [ ! -d "/root/ai_gf" ]; then
    echo "❌ Ошибка: Папка /root/ai_gf не найдена"
    echo "Запустите этот скрипт на сервере!"
    exit 1
fi

cd /root/ai_gf

# 2. Установка зависимостей Python
echo "📦 Устанавливаю Python зависимости..."
source venv/bin/activate
pip install yookassa==3.3.0 fastapi==0.115.4 uvicorn[standard]==0.32.0 pydantic==2.9.2
echo "✅ Python зависимости установлены"
echo ""

# 3. Проверка .env файла
echo "🔍 Проверяю .env конфигурацию..."
if ! grep -q "PAYMENT_SHOP_ID" .env; then
    echo "❌ Ошибка: PAYMENT_SHOP_ID не найден в .env"
    exit 1
fi
if ! grep -q "WEBHOOK_URL.*pay.aigirlfriendbot.ru" .env; then
    echo "❌ Ошибка: WEBHOOK_URL должен быть https://pay.aigirlfriendbot.ru/webhook/yookassa"
    exit 1
fi
echo "✅ .env конфигурация корректна"
echo ""

# 4. Тест системы
echo "🧪 Тестирую систему..."
python test_payment_system.py
if [ $? -ne 0 ]; then
    echo "❌ Тесты не прошли, исправьте ошибки!"
    exit 1
fi
echo "✅ Все тесты пройдены"
echo ""

# 5. Установка nginx
echo "🌐 Настройка nginx..."
apt update
apt install nginx certbot python3-certbot-nginx -y

# Создание конфигурации nginx
cat > /etc/nginx/sites-available/pay.aigirlfriendbot.ru << 'EOF'
# Redirect HTTP -> HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name pay.aigirlfriendbot.ru;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pay.aigirlfriendbot.ru;
    
    # SSL сертификаты (будут созданы через certbot)
    ssl_certificate /etc/letsencrypt/live/pay.aigirlfriendbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pay.aigirlfriendbot.ru/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Логи
    access_log /var/log/nginx/pay.aigirlfriendbot.ru.access.log;
    error_log /var/log/nginx/pay.aigirlfriendbot.ru.error.log;
    
    # Webhook endpoints
    location /webhook/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
    
    # Корневой endpoint
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/pay.aigirlfriendbot.ru /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
echo "✅ nginx настроен"
echo ""

# 6. Получение SSL сертификата
echo "🔒 Получение SSL сертификата..."
echo "ВАЖНО: Убедитесь, что DNS запись pay.aigirlfriendbot.ru указывает на этот сервер!"
read -p "DNS настроен? (y/n): " dns_ready
if [ "$dns_ready" != "y" ]; then
    echo "⚠️  Настройте DNS и запустите скрипт снова"
    exit 1
fi

certbot --nginx -d pay.aigirlfriendbot.ru --non-interactive --agree-tos --email admin@aigirlfriendbot.ru
echo "✅ SSL сертификат получен"
echo ""

# 7. Установка systemd service
echo "⚙️  Настройка systemd service..."
cp ai-gf-webhook.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-gf-webhook
systemctl start ai-gf-webhook
sleep 3
systemctl status ai-gf-webhook --no-pager
echo "✅ Webhook сервер запущен"
echo ""

# 8. Финальная проверка
echo "🎯 Финальная проверка..."
sleep 2

echo "Проверяю HTTP -> HTTPS редирект..."
curl -I http://pay.aigirlfriendbot.ru/health 2>&1 | grep "301"

echo "Проверяю HTTPS endpoint..."
curl -s https://pay.aigirlfriendbot.ru/health | grep "healthy"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ВСЁ ГОТОВО! Платёжная система работает!"
    echo "=========================================="
    echo ""
    echo "📝 Следующий шаг:"
    echo "1. Откройте: https://yookassa.ru/my/shop-settings"
    echo "2. Найдите 'HTTP-уведомления'"
    echo "3. Добавьте URL: https://pay.aigirlfriendbot.ru/webhook/yookassa"
    echo "4. Выберите события: payment.succeeded, payment.canceled"
    echo ""
    echo "🔍 Полезные команды:"
    echo "  - Логи webhook: journalctl -u ai-gf-webhook -f"
    echo "  - Логи nginx: tail -f /var/log/nginx/pay.aigirlfriendbot.ru.access.log"
    echo "  - Статус сервиса: systemctl status ai-gf-webhook"
    echo "  - Перезапуск: systemctl restart ai-gf-webhook"
    echo ""
else
    echo ""
    echo "❌ Ошибка при проверке HTTPS"
    echo "Проверьте логи:"
    echo "  - journalctl -u ai-gf-webhook -n 50"
    echo "  - tail -f /var/log/nginx/pay.aigirlfriendbot.ru.error.log"
fi
