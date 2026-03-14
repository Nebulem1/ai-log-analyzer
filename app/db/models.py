from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from datetime import datetime
import uuid

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_lines = Column(Integer, default=0)
    unique_errors = Column(Integer, default=0)
    report = Column(JSON, nullable=True)        # final report yahan store hoga
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())