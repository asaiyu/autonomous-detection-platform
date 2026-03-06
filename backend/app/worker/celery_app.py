from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "autonomous_detection_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.tasks.ingest_tasks",
        "app.worker.tasks.replay_tasks",
        "app.worker.tasks.triage_tasks",
        "app.worker.tasks.coverage_tasks",
    ],
)

celery_app.conf.task_default_queue = "default"
