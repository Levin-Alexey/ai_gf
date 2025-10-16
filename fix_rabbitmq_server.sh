#!/bin/bash
# СКРИПТ ДЛЯ НАСТРОЙКИ RABBITMQ НА VDS СЕРВЕРЕ
# Выполни эти команды на сервере 5.23.53.246

echo "🔥 ЭКСТРЕННАЯ НАСТРОЙКА RABBITMQ ДЛЯ ВНЕШНИХ ПОДКЛЮЧЕНИЙ 🔥"
echo "=========================================================="

echo "1️⃣ Проверяем статус RabbitMQ..."
sudo systemctl status rabbitmq-server

echo ""
echo "2️⃣ Запускаем RabbitMQ если не запущен..."
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

echo ""
echo "3️⃣ Создаем пользователя admin с полными правами..."
sudo rabbitmqctl add_user admin 'T7#mQ$vP2@wL9$nR6zE8*bY5cN3'
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

echo ""
echo "4️⃣ РАЗРЕШАЕМ ВНЕШНИЕ ПОДКЛЮЧЕНИЯ - редактируем конфиг..."
sudo tee /etc/rabbitmq/rabbitmq.conf << 'EOF'
# Разрешить подключения с любых IP адресов
listeners.tcp.default = 5672
listeners.tcp.1 = 0.0.0.0:5672

# Отключить guest пользователя для безопасности  
loopback_users = none

# Настройки логирования
log.file.level = info
log.console = true
log.console.level = info

# Heartbeat настройки (увеличиваем таймауты)
heartbeat = 60
EOF

echo ""
echo "5️⃣ ОТКРЫВАЕМ ПОРТЫ В ФАЙРВОЛЕ..."

# Ubuntu/Debian
if command -v ufw >/dev/null 2>&1; then
    echo "Настраиваем UFW файрвол..."
    sudo ufw allow 5672/tcp
    sudo ufw allow 15672/tcp  # Веб-интерфейс управления
    sudo ufw --force enable
fi

# CentOS/RHEL
if command -v firewall-cmd >/dev/null 2>&1; then
    echo "Настраиваем firewalld..."
    sudo firewall-cmd --add-port=5672/tcp --permanent
    sudo firewall-cmd --add-port=15672/tcp --permanent
    sudo firewall-cmd --reload
fi

echo ""
echo "6️⃣ ВКЛЮЧАЕМ ВЕБ-ИНТЕРФЕЙС УПРАВЛЕНИЯ..."
sudo rabbitmq-plugins enable rabbitmq_management

echo ""
echo "7️⃣ ПЕРЕЗАПУСКАЕМ RABBITMQ..."
sudo systemctl restart rabbitmq-server

echo ""
echo "8️⃣ Ждем запуска (10 секунд)..."
sleep 10

echo ""
echo "9️⃣ ПРОВЕРЯЕМ СТАТУС И ПОДКЛЮЧЕНИЯ..."
sudo systemctl status rabbitmq-server
sudo rabbitmqctl status
sudo rabbitmqctl list_users
sudo rabbitmqctl list_permissions -p /

echo ""
echo "🔟 ПРОВЕРЯЕМ ОТКРЫТЫЕ ПОРТЫ..."
sudo netstat -tulpn | grep :5672 || sudo ss -tulpn | grep :5672

echo ""
echo "✅ ГОТОВО! Теперь RabbitMQ должен принимать внешние подключения!"
echo "📊 Веб-интерфейс доступен по адресу: http://5.23.53.246:15672"
echo "🔐 Логин: admin"
echo "🔐 Пароль: T7#mQ\$vP2@wL9\$nR6zE8*bY5cN3"
echo ""