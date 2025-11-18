## Сервис уведомлений

Проект реализует API для создания пользовательских уведомлений с надёжной доставкой по следующим каналам: Email, SMS и Telegram. Если один канал недоступен, система автоматически пробует следующий из заданного порядка.

### Стек
- Django + Django REST Framework
- PostgreSQL
- Redis + Celery
- Docker / docker-compose

### Быстрый старт
1. Скопируйте пример настроек:
   ```bash
   cp env.example .env
   ```
2. Обновите значения переменных (пароли, SMTP, и т.д.).
3. (Опционально) Укажите `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD`, чтобы суперпользователь создавался автоматически при старте Docker.
4. Запустите проект:
   ```bash
   docker-compose up --build
   ```
   Доступные сервисы:
   - `http://localhost:8000` — API и админ-панель
   - Celery worker запускается автоматически
    - `http://localhost:8000/api/docs/` — Swagger UI (drf-spectacular)
    - `http://localhost:8000/api/redoc/` — ReDoc

### Локальный запуск без Docker
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser  # при необходимости
python manage.py runserver 0.0.0.0:8000
```

Celery:
```bash
celery -A app worker -l info
```

Redis:
```bash
redis-server
```
При локальном запуске не забудьте сменить хосты на localhost.

Документация OpenAPI:
- JSON-схема: `http://localhost:8000/api/schema/`
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

### Примеры API-запросов
Создать уведомление:
```bash
curl -X POST http://localhost:8000/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
        "recipient_email": "user@example.com",
        "recipient_phone": "+79993562133",
        "recipient_telegram": "@username",
        "subject": "Добро пожаловать",
        "body": "Спасибо за регистрацию!",
        "channel_order": ["email", "sms", "telegram"]
      }'
```

Переотправить уведомление:
```bash
curl -X POST http://localhost:8000/api/notifications/1/retry/
```

### Переменные окружения
Все ключевые параметры описаны в `env.example`:
- `POSTGRES_*` — настройки БД
- `CELERY_*` — брокер/бэкенд Redis
- `DEFAULT_FROM_EMAIL`, `EMAIL_*` — конфигурация SMTP
- `NOTIFICATION_DEFAULT_CHANNEL_ORDER` — порядок каналов по умолчанию
- `NOTIFICATION_SIMULATED_FAILURES` — перечислите каналы (через запятую), чтобы симулировать падение и проверить отказоустойчивость
- `DJANGO_SUPERUSER_*` — при указании создаётся суперпользователь во время `docker-compose up`

### Тесты
```bash
python manage.py test notifications
```

