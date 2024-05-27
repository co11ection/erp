import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
# Настройки Celery Beat для выполнения задачи каждую минуту
app.conf.beat_schedule = {
    "check-and-publish-news": {
        "task": "config.tasks.check_and_publish_news",
        "schedule": crontab(minute="*"),  # Запускать каждую минуту
    },
    "send_tg":{
        "task": "config.tasks.send_notification_tg",
        "schedule": crontab(hour=18)
    }
}
