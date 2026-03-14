from fastapi import APIRouter, HTTPException
from app.db.database import AsyncSessionLocal
from app.db.models import Job
from app.schemas.job import JobStatusResponse
from sqlalchemy import select
import uuid

router = APIRouter()

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Job).where(Job.id == uuid.UUID(job_id))
        )
        job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        total_lines=job.total_lines,
        unique_errors=job.unique_errors,
        report=job.report
    )