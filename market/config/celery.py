import os
import logging
import datetime

from celery import Celery
from celery.schedules import crontab
from celery.app.log import TaskFormatter
from celery.signals import task_prerun, task_postrun

# Celery https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#django-first-steps
# Real Python https://realpython.com/asynchronous-tasks-with-django-and-celery/


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# set up periodic tasks
app.conf.beat_schedule = {
    "update-discount-status-every-midnight": {
        "task": "discount.tasks.update_discount_status",
        "schedule": crontab(minute=0, hour=0),
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@task_prerun.connect
def setup_task_logger(task_id, task, args, **kwargs):
    """
    Добавление FileHandler к logger.handlers при запуске команды.
    """
    logger = logging.getLogger("celery.task")

    if not os.path.exists(f"tmp/logs/celery.task/{task.name}"):
        os.makedirs(f"tmp/logs/celery.task/{task.name}")

    # FileHandler
    file_handler = logging.FileHandler(
        f'tmp/logs/celery.task/{task.name}/{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.log'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(TaskFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logger.addHandler(file_handler)


@task_postrun.connect
def cleanup_logger(task_id, task, args, **kwargs):
    """
    Удаление FileHandler из logger.handlers при завершении команды.
    """
    logger = logging.getLogger("celery.task")

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and task.name in handler.baseFilename:
            logger.removeHandler(handler)
