from fastapi import FastAPI
from app.api import upload, jobs, sample

app = FastAPI()

app.include_router(upload.router, tags=["Upload"])
app.include_router(jobs.router, tags=["Jobs"])
app.include_router(sample.router, tags=["Sample"])

@app.get("/health")
def health():
    return {"status": "ok"}