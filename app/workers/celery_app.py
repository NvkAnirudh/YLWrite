import logging
from celery import Celery

from config.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/celery.log')
    ]
)

logger = logging.getLogger(__name__)

# Create Celery app
app = Celery(
    'youtube_linkedin_pipeline',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        'app.workers.tasks.transcript',
        'app.workers.tasks.summarize',
        'app.workers.tasks.linkedin_post',
        'app.workers.tasks.email'
    ]
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1
)

if __name__ == '__main__':
    app.start() 