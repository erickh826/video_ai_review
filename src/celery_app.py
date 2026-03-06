from celery import Celery
from src.config import settings

celery_app = Celery(
    "video_review",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Hong_Kong",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks in these modules
celery_app.autodiscover_tasks(["src.video_ingestion"])
