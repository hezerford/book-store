# BookStore

BookStore - это веб-приложение для продажи книг, где пользователи могут просматривать, искать и покупать книги. Пользователи также могут добавлять книги в избранное и управлять своим профилем.

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/hezerford/book-store.git
    ```

2. Перейдите в директорию проекта:

    ```bash
    cd online_store
    ```

3. Создайте виртуальное окружение:

    ```bash
    python -m venv venv
    ```

4. Активируйте виртуальное окружение:

    - Для Windows:

    ```bash
    .\venv\Scripts\activate
    ```

    - Для macOS/Linux:

    ```bash
    source venv/bin/activate
    ```

5. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

6. Примените миграции:

    ```bash
    python manage.py migrate
    ```

7. Запустите сервер:

    ```bash
    python manage.py runserver
    ```

8. Перейдите по адресу http://127.0.0.1:8000/ в вашем веб-браузере.

## Использование

- Создайте аккаунт или войдите, если у вас уже есть аккаунт.
- Исследуйте книжный магазин, просматривайте книги и добавляйте их в избранное.
- Управляйте своим профилем, редактируйте информацию о себе.
- Добавляйте интересующие книги в корзину

## Технологии

- Python
- Django
- Django Rest Framework
- HTML/CSS
- Bootstrap

## Автор

Бакланов Иван

## Лицензия

Этот проект лицензирован по лицензии MIT