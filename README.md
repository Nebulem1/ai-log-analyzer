# AI-Powered Log Analyzer

A production-grade backend system that analyzes server logs using AI. Upload a CSV log file and get a detailed analysis report — root causes, severity ratings, and fix suggestions for every unique error — processed in parallel using distributed task queues.

---

## Architecture

```
Client
  │
  ▼
FastAPI (API Layer)
  │
  ├── CSV Validation & Parsing
  │     └── Deduplication + Frequency Counting
  │
  ├── PostgreSQL (Job Storage)
  │
  └── Celery + Redis (Task Queue)
        │
        ├── Worker 1 → Gemini LLM → Error Analysis
        ├── Worker 2 → Gemini LLM → Error Analysis
        ├── Worker 3 → Gemini LLM → Error Analysis
        │
        └── Chord Callback → Final Report → PostgreSQL
```

**Key Design Decisions:**
- **In-memory deduplication** before queuing — avoids redundant LLM calls for repeated errors
- **Celery Chord** — all error analysis tasks run in parallel; final report generates only after all complete
- **Sync SQLAlchemy in Celery workers** — avoids nested event loop issues with async in background tasks
- **Per-job isolation** — each upload creates an independent job with its own UUID

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Task Queue | Celery |
| Broker / Backend | Redis |
| Database | PostgreSQL + SQLAlchemy (Async) |
| Migrations | Alembic |
| AI / LLM | LangChain + Google Gemini |
| Containerization | Docker Compose |

---

## Project Structure

```
log-analyzer/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Pydantic BaseSettings — env config
│   ├── celery_app.py           # Celery instance
│   │
│   ├── api/
│   │   ├── upload.py           # CSV upload + validation endpoint
│   │   ├── jobs.py             # Job status + result endpoint
│   │   └── sample.py           # Sample CSV download
│   │
│   ├── tasks/
│   │   ├── analyze.py          # Celery task — LLM error analysis
│   │   └── report.py           # Chord callback — final report generation
│   │
│   ├── services/
│   │   ├── validator.py        # CSV column + format validation
│   │   ├── parser.py           # Deduplication + frequency grouping
│   │   └── llm.py              # LangChain + Gemini integration
│   │
│   ├── db/
│   │   ├── database.py         # Async + Sync SQLAlchemy engines
│   │   └── models.py           # Job model
│   │
│   └── schemas/
│       └── job.py              # Pydantic request/response schemas
│
├── alembic/                    # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- Google Gemini API Key — [Get it free from Google AI Studio](https://aistudio.google.com)

### Setup

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/log-analyzer.git
cd log-analyzer
```

**2. Create `.env` file:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/loganalyzer
LOCAL_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loganalyzer
REDIS_URL=redis://redis:6379/0
GOOGLE_API_KEY=your_gemini_api_key_here
```

**3. Start the database:**
```bash
docker compose up db redis -d
```

**4. Run database migrations:**
```bash
docker compose run --rm api alembic upgrade head
```

**5. Start all services:**
```bash
docker compose up --build
```

---

## API Endpoints

### `GET /sample`
Download a sample CSV file to understand the required format.

**Required CSV columns:**
| Column | Description | Example |
|---|---|---|
| `timestamp` | When the log was recorded | `2026-03-14 10:23:45` |
| `level` | Log level | `ERROR`, `WARNING`, `INFO`, `DEBUG` |
| `message` | Log message | `Database connection failed` |
| `source` | File/module that generated the log | `app.py` |

---

### `POST /upload`
Upload a CSV log file for analysis.

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_logs.csv"
```

**Response:**
```json
{
  "job_id": "abc-123",
  "file_name": "your_logs.csv",
  "status": "processing",
  "message": "File uploaded, analysis started"
}
```

---

### `GET /jobs/{job_id}`
Check the status and get the analysis report.

```bash
curl http://localhost:8000/jobs/abc-123
```

**Response (completed):**
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "total_lines": 1000,
  "unique_errors": 5,
  "report": {
    "total_unique_errors": 5,
    "critical": [...],
    "high": [...],
    "medium": [...],
    "low": [...],
    "errors": [
      {
        "message": "Database connection failed",
        "level": "ERROR",
        "count": 45,
        "first_seen": "2026-03-14 10:23:45",
        "last_seen": "2026-03-14 11:45:23",
        "sources": ["app.py", "db.py"],
        "root_cause": "PostgreSQL connection pool exhausted",
        "severity": "Critical",
        "fix": "Increase connection pool size or add retry logic"
      }
    ]
  }
}
```

---

## How It Works

1. **Upload** — User uploads a CSV log file
2. **Validate** — Required columns are checked; invalid files are rejected with a clear error message
3. **Parse** — All log lines are scanned in-memory; duplicate error messages are deduplicated with frequency counts, first/last seen timestamps, and source files tracked
4. **Queue** — Only unique errors are queued as individual Celery tasks — one task per unique error
5. **Analyze** — Workers process all tasks in parallel, calling the Gemini LLM for each unique error
6. **Report** — Once all tasks complete, a Chord callback aggregates results and saves the final report to PostgreSQL
7. **Retrieve** — User polls `/jobs/{job_id}` to get the completed report

---

## Monitoring

Flower dashboard available at `http://localhost:5555`

- Active tasks — real-time task execution
- Processed / Failed / Succeeded counts per worker
- Task history with execution time
- Retry tracking

## Scaling Workers

```bash
docker compose up --scale worker=5
```

Each worker handles tasks independently from the shared Redis queue.

---

## Interactive API Docs

Once running, visit: `http://localhost:8000/docs`
