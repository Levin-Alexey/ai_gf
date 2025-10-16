# 🔥 ЭКСТРЕННЫЕ КОМАНДЫ ДЛЯ RABBITMQ НА VDS
# Выполни эти команды одну за одной на сервере 5.23.53.246

# 1. Запуск RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# 2. Создание пользователя admin
sudo rabbitmqctl add_user admin 'T7#mQ$vP2@wL9$nR6zE8*bY5cN3'
sudo rabbitmqctl set_user_tags admin administrator  
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# 3. Настройка конфига для внешних подключений
sudo mkdir -p /etc/rabbitmq
sudo bash -c 'cat > /etc/rabbitmq/rabbitmq.conf << EOF
listeners.tcp.default = 5672
listeners.tcp.1 = 0.0.0.0:5672
loopback_users = none
heartbeat = 60
EOF'

# 4. Открытие портов в файрволе (Ubuntu/Debian)
sudo ufw allow 5672/tcp
sudo ufw allow 15672/tcp
sudo ufw --force enable

# 4. Открытие портов в файрволе (CentOS/RHEL) - если предыдущие команды не сработали
# sudo firewall-cmd --add-port=5672/tcp --permanent
# sudo firewall-cmd --add-port=15672/tcp --permanent  
# sudo firewall-cmd --reload

# 5. Включение веб-интерфейса
sudo rabbitmq-plugins enable rabbitmq_management

# 6. Перезапуск RabbitMQ
sudo systemctl restart rabbitmq-server

# 7. Проверка статуса
sudo systemctl status rabbitmq-server
sudo rabbitmqctl status
sudo netstat -tulpn | grep :5672