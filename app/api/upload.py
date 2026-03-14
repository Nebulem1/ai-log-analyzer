from fastapi import APIRouter, UploadFile, File
from celery import chord, group
from app.services.validator import validate_csv
from app.services.parser import parse_logs
from app.tasks.analyze import analyze_error_task
from app.tasks.report import generate_report
from app.db.database import AsyncSessionLocal
from app.db.models import Job
from app.schemas.job import JobCreateResponse
import uuid

router = APIRouter()

@router.post("/upload", response_model=JobCreateResponse)
async def upload_logs(file: UploadFile = File(...)):

    # 1. CSV validate karo
    df = validate_csv(file.file)

    # 2. Parse karo — unique errors nikalo
    unique_errors = parse_logs(df)

    # 3. Job DB mein save karo
    job_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        job = Job(
            id=uuid.UUID(job_id),
            file_name=file.filename,
            status="processing",
            total_lines=len(df),
            unique_errors=len(unique_errors)
        )
        session.add(job)
        await session.commit()

    # 4. Celery chord banao
    tasks = [analyze_error_task.s(error) for error in unique_errors]

    chord(
        group(*tasks),
        generate_report.s(job_id)
    ).delay()

    return JobCreateResponse(
        job_id=job_id,
        file_name=file.filename,
        status="processing",
        message="File uploaded, analysis started"
    )