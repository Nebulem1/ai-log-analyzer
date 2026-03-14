from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

SAMPLE_CSV = """timestamp,level,message,source
2026-03-14 10:23:45,ERROR,Database connection failed,app.py
2026-03-14 10:24:01,WARNING,High memory usage detected,monitor.py
2026-03-14 10:24:15,INFO,User logged in,auth.py
2026-03-14 10:25:00,ERROR,Database connection failed,db.py
2026-03-14 10:25:30,ERROR,Timeout exceeded,api.py
2026-03-14 10:26:00,ERROR,Timeout exceeded,router.py
2026-03-14 10:26:45,WARNING,High memory usage detected,worker.py
2026-03-14 10:27:00,ERROR,Null pointer exception,utils.py
"""

@router.get("/sample")
def download_sample():
    return StreamingResponse(
        io.StringIO(SAMPLE_CSV),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample_logs.csv"}
    )