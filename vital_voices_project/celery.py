import os
from celery import Celery
import multiprocessing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vital_voices_project.settings')

app = Celery('vital_voices_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
cpu_count = multiprocessing.cpu_count()
app.conf.update(
    worker_concurrency=cpu_count,
    optimizer='fair',
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=3600,
    task_soft_time_limit=3540
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
