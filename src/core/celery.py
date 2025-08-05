from __future__ import absolute_import, unicode_literals

from celery import Celery
from celery.schedules import crontab

app = Celery("core")

app.conf.beat_schedule = {
    "delete-old-anonymous-carts-everyday": {
        "task": "cart.tasks.delete_old_anonymous_carts",
        "schedule": crontab(hour=0, minute=0),  # Ежедневно в полночь
    },
}


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Отладка
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
