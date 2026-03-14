from app.celery_app import celery
from app.db.database import SyncSessionLocal
from app.db.models import Job
from sqlalchemy import update
import asyncio
import uuid

@celery.task
def generate_report(results: list, job_id: str):

    report = {
        "total_unique_errors": len(results),
        "critical": [r for r in results if r.get("severity") == "Critical"],
        "high": [r for r in results if r.get("severity") == "High"],
        "medium": [r for r in results if r.get("severity") == "Medium"],
        "low": [r for r in results if r.get("severity") == "Low"],
        "errors": results
    }

    with SyncSessionLocal() as session:
        session.execute(
            update(Job)
            .where(Job.id == uuid.UUID(job_id))
            .values(
                status="completed",
                unique_errors=len(results),
                report=report
            )
        )
        session.commit()

    return report