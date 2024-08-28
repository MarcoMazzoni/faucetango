import os

from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faucetapi.settings')

app = Celery('faucet')
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.task_queues = [
#     Queue('tasks', Exchange('tasks'), routing_key='tasks',
#           queue_arguments={'x-max-priority': 10}),
# ]

app.conf.task_routes = {'faucet.celery_tasks.tasks.update_transaction_status': {'queue': 'celery1'}}
app.autodiscover_tasks()
