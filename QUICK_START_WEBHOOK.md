# ⚡ Быстрая установка webhook сервера

## На сервере выполните:

```bash
cd /root/ai_gf

# 1. Установить зависимости
source venv/bin/activate
pip install yookassa==3.3.0 fastapi==0.115.4 uvicorn[standard]==0.32.0 pydantic==2.9.2

# 2. Установить и запустить сервис
chmod +x install_webhook_service.sh
./install_webhook_service.sh
```

**Готово!** Сервис автоматически установлен и запущен. ✅

---

## Проверка:

```bash
# Статус
sudo systemctl status ai-gf-webhook

# Логи
sudo journalctl -u ai-gf-webhook -f

# Health check
curl http://localhost:8000/health
```

---

## Дальше:

1. **Настройте ЮKassa:**
   - URL: `https://pay.aigirlfriendbot.ru/webhook/yookassa`
   - События: `payment.succeeded`, `payment.canceled`

2. **Настройте nginx** (см. `NGINX_SETUP.md`)

---

**Всё работает!** 🚀
