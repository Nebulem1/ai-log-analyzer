from app.celery_app import celery
from app.services.llm import analyze_error

@celery.task(bind=True, max_retries=3)
def analyze_error_task(self, error: dict):
    try:
        result = analyze_error(error)
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)