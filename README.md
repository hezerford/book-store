# BookStore - Django Book Store Application

Современное веб-приложение для книжного магазина, построенное на Django с использованием REST API, Docker и Celery.

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

## 🛠 Технологии

- **Backend**: Django 5.1.4, Python 3.12
- **Database**: PostgreSQL
- **Cache**: Redis
- **API**: Django REST Framework
- **Documentation**: drf-spectacular (Swagger)
- **Testing**: pytest, pytest-django
- **Containerization**: Docker, docker-compose
- **Task Queue**: Celery
- **Security**: django-axes, django-simple-captcha

## 📋 Требования

- Python 3.12+
- Docker и docker-compose
- Poetry (для локальной разработки)

## 🚀 Быстрый старт с Docker

1. **Клонируйте репозиторий**

```bash
git clone https://github.com/hezerford/book-store
cd BookStore
```

2. **Создайте файл .env**

```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите с Docker**

```bash
docker-compose up --build
```

4. **Создайте суперпользователя**

```bash
docker-compose exec web python manage.py createsuperuser
```

Приложение будет доступно по адресу: http://localhost:8000

## 🔧 Локальная разработка

1. **Установите Poetry**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Установите зависимости**

```bash
poetry install
```

3. **Активируйте виртуальное окружение**

```bash
poetry shell
```

4. **Настройте базу данных**

```bash
# Установите PostgreSQL и Redis
# Создайте .env файл с настройками БД
```

5. **Выполните миграции**

```bash
python manage.py migrate
```

6. **Запустите сервер разработки**

```bash
python manage.py runserver
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src

# Запуск конкретного теста
pytest src/store/tests/test_views.py::test_homepage_view
```

## 📚 API Документация

После запуска приложения API документация доступна по адресам:

- Swagger UI: http://localhost:8000/api/docs/
- Schema: http://localhost:8000/api/schema/

## 🏗 Структура проекта

```
BookStore/
├── src/
│   ├── api/           # REST API
│   ├── authentication/ # Аутентификация
│   ├── cart/          # Корзина покупок
│   ├── core/          # Основные настройки
│   ├── store/         # Основная логика магазина
│   ├── user_profile/  # Профили пользователей
│   └── templates/     # Шаблоны
├── static/            # Статические файлы
├── docker-compose.yml # Docker конфигурация
└── pyproject.toml    # Зависимости Poetry
```

## 🔒 Безопасность

- Защита от брутфорс-атак (django-axes)
- CAPTCHA для форм
- Валидация паролей
- CSRF защита
- Безопасные настройки для production

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

IvanB <baklanovivan25@gmail.com>
