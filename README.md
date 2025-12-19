# Leave Management System (LMS)

Backend service for a configurable Leave Management System.

Key goals:

- Configuration-driven policies and workflows (stored in DB; minimal hardcoded rules).
- Clean architecture boundaries: API → Engines → Repositories → DB.
- Append-only audit trail for all mutations.

## Tech stack

- FastAPI (HTTP API)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Celery + Redis (async tasks; scaffold)
- PostgreSQL (intended DB)

## Project structure

- `lms/app/main.py`: FastAPI app entrypoint
- `lms/app/api/`: HTTP controllers + dependencies
- `lms/app/engines/`: domain orchestration/business logic (controllers call engines)
- `lms/app/repositories/`: DB access + audit emission (no DB access elsewhere)
- `lms/app/models/`: SQLAlchemy models
- `lms/app/schemas/`: Pydantic request/response schemas
- `alembic/`: Alembic migrations

## Architecture guardrails (important)

- Controllers contain **no business logic**.
  - Controllers depend on **engines**, not repositories.
- Engines orchestrate work and enforce domain decisions.
  - Engines may call multiple repositories.
- Repositories are the **only** layer that talks to the database.
  - All mutations go through repositories.
  - Repositories emit audit events for mutations via `AuditRepository`.

## Prerequisites

- Python 3.12+ (this repo currently uses a local `.venv`)
- PostgreSQL 14+ (recommended: local install or Docker)
- (Optional) Redis for Celery tasks

## Setup (Windows / PowerShell)

### 1) Create/activate venv

If you already have `C:\Python_Programs\LMS_ORG_01\.venv`, you can skip creation.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

Configuration is read from environment variables (and optionally `.env`).

Common variables:

- `DATABASE_URL` (required for migrations):
  - Example: `postgresql://postgres:postgres@localhost:5432/lms_db`
- `SQL_ECHO` (optional): `true|false`
- `REDIS_URL` (optional)
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` (optional)

## Run the API

```powershell
python -m uvicorn lms.app.main:app --reload
```

Health check:

- `GET /health`

API routes are mounted under:

- `/api/v1`

## Database migrations (Alembic)

Alembic is configured to use `DATABASE_URL` (or the default in `lms/app/core/config.py`).

### Create a migration from model changes

Make sure Postgres is running and `DATABASE_URL` points to it.

```powershell
alembic revision --autogenerate -m "init"
```

### Apply migrations

```powershell
alembic upgrade head
```

## Background workers (Celery)

Celery is scaffolded (tasks are intentionally thin wrappers).

Start a worker (requires Redis and broker/backends configured):

```powershell
celery -A lms.app.workers.celery_app.celery_app worker -l info
```

## Notes

- This repo targets PostgreSQL types (e.g., `JSONB`, `INET`). SQLite is not supported for migrations/autogenerate.
- `requirements.txt` must stay UTF-8 (CI/CD and `pip -r` depend on it).
