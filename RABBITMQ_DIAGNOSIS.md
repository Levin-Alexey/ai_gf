## 🐰 ПРОБЛЕМЫ С RABBITMQ НА VDS СЕРВЕРЕ

### 📊 Диагностика показала:
- ✅ TCP подключение к 5.23.53.246:5672 работает
- ❌ AMQP handshake не завершается (таймаут)

### 🔍 Возможные причины:

1. **RabbitMQ сервис не запущен или неправильно настроен**
2. **Учетные данные admin/password неверные**
3. **Пользователь admin не имеет прав на виртуальный хост '/'**
4. **Файрвол блокирует AMQP протокол**

### 🛠 Что нужно проверить на VDS сервере:

#### 1. Статус RabbitMQ сервиса:
```bash
sudo systemctl status rabbitmq-server
sudo systemctl start rabbitmq-server  # если не запущен
```

#### 2. Логи RabbitMQ:
```bash
sudo journalctl -u rabbitmq-server -f
```

#### 3. Список пользователей:
```bash
sudo rabbitmqctl list_users
```

#### 4. Создать/настроить пользователя admin:
```bash
# Создать пользователя
sudo rabbitmqctl add_user admin T7#mQ$vP2@wL9$nR6zE8*bY5cN3

# Дать права администратора
sudo rabbitmqctl set_user_tags admin administrator

# Дать права на виртуальный хост '/'
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

#### 5. Проверить виртуальные хосты:
```bash
sudo rabbitmqctl list_vhosts
sudo rabbitmqctl list_permissions -p /
```

#### 6. Проверить порты:
```bash
sudo netstat -tulpn | grep 5672
sudo ss -tulpn | grep 5672
```

#### 7. Проверить файрвол:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 5672/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=5672/tcp --permanent
sudo firewall-cmd --reload
```

#### 8. Тест подключения локально на сервере:
```bash
# Установить rabbitmq-admin tools если нет
sudo apt install rabbitmq-server  # или yum install rabbitmq-server

# Тест подключения
rabbitmqctl status
```

### 🚨 БЫСТРОЕ РЕШЕНИЕ:

1. **Подключитесь к VDS серверу по SSH**
2. **Проверьте статус RabbitMQ:** `sudo systemctl status rabbitmq-server`
3. **Если не запущен:** `sudo systemctl start rabbitmq-server`
4. **Создайте пользователя admin с правами:**
   ```bash
   sudo rabbitmqctl add_user admin T7#mQ$vP2@wL9$nR6zE8*bY5cN3
   sudo rabbitmqctl set_user_tags admin administrator
   sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
   ```

### 📋 После исправления на сервере:

Запустите тест еще раз:
```bash
python test_rabbitmq_vds.py
```

---

**💡 Основная проблема:** RabbitMQ сервер принимает TCP соединения, но не отвечает на AMQP протокол. Это типично для неправильно настроенного или незапущенного RabbitMQ сервиса.