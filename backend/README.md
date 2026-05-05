FastAPI Backend Boilerplate
===========================

This repository provides a reusable FastAPI backend boilerplate with:

- Async PostgreSQL access via `asyncpg`
- Environment-driven configuration using `pydantic-settings`
- Alembic migrations configured via `alembic.ini` and `alembic/env.py`
- A minimal auth feature demonstrating session-based login
- Pytest-based tests for configuration, database connectivity, and auth flows

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Ensure `.env` exists at `backend/.env` (you can start from `.env.example`) with at least:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Running the app

From the `backend/` directory:

```bash
uv run uvicorn app.app:create_app --factory --reload --loop asyncio
```

Use `uv run` so the interpreter matches this project’s synced dependencies (LangChain ingestion, agents, tracing). Running uvicorn against another clone’s `.venv` (missing `langchain-core`) will raise import errors at startup or during extraction. Resume agent runs also depend on `langgraph`, so run `uv sync` in this directory before starting the server.

After dependency changes (for example edits to `pyproject.toml`), run `uv sync` from this directory first.

## Running tests

```bash
uv run python -m pytest
```

## Job tracker extraction behavior

- Creating an opening with `source_url` via `POST /job-openings` now auto-queues background extraction.
- Extraction is best-effort and does not block the `201` create response.
- Manual re-runs remain available with `POST /job-openings/{opening_id}/extraction/refresh`.
- LangSmith tracing: set `LANGCHAIN_API_KEY` in `.env` to send traces for extraction and other LangChain flows. Runs appear under project `ETB_Project`; filter by run name `job_opening_extraction` or tags `opening_ingestion`, `extraction`.

## Running migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a new revision (once models/metadata are in place):

```bash
uv run alembic revision -m "add users and sessions tables"
```

The Alembic configuration lives in `alembic/` with an `alembic.ini`
file at the backend root.

## Using this as a template for a new project

You can treat this backend as a starting point for new services.

### Option 1: Manual clone

1. Create a new empty repository on your Git hosting provider.
2. Locally, clone this boilerplate:

   ```bash
   git clone <this-boilerplate-repo-url> my-new-backend
   cd my-new-backend
   ```

3. Remove the existing Git history and re-init:

   ```bash
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit from FastAPI backend boilerplate"
   git remote add origin <your-new-repo-url>
   git push -u origin main
   ```

### Option 2: Scaffold script

From the `backend/` directory of this boilerplate (with `uv` installed):

```bash
uv run python scripts/scaffold_new_project.py
```

The script will prompt you for a target directory and project name, copy the
backend tree there, remove any `.git` metadata, and update the README title.

Then:

1. `cd` into the new project directory.
2. Initialize Git and set your remote.
3. Create your `.env` from `.env.example` and update `DATABASE_URL`.

## Project structure

At a high level:

- `app/app.py` – FastAPI application factory and core wiring.
- `app/features/core` – configuration, database helpers, and shared dependencies.
- `app/features/auth` – example auth feature with endpoints, schemas, and SQL helpers.
- `alembic/` – Alembic migration environment and scripts.
- `tests` (under `app/features/*/tests`) – pytest-based tests for core and auth.
- `.env.example` – example environment configuration.
- `Makefile` – convenience commands for dev, tests, and migrations.
