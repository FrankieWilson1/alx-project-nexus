import os
from celery import Celery

# Set the default Django settings module for the celery program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_rec_project.settings')

app = Celery('movie_rec_project')

app.config_from_object('django.config:settings', namespace='Celery')

# Load task module from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
