from app.celery_app import celery
from app.db.database import SyncSessionLocal
from app.db.models import Job
from sqlalchemy import update
import asyncio
import uuid

@celery.task
def generate_report(results: list, job_id: str):
    
    critical,high,medium,low=[],[],[],[]
    for r in results:
        match r.get("severity"):
            
            case "Critical":
                  critical.append(r)
            case "High":
                  high.append(r)
            case "Medium":
                medium.append(r)
            case "Low":
                low.append(r)
            
    report = {
        "total_unique_errors": len(results),
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
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