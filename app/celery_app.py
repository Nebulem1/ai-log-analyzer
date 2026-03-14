from celery import Celery
from app.config import settings

celery = Celery(
    "log-analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL.replace("/0", "/1"),
    include=["app.tasks.analyze", "app.tasks.report"]
)

celery.conf.update(
    result_backend=settings.REDIS_URL.replace("/0", "/1"),
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)
