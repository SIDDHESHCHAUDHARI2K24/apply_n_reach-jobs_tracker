# FastAPI Tutorial T2

This repository is a full-stack job-tracker application:

- `backend/`: FastAPI + PostgreSQL + Alembic + asyncpg + agent workflows
- `frontend/`: Next.js + React + TypeScript UI

It is designed to ingest job openings, extract content from source URLs, and tailor resume/email data through backend agent flows.

## How The Project Works

At runtime, the app has two services:

1. **Frontend (`frontend/`)**
   - Runs a Next.js app (default `http://localhost:3000`)
   - Calls the backend through `NEXT_PUBLIC_API_BASE_URL`
2. **Backend (`backend/`)**
   - Runs FastAPI (default `http://localhost:8000`)
   - Connects to PostgreSQL
   - Exposes APIs for auth, profile data, job tracking, opening ingestion, and agent runs

Typical flow:

1. User interacts with UI in `frontend/`
2. UI calls FastAPI endpoints
3. Backend stores/fetches data from PostgreSQL
4. For job opening ingestion, backend may queue background extraction work
5. Results are persisted and surfaced back through API to the frontend

## Prerequisites

Install these before setup:

- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js `20+` and npm
- PostgreSQL (local or remote)

## Initial Setup

### 1) Backend setup

```bash
cd backend
uv sync
```

Create `backend/.env` from `backend/.env.example` and set at least:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
APIFY_API_TOKEN=apify_api_...
```

Optional but recommended for agent/tracing features:

- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY` (fallback path when configured)
- `LANGCHAIN_API_KEY` (for LangSmith tracing)

Run database migrations:

```bash
uv run alembic upgrade head
```

### 2) Frontend setup

```bash
cd ../frontend
npm install
```

Create `frontend/.env.local` from `frontend/.env.example`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run The Project Locally

Use two terminals.

### Terminal A (backend)

```bash
cd backend
uv run uvicorn app.app:create_app --factory --reload --reload-dir app --loop asyncio
```

### Terminal B (frontend)

```bash
cd frontend
npm run dev
```

Then open `http://localhost:3000`.

## Docker Setup (Workers + Renderer)

This repo includes Docker support for background processing services:

- `worker`: runs `app.worker` for agent/extraction jobs
- `renderer`: runs the LaTeX PDF rendering server on port `8001`

The FastAPI API itself is currently intended to run locally via `uv run uvicorn ...` (not via `docker-compose`).

### Prerequisites

- Docker Desktop / Docker Engine with Compose enabled
- A running PostgreSQL instance on your host machine
- `backend/.env` configured (used by the `worker` container)

### 1) Build and start containers

From the repo root:

```bash
docker compose up --build -d
```

### 2) Check status and logs

```bash
docker compose ps
docker compose logs -f worker
docker compose logs -f renderer
```

### 3) Stop containers

```bash
docker compose down
```

### PostgreSQL host access notes

`docker-compose.yml` is configured to connect containers to your host PostgreSQL via `host.docker.internal`.

On local Postgres, ensure:

- `postgresql.conf` has `listen_addresses = '*'`
- `pg_hba.conf` allows Docker bridge ranges (example: `host all all 172.16.0.0/12 md5`)

Adjust the `DATABASE_URL` values in `docker-compose.yml`/`backend/.env` to match your environment.

## Development Commands

### Backend

```bash
cd backend
uv run python -m pytest
uv run alembic upgrade head
uv run alembic revision -m "new migration"
```

### Frontend

```bash
cd frontend
npm run lint
npm run test
npm run build
```

## API And Feature Areas

Major backend feature domains (see `backend/app/features/`):

- `auth`: session-based login/auth endpoints
- `user_profile`: personal profile sections (education, skills, projects, etc.)
- `job_profile`: generated/tailored profile slices and resume rendering helpers
- `job_tracker/openings_core`: job opening CRUD/status
- `job_tracker/opening_ingestion`: URL ingestion and extraction pipeline
- `job_tracker/opening_resume`: opening-specific resume sections + latex rendering
- `job_tracker/agents` and `job_tracker/email_agent`: agent execution and email generation

Useful endpoint for quick checks:

- `GET /health` returns `{"status":"ok"}`

## Notes

- Always run backend commands via `uv run ...` so dependencies match the project environment.
- If `pyproject.toml` changes, run `uv sync` again in `backend/`.
- If backend APIs change, regenerate frontend schema/types:

```bash
cd frontend
npm run openapi:generate
```
