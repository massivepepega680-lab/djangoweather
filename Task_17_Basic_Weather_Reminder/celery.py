import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Task_17_Basic_Weather_Reminder.settings')

app = Celery('Task_17_Basic_Weather_Reminder')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()