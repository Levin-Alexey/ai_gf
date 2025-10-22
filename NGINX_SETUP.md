# 🚀 Настройка nginx для pay.aigirlfriendbot.ru

## 📋 Конфигурация

### 1. Установить nginx (если ещё не установлен)

```bash
sudo apt update
sudo apt install nginx
```

---

### 2. Создать конфигурацию для домена

**Файл:** `/etc/nginx/sites-available/pay.aigirlfriendbot.ru`

```nginx
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
```

---

### 3. Получить SSL сертификат (Let's Encrypt)

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d pay.aigirlfriendbot.ru

# Certbot автоматически:
# 1. Получит сертификат
# 2. Обновит конфигурацию nginx
# 3. Настроит автопродление
```

---

### 4. Активировать конфигурацию

```bash
# Создать символическую ссылку
sudo ln -s /etc/nginx/sites-available/pay.aigirlfriendbot.ru /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезапустить nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

---

### 5. Настроить DNS

В панели управления доменом (где купили домен):

**Добавить A-запись:**
```
Тип: A
Имя: pay
Значение: 72.56.69.63
TTL: 300
```

**Проверка:**
```bash
# Подождите 5-10 минут после настройки DNS, затем:
ping pay.aigirlfriendbot.ru
# Должен пинговаться 72.56.69.63
```

---

### 6. Проверка работы

```bash
# HTTP (должен редиректить на HTTPS)
curl -I http://pay.aigirlfriendbot.ru/health

# HTTPS
curl https://pay.aigirlfriendbot.ru/health
# Ожидается: {"status":"healthy","timestamp":"..."}
```

---

## 🔥 Быстрая настройка (все команды сразу)

```bash
# 1. Установка nginx
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y

# 2. Создание конфигурации
sudo nano /etc/nginx/sites-available/pay.aigirlfriendbot.ru
# (вставить конфигурацию выше, сохранить Ctrl+O, выйти Ctrl+X)

# 3. Активация
sudo ln -s /etc/nginx/sites-available/pay.aigirlfriendbot.ru /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. SSL сертификат
sudo certbot --nginx -d pay.aigirlfriendbot.ru

# 5. Проверка
curl https://pay.aigirlfriendbot.ru/health
```

---

## 📝 Настройка в ЮKassa

После настройки nginx:

1. Откройте: https://yookassa.ru/my/shop-settings
2. Найдите **"HTTP-уведомления"**
3. Добавьте URL: `https://pay.aigirlfriendbot.ru/webhook/yookassa`
4. Выберите события:
   - ✅ `payment.succeeded`
   - ✅ `payment.canceled`
5. Сохраните

---

## ✅ Проверка

### 1. DNS работает
```bash
ping pay.aigirlfriendbot.ru
# 72.56.69.63
```

### 2. HTTPS работает
```bash
curl https://pay.aigirlfriendbot.ru/health
# {"status":"healthy","timestamp":"..."}
```

### 3. Webhook сервер работает
```bash
sudo systemctl status ai-gf-webhook
# Active: active (running)
```

### 4. Логи nginx
```bash
tail -f /var/log/nginx/pay.aigirlfriendbot.ru.access.log
```

---

## 🐛 Troubleshooting

### DNS не резолвится
```bash
# Проверить DNS
nslookup pay.aigirlfriendbot.ru
dig pay.aigirlfriendbot.ru

# Подождать 5-10 минут после настройки
```

### SSL не работает
```bash
# Перезапустить certbot
sudo certbot --nginx -d pay.aigirlfriendbot.ru --force-renewal

# Проверить сертификат
sudo certbot certificates
```

### 502 Bad Gateway
```bash
# Проверить webhook сервер
sudo systemctl status ai-gf-webhook

# Перезапустить
sudo systemctl restart ai-gf-webhook
```

---

## 🎯 Итого

После настройки у вас будет:
- ✅ Домен: `pay.aigirlfriendbot.ru`
- ✅ HTTPS через Let's Encrypt
- ✅ Webhook URL: `https://pay.aigirlfriendbot.ru/webhook/yookassa`
- ✅ Автопродление SSL сертификата
- ✅ Логирование всех запросов

**Готово к приёму платежей!** 💰
