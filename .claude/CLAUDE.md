# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run development server
make dev
# or: uv run uvicorn app.app:create_app --factory --reload --loop asyncio

# Run all tests
make test
# or: uv run python -m pytest

# Run tests for a specific feature
uv run python -m pytest app/features/auth/tests -q
uv run python -m pytest app/features/core/tests -q

# Run a single test file
uv run python -m pytest app/features/auth/tests/test_auth_endpoints.py -q

# Apply database migrations
make migrate
# or: uv run alembic upgrade head

# Create a new migration
make revision
# or: uv run alembic revision -m "description"
```

## Architecture

The project uses a **feature-based vertical slice architecture** under `app/features/`. Each feature is self-contained with its own models, schemas, endpoints, and tests.

```
app/features/
├── core/       # Infrastructure: config, database, dependencies, base schemas
└── auth/       # Domain feature: registration, login, logout, password reset, /me
```

**Adding a new feature** means creating a new directory under `app/features/` with the same structure (`models.py`, `schemas.py`, `routers.py`, `endpoints/`, `tests/`) and registering the router in `app/app.py`.

The `user_profile` feature (merged 2026-03-29) is the reference implementation for a full multi-section feature. See `app/features/user_profile/` for patterns.

### Key conventions

- **Database**: Raw SQL via AsyncPG (no ORM). Each feature's `models.py` contains SQL string constants and async functions for queries. Tables are created lazily via `ensure_*_schema()` called at request time — Alembic migrations are the intended long-term approach.
- **Dependency injection**: `DbDep` and `SettingsDep` from `app/features/core/dependencies.py` are injected into route handlers via FastAPI's `Depends()`.
- **Authentication**: Session-based with HttpOnly cookies. `get_current_user()` in `app/features/auth/utils.py` is the auth dependency. It reads `request.cookies.get("session_id")` and returns an `asyncpg.Record`. Use `app.dependency_overrides[get_current_user]` in tests.
- **Schemas**: Pydantic v2. Extend `BaseSchema` (has `from_attributes=True`) or `TimestampedSchema` from `app/features/core/base_model.py`.
- **Configuration**: All settings loaded from `.env` via `app/features/core/config.py`. Use the `settings` singleton or inject `SettingsDep`.
- **Sanitization**: Use `sanitize_text()` from `app/features/user_profile/validators.py` on ALL string inputs including URL fields — not just free-text.
- **Error responses**: All `HTTPException` and `RequestValidationError` responses return `{"detail": "...", "code": N}` via handlers registered in `app/app.py`.

### JSONB columns (asyncpg quirk)

When inserting/updating JSONB columns, pass `json.dumps(value)` with a `::jsonb` SQL cast. asyncpg returns the JSONB field as a **raw JSON string** in RETURNING clauses — call `json.loads()` before constructing the response. Plain `SELECT` queries return JSONB as Python list/dict natively.

```python
# INSERT with JSONB
await conn.fetchrow(
    "INSERT INTO table (..., tags) VALUES (..., $1::jsonb) RETURNING ...",
    json.dumps(data.tags),
)
# Response: row["tags"] may be a string — call json.loads() if needed
```

### Alembic migrations

Write migrations with raw DDL via `op.execute()` — no autogenerate from ORM models (there is no ORM). Use `DROP TABLE IF EXISTS parent CASCADE` in downgrade functions to handle FK children safely.

### Test conventions

- Use real DB with unique data (uuid4) per test — no mocking or rollback tricks.
- Each sub-feature test directory needs its **own** `conftest.py` (pytest doesn't traverse siblings).
- Insert test users via `asyncio.run(async_fn())` inside sync fixtures.
- Always clear `app.dependency_overrides` after each fixture yields.
- Test status codes explicitly (e.g., assert `201` on POST, not just the body).

### Request flow

```
HTTP Request → FastAPI router → endpoint function
                                    ↓
                           DbDep (asyncpg connection)
                           SettingsDep (settings)
                                    ↓
                           models.py (raw SQL queries)
                           utils.py (hashing, token generation)
                                    ↓
                           Pydantic schema response
```

## Environment

Copy `.env.example` to `.env`. Required variable: `DATABASE_URL` (PostgreSQL connection string). The app uses `asyncpg` so the URL must use the `postgresql://` scheme (not `postgresql+asyncpg://`).

## Registered API routes (as of 2026-03-29)

| Prefix | Feature | File |
|--------|---------|------|
| `/auth` | Auth (register, login, logout, reset, me) | `auth/routers.py` |
| `/profile` | Profile bootstrap + personal details | `user_profile/personal/router.py` |
| `/profile/education` | Education CRUD | `user_profile/education/router.py` |
| `/profile/experience` | Experience CRUD | `user_profile/experience/router.py` |
| `/profile/projects` | Projects CRUD | `user_profile/projects/router.py` |
| `/profile/research` | Research CRUD | `user_profile/research/router.py` |
| `/profile/certifications` | Certifications CRUD | `user_profile/certifications/router.py` |
| `/profile/skills` | Skills (full-replace PATCH) | `user_profile/skills/router.py` |

## Agent workflow notes

When using subagent-driven development on this project:
- **Do NOT use `run_in_background=true`** for agents that need Bash or Write access — they lose those permissions.
- **Parallel agents must not touch `app/app.py`** — have each agent skip router registration and do all registrations in one pass from the main context afterward.
- Copy `app/features/user_profile/tests/conftest.py` as the base for any new feature's test fixtures.
