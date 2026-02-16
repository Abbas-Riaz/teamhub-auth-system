# celery_app/tasks.py
from celery import shared_task
import time


@shared_task
def slow_add(x, y):
    time.sleep(2)
    return x + y
