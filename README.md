# BookStore — Django Book Store Application

Современное веб‑приложение книжного магазина на Django с REST API, Docker, Celery и продвинутым поиском (Elasticsearch).

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Функциональность

- **Каталог книг** с поиском и фильтрацией
- **Система корзины** с поддержкой сессий и пользователей
- **Профили пользователей** с загрузкой изображений
- **Система отзывов** с добавлением рейтинга
- **Система скидок** и уведомлений
- **REST API** с автоматической документацией
- **Безопасность** с защитой от брутфорс-атак и CAPTCHA
- **Фоновые задачи** с Celery
- **Кэширование** с Redis
- **Поиск** c автодополнением на ElasticSearch

## 🛠 Технологии

- Backend: Django 5.1, Python 3.12
- Database: PostgreSQL
- Cache/Broker: Redis
- API: Django REST Framework, drf-spectacular (Swagger)
- Queue: Celery (+ django-celery-beat/results)
- Search: Elasticsearch 8
- Testing: pytest, pytest-django
- Containers: Docker, docker-compose

## 📋 Требования

- Python 3.12+
- Docker и docker-compose
- Poetry (для локальной разработки)

## ⚙️ Окружения и переменные

- Окружения: `development`, `production`, `testing` (через `DJANGO_SETTINGS_MODULE`)
- Важные переменные (`.env`):
  - Django: `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `SITE_URL`
  - DB: `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`
  - Redis/Celery: `REDIS_URL`, `CELERY_BROKER_URL`
  - Email: `SMTP_EMAIL`, `SMTP_PASS`
  - Search: `ELASTICSEARCH_URL`

Создайте `.env` из примера:

```bash
cp .env.example .env
# Отредактируйте значения под своё окружение
```

## 🚀 Быстрый старт (Docker)

```bash
cp .env.example .env
docker-compose up --build -d
# Применить миграции и собрать статику
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser
# (Опционально) Индекс Elasticsearch
docker-compose exec web python manage.py search_index --create
docker-compose exec web python manage.py search_index --populate
```

Приложение: `http://localhost:8000`

Swagger: `http://localhost:8000/api/docs/`

## 🔧 Локальная разработка

```bash
poetry install
cp .env.example .env  # укажите локальные значения (например, DB_HOST=localhost)
poetry run python src/manage.py migrate
poetry run python src/manage.py runserver

# Celery (в отдельных терминалах)
poetry run celery -A core worker -l info
poetry run celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 🔎 Поиск (Elasticsearch)

Elasticsearch поднимается сервисом Docker. После старта:

```bash
docker-compose exec web python manage.py search_index --delete   # при необходимости
docker-compose exec web python manage.py search_index --create
docker-compose exec web python manage.py search_index --populate
```

Веб‑поиск доступен по маршруту `search/`. Для автодополнения используется JSON‑режим:

```
GET /search/?format=json&query=...
```

## 🧪 Тестирование

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src

# Конкретный тест
pytest src/store/tests/test_views.py::test_homepage_view -q
```

В тестовом окружении используются SQLite, локальная почта (`locmem`), Celery eager‑режим. Elasticsearch в тестах опционален.

## 📚 API Документация

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## 🏗 Структура проекта

```
BookStore/
├── src/
│   ├── api/            # REST API
│   ├── authentication/ # Аутентификация
│   ├── cart/           # Корзина
│   ├── core/           # Настройки и инфраструктура
│   ├── media/          # Медиа файлы
│   ├── reviews/        # Отзывы
│   ├── static/         # Статические файлы (css, img, js)
│   ├── store/          # Домены магазина
│   ├── user_profile/   # Профили пользователей
│   └── templates/      # Шаблоны
├── static/             # Статика
├── docker-compose.yml  # Docker конфигурация
└── pyproject.toml      # Зависимости Poetry
```

## 🔒 Безопасность

- Защита от брутфорса (django-axes)
- CAPTCHA для форм
- Валидация паролей, CSRF
- Отдельные настройки для production

## 🤝 Contributing

PR приветствуются. Для фич создавайте ветки `feature/...`, для исправлений — `fix/...`. 
Мержите через PR в `master`. Поддерживайте чистую историю коммитов.

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

IvanB <baklanovivan25@gmail.com>
