from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Response schema — job create hone ke baad user ko kya milega
class JobCreateResponse(BaseModel):
    job_id: UUID
    file_name: str
    status: str
    message: str

# Status check karne pe kya milega
class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    total_lines: int
    unique_errors: int
    report: dict | None

    class Config:
        from_attributes = True  # SQLAlchemy model se directly convert hoga