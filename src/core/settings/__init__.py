import os

# Определяем, какие настройки использовать
if os.environ.get("DJANGO_SETTINGS_MODULE") is None:
    # По умолчанию используем development settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
