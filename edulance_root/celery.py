import os
from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edulance_root.settings")

app = Celery("edulance")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()


app.conf.beat_schedule = {
    "check-recurring-aasks": {
        "task": "common.tasks.test_beat_task",
        "schedule": crontab(minute="*"),  # This runs every minute
        # "schedule": crontab(minute=0, hour=0),  # This runs every midnight
    },
}
app.conf.update(include=["common.tasks"])
