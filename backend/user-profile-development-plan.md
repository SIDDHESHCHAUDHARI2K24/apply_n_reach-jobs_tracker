# Development Plan: User Profile Feature
## apply_n_reach — Jobs Tracker Backend

---

## Executive Summary

This plan covers the full backend implementation of the Unified User Profile System — a CRUD-based master profile feature for the apply_n_reach jobs tracker. The profile stores a user's professional identity across 7 modular sections (Personal Details, Education, Experience, Projects, Research, Skills, Certifications) and serves as the data source for future resume and job profile sub-profile generation.

- **Total Phases**: 3
- **Estimated Total Effort**: 10–15 days (solo developer)
- **Stack**: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pytest, bleach, session-based auth

**Top 3 Risks:**
1. **Alembic JSONB type detection** — auto-generate may render JSONB columns (e.g. `bullet_points`, `reference_links`) as `sa.JSON` instead of `postgresql.JSONB`. Always manually review migration files before committing. Mitigation: add a post-generate review checklist item to every Alembic task.
2. **Transaction rollback test isolation** — SQLAlchemy SAVEPOINT-based rollback requires careful session scoping in conftest. If the session is not properly nested, tests can pollute each other. Mitigation: validate the conftest fixture with a canary test (P1.T4.S3) before writing any feature tests.
3. **Session auth key name mismatch** — the `get_current_user` dependency assumes a specific key in `request.session`. If the existing auth stores the user ID under a different key, all endpoints break silently. Mitigation: explicitly verify the session key name against existing auth code in P1.T2.S1.

---

## API surface (read paths)

The API does **not** expose a monolithic `GET /profile` that returns the entire profile. Clients fetch **one section at a time** via dedicated routes.

**Collection (per section)**

- `GET /profile/personal`
- `GET /profile/education`
- `GET /profile/experience`
- `GET /profile/projects`
- `GET /profile/research`
- `GET /profile/skills`
- `GET /profile/certifications`

**Single item (by id)**

- `GET /profile/education/{id}`
- `GET /profile/experience/{id}`
- `GET /profile/projects/{id}`
- `GET /profile/research/{id}`
- `GET /profile/certifications/{id}`
- `GET /profile/skills/{id}`

**Bootstrap** (master record only): `POST /profile` creates the `UserProfile` row; it does not return nested sections. Personal details are read via `GET /profile/personal` and updated via `PATCH /profile/personal`.

---

## Phase Overview

| Phase | Name | Focus | Key Deliverables | Estimated Effort | Depends On |
|-------|------|--------|-----------------|-----------------|------------|
| P1 | Foundation | Infrastructure, auth wiring, sanitization, test fixtures, error schema | DB models (sub-feature layout + barrel), migrations, dependencies.py, validators.py, conftest.py, error envelope | 3–4 days | Existing auth system |
| P2 | Core Profile | Profile initialization + Personal Details | `POST /profile`, `GET /profile/personal`, `PATCH /profile/personal` + full test coverage | 2–3 days | P1 complete |
| P3 | Profile Sections | All 6 remaining sections (Education, Experience, Projects, Research, Skills, Certifications) | Per-section GET (collection + by id), POST/PATCH/DELETE + tests for each | 5–8 days | P2 complete |

---

## Phase 1: Foundation

### Overview
- **Goal**: Build everything that every other task depends on. No feature code ships in this phase — only infrastructure. This phase must be 100% complete before P2 starts.
- **Features addressed**: F1, F10, F11, F12, F13
- **Entry criteria**: Existing FastAPI app runs, auth system is operational, Alembic is initialised (`alembic/` directory exists)
- **Exit criteria**: DB tables exist in dev DB, `get_current_user` returns a user from session, `sanitize_text()` strips HTML correctly, `conftest.py` rollback fixture passes canary test, `ErrorResponse` schema is registered in `main.py`

---

### Task P1.T1: Database Models & Alembic Migrations

**Feature**: F1 — DB Models & Migrations  
**Effort**: M / 1 day  
**Dependencies**: None  
**Risk Level**: Medium (JSONB type detection risk — see Executive Summary)

#### Sub-task P1.T1.S1: Define SQLAlchemy ORM models for all profile tables

**Description**: Create the SQLAlchemy declarative models for all tables in the user profile feature. The models must define all columns, types, constraints, relationships, and cascade delete rules. **Organize ORM classes by sub-feature** (see [File Structure Reference](#file-structure-reference)): each of `personal/`, `education/`, `experience/`, `projects/`, `research/`, `skills/`, `certifications/` contains its own `models.py`; `UserProfile` lives in `personal/models.py` (or a dedicated `core` module if you prefer—document the choice). Provide a **barrel** module `user_profile/models/__init__.py` that imports every sub-feature model so Alembic and the app see one `Base.metadata`. Getting the schema right is critical — every subsequent task depends on it.

**Implementation Hints**:
- Import `Base` from the shared `backend/app/database.py` (match the pattern used by existing models)
- Models to define (split across files as above):
  - `UserProfile` — columns: `id` (PK), `user_id` (FK → users.id, unique, not null), `created_at`, `updated_at`. **Do not** store skills as JSONB on this row; skills are normalized (see `SkillItem`).
  - `PersonalDetails` — columns: `id`, `profile_id` (FK → user_profiles.id, unique), `full_name`, `email`, `linkedin_url`, `github_url` (nullable), `portfolio_url` (nullable)
  - `SkillItem` — columns: `id` (PK), `profile_id` (FK → user_profiles.id), `kind` (e.g. enum or string: `technical` | `competency`), `name` (str, sanitized), `sort_order` (int, optional). Table name e.g. `skill_items`. Enables `GET /profile/skills`, `GET /profile/skills/{id}`, and PATCH flows that sync rows.
  - `Education` — columns: `id`, `profile_id` (FK), `university_name`, `major`, `degree_type`, `start_month_year`, `end_month_year` (nullable = ongoing), `bullet_points` (JSONB, default `[]`), `reference_links` (JSONB, default `[]`)
  - `Experience` — columns: `id`, `profile_id` (FK), `role_title`, `company_name`, `start_month_year`, `end_month_year` (nullable), `context` (Text, large field), `work_sample_links` (JSONB, default `[]`), `bullet_points` (JSONB, default `[]`)
  - `Project` — columns: `id`, `profile_id` (FK), `project_name`, `description` (Text), `start_month_year`, `end_month_year` (nullable), `reference_links` (JSONB, default `[]`)
  - `Research` — columns: `id`, `profile_id` (FK), `paper_name`, `publication_link`, `description` (Text, nullable)
  - `Certification` — columns: `id`, `profile_id` (FK), `certification_name`, `verification_link`
- Use `from sqlalchemy.dialects.postgresql import JSONB` — not `sa.JSON` where JSONB is used
- On `UserProfile`: set `relationship(..., cascade="all, delete-orphan")` for each child collection (`educations`, `skill_items`, etc.)
- On all child models: `relationship("UserProfile", back_populates=...)`
- Add `__tablename__` strings using snake_case: `user_profiles`, `personal_details`, `skill_items`, `educations`, `experiences`, `projects`, `researches`, `certifications`
- Add `updated_at` with `onupdate=func.now()` on `UserProfile` and list-section tables as applicable

**Dependencies**: None  
**Effort**: M / 4–6 hours  
**Risk Flags**: Ensure `JSONB` import is from `sqlalchemy.dialects.postgresql`, not `sqlalchemy`. Using generic `JSON` will work but loses PostgreSQL-specific indexing capabilities and Alembic will generate the wrong column type.  
**Acceptance Criteria**:
- All ORM models are defined with correct column types and nullability
- All FK relationships include `cascade="all, delete-orphan"` on the parent side where required
- `JSONB` columns are imported from `sqlalchemy.dialects.postgresql`
- Importing the barrel succeeds: `python -c "from app.features.user_profile.models import UserProfile"` (adjust to your package layout)

---

#### Sub-task P1.T1.S2: Register models in Alembic env.py target metadata

**Description**: Alembic's `--autogenerate` only detects models that are imported into `env.py`'s `target_metadata`. If the new profile models are not registered here, Alembic will generate an empty migration and the tables will never be created.

**Implementation Hints**:
- File: `alembic/env.py`
- Find the line that sets `target_metadata` — it likely looks like `target_metadata = Base.metadata` or imports from a specific models file
- Add an import that loads **all** profile ORM classes into metadata: e.g. `from app.features.user_profile.models import *` or import the barrel package `from app.features.user_profile import models as user_profile_models` — the import side effect must register every table (personal, education, …, `skill_items`) with the shared `Base.metadata`
- If other features have their own `Base`, check whether the project uses a single shared `Base` (preferred) or multiple. If multiple, `target_metadata` must be a list: `target_metadata = [Base.metadata, OtherBase.metadata]`
- Verify by running `alembic check` — it should report pending changes for the new tables

**Dependencies**: P1.T1.S1  
**Effort**: XS / 30 minutes  
**Risk Flags**: If the project accidentally uses two different `Base` instances (one for existing models, one defined in the new feature), Alembic won't see either set completely. Confirm that `models.py` imports `Base` from the same location as all other models.  
**Acceptance Criteria**:
- `alembic check` reports "New table: user_profiles" (and other tables) as pending
- No import errors when running `alembic check`

---

#### Sub-task P1.T1.S3: Generate, review, and apply Alembic migrations

**Description**: Generate two migration files for the profile tables (base tables first, section tables second), review both for correctness, then apply to the dev database. Two separate migrations allow easier rollback if the section tables have issues without losing the core profile table.

**Implementation Hints**:
- Run: `alembic revision --autogenerate -m "add_user_profile_base"` — then immediately open the generated file and verify:
  - `user_profiles` table is created (no JSONB skill blobs on this table if skills are normalized)
  - `personal_details` table is created with a `UNIQUE` constraint on `profile_id`
  - FK from `user_profiles.user_id` to `users.id` is present
- Then run: `alembic revision --autogenerate -m "add_user_profile_sections"` — verify:
  - All section tables: `skill_items`, `educations`, `experiences`, `projects`, `researches`, `certifications`
  - Each has a FK to `user_profiles.id` with `ON DELETE CASCADE`
  - JSONB columns on list-section tables render as `postgresql.JSONB`
- Common Alembic auto-generate issues to fix manually:
  - `sa.JSON` → `postgresql.JSONB` (add `from sqlalchemy.dialects import postgresql` to migration imports)
  - Missing `unique=True` on `personal_details.profile_id` — add manually if absent
  - Missing `onupdate` on `updated_at` — acceptable to leave in migration, handled at ORM level
- Apply: `alembic upgrade head`
- Verify tables exist: connect to dev DB and run `\dt` in psql

**Dependencies**: P1.T1.S2  
**Effort**: S / 2 hours  
**Risk Flags**: Never run `alembic upgrade head` without reviewing the generated migration file first. A bad auto-generated migration can drop existing tables if Alembic misdetects a rename as drop+create.  
**Acceptance Criteria**:
- Both migration files exist in `alembic/versions/`
- `alembic upgrade head` runs without errors
- All profile tables exist in the dev PostgreSQL database (including `skill_items`)
- `alembic downgrade -1` rolls back cleanly (test this before committing)

---

### Task P1.T2: Auth Dependencies & Ownership Validation

**Feature**: F10 — Auth Dependencies  
**Effort**: S / 2–3 hours  
**Dependencies**: P1.T1.S1  
**Risk Level**: Medium (session key name must match existing auth)

#### Sub-task P1.T2.S1: Create get_current_user dependency

**Description**: Create a FastAPI dependency that extracts the authenticated user from the session and returns the `User` ORM object (or raises `401` if not authenticated). This dependency is injected into every profile endpoint. It must use the same session key that the existing auth feature writes when a user logs in.

**Implementation Hints**:
- File: `backend/app/features/user_profile/dependencies.py`
- Before writing: check the existing auth feature's login endpoint to find the exact session key used (e.g. `request.session["user_id"]` or `request.session["id"]` — do not guess)
- Pattern:
  ```python
  from fastapi import Depends, HTTPException, Request
  from sqlalchemy.orm import Session
  from app.database import get_db
  from app.features.auth.models import User  # adjust import path

  def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
      user_id = request.session.get("user_id")  # confirm key name
      if not user_id:
          raise HTTPException(status_code=401, detail="Not authenticated")
      user = db.get(User, user_id)
      if not user:
          raise HTTPException(status_code=401, detail="User not found")
      return user
  ```
- This dependency will be composed into `get_profile_or_404` in the next sub-task

**Dependencies**: P1.T1.S1  
**Effort**: S / 1–2 hours  
**Risk Flags**: Session key name mismatch is the #1 risk here. Spend 5 minutes finding the exact key in the existing auth code rather than guessing.  
**Acceptance Criteria**:
- A request with a valid session returns the `User` ORM object
- A request with no session raises `HTTP 401`
- A request with an invalid/expired session user_id raises `HTTP 401`
- Unit test: mock `request.session` with valid and invalid values, verify correct return/exception

---

#### Sub-task P1.T2.S2: Create get_profile_or_404 dependency

**Description**: Create a dependency that, given a valid authenticated user, fetches their `UserProfile` record. Raises `404` if the profile doesn't exist (i.e. user has not called `POST /profile` yet). This dependency is injected into all section endpoints (Education, Experience, etc.) to prevent section creation without a parent profile.

**Implementation Hints**:
- File: `backend/app/features/user_profile/dependencies.py` (same file as above)
- Pattern:
  ```python
  from app.features.user_profile.models import UserProfile  # adjust import to barrel path

  def get_profile_or_404(
      current_user: User = Depends(get_current_user),
      db: Session = Depends(get_db)
  ) -> UserProfile:
      profile = db.query(UserProfile).filter(
          UserProfile.user_id == current_user.id
      ).first()
      if not profile:
          raise HTTPException(
              status_code=404,
              detail="Profile not found. Create a profile first via POST /profile"
          )
      return profile
  ```
- The `detail` message is intentionally descriptive — it guides API consumers who hit this before creating a profile

**Dependencies**: P1.T2.S1  
**Effort**: XS / 1 hour  
**Acceptance Criteria**:
- Returns `UserProfile` object when profile exists for the current user
- Raises `HTTP 404` with descriptive message when no profile exists
- Raises `HTTP 401` (via `get_current_user`) when user is not authenticated

---

### Task P1.T3: Input Sanitization Layer

**Feature**: F11 — Input Sanitization  
**Effort**: S / 2–3 hours  
**Dependencies**: None  
**Risk Level**: Low

#### Sub-task P1.T3.S1: Implement sanitize_text helper using bleach

**Description**: Create a reusable `sanitize_text()` helper function using `bleach` that strips all HTML tags and dangerous attributes from text input. This function will be called from Pydantic `field_validator` decorators in all request schemas. It must handle `None` values gracefully (for optional fields) and enforce per-call maximum length.

**Implementation Hints**:
- Install: add `bleach>=6.0.0` to `requirements.txt`
- File: `backend/app/features/user_profile/validators.py`
- Pattern:
  ```python
  import bleach
  from typing import Optional

  def sanitize_text(value: Optional[str], max_length: int = 5000) -> Optional[str]:
      if value is None:
          return None
      cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)
      cleaned = cleaned.strip()
      if len(cleaned) > max_length:
          raise ValueError(f"Field exceeds maximum length of {max_length} characters")
      return cleaned
  ```
- `tags=[]` strips ALL HTML tags (no allowlist). `strip=True` removes the tags entirely rather than escaping them.
- Max lengths by field type (enforce in schemas via `max_length` kwarg): short text (names, titles) = 255, medium text (descriptions) = 1000, large text (experience context) = 10000, URLs = 2048
- In Pydantic schemas, use as: `@field_validator("field_name", mode="before") def clean_field(cls, v): return sanitize_text(v, max_length=255)`

**Dependencies**: None  
**Effort**: S / 2 hours  
**Acceptance Criteria**:
- `sanitize_text("<script>alert('xss')</script>Hello")` returns `"Hello"`
- `sanitize_text("<b>Bold text</b>")` returns `"Bold text"`
- `sanitize_text(None)` returns `None` without raising
- `sanitize_text("a" * 6000, max_length=5000)` raises `ValueError`
- Unit tests for all four cases above pass

---

### Task P1.T4: Pytest Infrastructure

**Feature**: F12 — Pytest Infrastructure  
**Effort**: M / 4–6 hours  
**Dependencies**: P1.T1.S3 (tables must exist in DB)  
**Risk Level**: Medium (SAVEPOINT isolation requires careful session scoping)

#### Sub-task P1.T4.S1: Create conftest.py with DB session and rollback fixture

**Description**: Create the test configuration that provides a database session wrapped in a SAVEPOINT transaction that rolls back after each test. This ensures tests never pollute the dev database. Every test in the user profile feature will use the `db_session` fixture from this file.

**Implementation Hints**:
- File: `backend/app/features/user_profile/tests/conftest.py`
- Pattern:
  ```python
  import pytest
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from app.database import Base, DATABASE_URL  # adjust to your actual import

  engine = create_engine(DATABASE_URL)
  TestingSessionLocal = sessionmaker(bind=engine)

  @pytest.fixture(scope="function")
  def db_session():
      connection = engine.connect()
      transaction = connection.begin()
      session = TestingSessionLocal(bind=connection)
      # Create a savepoint so we can roll back to it after the test
      nested = connection.begin_nested()

      yield session

      session.close()
      # Roll back to before the test ran
      if nested.is_active:
          nested.rollback()
      transaction.rollback()
      connection.close()
  ```
- `scope="function"` is critical — each test gets a fresh rollback. Do not use `scope="session"` here.
- The `DATABASE_URL` must point to your actual dev DB — confirm the import path matches your project structure

**Dependencies**: P1.T1.S3  
**Effort**: M / 2–3 hours  
**Risk Flags**: If `connection.begin_nested()` (SAVEPOINT) is not supported, the rollback won't work correctly. PostgreSQL fully supports SAVEPOINTs. Verify the DB URL is PostgreSQL, not SQLite (SQLite SAVEPOINT support is limited).  
**Acceptance Criteria**:
- `db_session` fixture yields a valid SQLAlchemy `Session`
- Data written during a test does not appear in the DB after the test completes (verify manually)
- Fixture works with `scope="function"` across multiple test functions in the same file

---

#### Sub-task P1.T4.S2: Create mock_session fixture for auth injection

**Description**: Create a fixture that injects a fake authenticated user into FastAPI's test client `Request.session`, so endpoints that call `get_current_user` receive a valid user without going through the real login flow. Also create a `test_client` fixture that mounts the profile router with this session override.

**Implementation Hints**:
- File: `backend/app/features/user_profile/tests/conftest.py` (same file)
- Pattern:
  ```python
  from fastapi.testclient import TestClient
  from app.main import app
  from app.features.user_profile.dependencies import get_current_user
  from app.features.auth.models import User  # adjust

  @pytest.fixture
  def test_user(db_session):
      user = User(id=1, email="test@example.com")  # minimal user object
      db_session.add(user)
      db_session.flush()
      return user

  @pytest.fixture
  def authenticated_client(test_user):
      def override_get_current_user():
          return test_user
      app.dependency_overrides[get_current_user] = override_get_current_user
      client = TestClient(app)
      yield client
      app.dependency_overrides.clear()
  ```
- `dependency_overrides` is FastAPI's built-in mechanism for replacing dependencies in tests — cleaner than mocking
- Always call `app.dependency_overrides.clear()` in teardown to prevent fixture leakage between test files

**Dependencies**: P1.T4.S1, P1.T2.S1  
**Effort**: S / 1–2 hours  
**Acceptance Criteria**:
- `authenticated_client` makes requests that pass `get_current_user` without a real session
- `unauthenticated_client` (without override) returns `401` on protected endpoints
- Dependency overrides are cleared after each test (no cross-test contamination)

---

#### Sub-task P1.T4.S3: Write canary test to validate fixture correctness

**Description**: Write a single "canary" test that validates the rollback isolation is working correctly before any feature tests are written. If this test fails, the conftest fixtures are broken and no subsequent tests can be trusted. This test intentionally writes data and verifies it's gone after the test.

**Implementation Hints**:
- File: `backend/app/features/user_profile/tests/test_fixtures_canary.py`
- Test 1: Write a `UserProfile` row inside `db_session`, commit, then in a second DB connection (outside the fixture), verify the row does NOT exist. This confirms rollback is working.
- Test 2: Make a request to a protected endpoint without auth using a plain `TestClient(app)` — verify `401` is returned. This confirms `get_current_user` enforces auth.
- Test 3: After the profile router exists, make a request using `authenticated_client` (e.g. `POST /profile` or `GET /profile/personal`) — verify a defined status (`201`, `404`, etc.), not `401`. Confirms the dependency override works.

**Dependencies**: P1.T4.S1, P1.T4.S2  
**Effort**: S / 1–2 hours  
**Acceptance Criteria**:
- All 3 canary tests pass with `pytest -v`
- Canary test file can be deleted or kept — its purpose is to validate the infrastructure before feature tests are written

---

### Task P1.T5: Error Response Standardisation

**Feature**: F13 — Error Response Schema  
**Effort**: XS / 1 hour  
**Dependencies**: None  
**Risk Level**: Low

#### Sub-task P1.T5.S1: Define ErrorResponse schema and register exception handler

**Description**: Define a consistent error response envelope and register a custom exception handler in `main.py` so all `HTTPException` errors return the same JSON shape. This ensures API consumers always know what structure to expect from errors.

**Implementation Hints**:
- File: `backend/app/core/errors.py` (create `core/` directory if it doesn't exist; this is shared across all features)
- Schema:
  ```python
  from pydantic import BaseModel

  class ErrorResponse(BaseModel):
      detail: str
      code: int
  ```
- In `main.py`, register the handler:
  ```python
  from fastapi import Request
  from fastapi.responses import JSONResponse
  from fastapi.exceptions import HTTPException

  @app.exception_handler(HTTPException)
  async def http_exception_handler(request: Request, exc: HTTPException):
      return JSONResponse(
          status_code=exc.status_code,
          content={"detail": exc.detail, "code": exc.status_code}
      )
  ```
- Also add a handler for `RequestValidationError` (Pydantic 422 errors) to normalise those to the same shape if desired

**Dependencies**: None  
**Effort**: XS / 1 hour  
**Acceptance Criteria**:
- All `HTTPException` responses return `{"detail": "...", "code": N}` JSON shape
- `422` validation errors from Pydantic are also normalised
- Existing endpoints (if any) are not broken by the new handler

---

## Phase 2: Core Profile

### Overview
- **Goal**: Implement the master profile record (the root of the 1:1 relationship) and Personal Details. These are the two endpoints every other section depends on conceptually.
- **Features addressed**: F2 (Core Profile Init), F3 (Personal Details)
- **Entry criteria**: All Phase 1 tasks complete and passing
- **Exit criteria**: `POST /profile`, `GET /profile/personal`, `PATCH /profile/personal`, and related tests work, are authenticated, ownership-validated, and have full test coverage

---

### Task P2.T1: Core Profile Schemas

**Feature**: F2  
**Effort**: S / 2 hours  
**Dependencies**: P1.T1.S1, P1.T3.S1  
**Risk Level**: Low

#### Sub-task P2.T1.S1: Define Pydantic schemas for UserProfile and PersonalDetails

**Description**: Create request and response Pydantic schemas for profile bootstrap and **Personal Details only**. Sections are loaded via separate endpoints — do **not** define a mega-response that embeds every section. Schemas enforce validation, apply sanitization via `field_validator`, and define the response shape. Separate `Create`, `Update`, and `Response` schemas following the FastAPI convention.

**Implementation Hints**:
- File: `backend/app/features/user_profile/personal/schemas.py` (or `schemas.py` under the personal sub-feature per directory layout)
- For **profile creation** (minimal response):
  ```python
  class UserProfileCreatedResponse(BaseModel):
      id: int
      user_id: int
      created_at: datetime
      # no nested sections

      class Config:
          from_attributes = True
  ```
- For `PersonalDetails`:
  ```python
  class PersonalDetailsCreate(BaseModel):
      full_name: str = Field(..., max_length=255)
      email: EmailStr
      linkedin_url: HttpUrl
      github_url: Optional[HttpUrl] = None
      portfolio_url: Optional[HttpUrl] = None

      @field_validator("full_name", mode="before")
      def sanitize_name(cls, v):
          return sanitize_text(v, max_length=255)
  ```
  ```python
  class PersonalDetailsResponse(BaseModel):
      id: int
      profile_id: int
      full_name: str
      email: EmailStr
      # ... mirror ORM

      class Config:
          from_attributes = True
  ```
- Use `from pydantic import EmailStr, HttpUrl, Field, field_validator`
- List-section response types (`EducationResponse`, etc.) are defined in their respective sub-features in P3 — not in P2

**Dependencies**: P1.T1.S1, P1.T3.S1  
**Effort**: S / 2 hours  
**Acceptance Criteria**:
- `PersonalDetailsCreate` with invalid email raises `ValidationError`
- `PersonalDetailsCreate` with non-HTTP URL raises `ValidationError`
- `PersonalDetailsCreate` with HTML in `full_name` sanitizes it before storage
- `UserProfileCreatedResponse` and `PersonalDetailsResponse` serialize correctly from ORM objects

---

### Task P2.T2: Core Profile Service & Router

**Feature**: F2, F3  
**Effort**: M / 4–6 hours  
**Dependencies**: P2.T1.S1, P1.T2.S2, P1.T5.S1  
**Risk Level**: Low

#### Sub-task P2.T2.S1: Implement profile service layer

**Description**: Create the service layer for **creating** the master profile and **reading/updating Personal Details only**. Business logic (ownership checks, existence checks) lives here — not in the router. Do **not** implement a single query that loads every section.

**Implementation Hints**:
- File: `backend/app/features/user_profile/personal/service.py` (split files per sub-feature as needed)
- Functions to implement:
  ```python
  def create_profile(db: Session, user_id: int) -> UserProfile
  def get_personal_details(db: Session, profile_id: int) -> PersonalDetails | None
  def upsert_personal_details(db: Session, profile_id: int, data: PersonalDetailsCreate) -> PersonalDetails
  ```
- `create_profile`: check if a profile already exists for `user_id` — if so, raise `HTTPException(409, "Profile already exists")`. Otherwise create and return.
- `get_personal_details`: load `PersonalDetails` for `profile_id` (optional `joinedload` from profile if useful). Return `None` if no row exists yet — router maps that to `404` or empty payload per API contract (prefer **404** for missing personal block if that is the chosen behavior, or **200** with null body — document one choice in the personal sub-feature `features.md`).
- `upsert_personal_details`: check if a `PersonalDetails` record exists for this `profile_id`. If yes, update. If no, create.

**Dependencies**: P2.T1.S1  
**Effort**: M / 3–4 hours  
**Acceptance Criteria**:
- `create_profile` called twice for the same user raises `409`
- `get_personal_details` does not load unrelated sections (education, experience, etc.)
- `upsert_personal_details` creates on first call, updates on subsequent calls

---

#### Sub-task P2.T2.S2: Implement profile router

**Description**: Create the FastAPI `APIRouter` for **bootstrap + Personal Details**. Aggregate sub-routers under `/profile` in `main.py` (include a personal router with prefix `/profile` or mount sub-routers on a parent APIRouter). There is **no** `GET ""` on `/profile` that returns the full profile.

**Implementation Hints**:
- File: `backend/app/features/user_profile/personal/router.py` (included from feature root `user_profile/__init__.py` or a thin `user_profile/router.py` that `include_router`s all sub-routers)
- Endpoints:
  ```python
  router = APIRouter(prefix="/profile", tags=["user-profile"])

  @router.post("", response_model=UserProfileCreatedResponse, status_code=201)
  def create_profile(
      current_user: User = Depends(get_current_user),
      db: Session = Depends(get_db)
  ):
      return service.create_profile(db, current_user.id)

  @router.get("/personal", response_model=PersonalDetailsResponse)
  def get_personal(
      profile: UserProfile = Depends(get_profile_or_404),
      db: Session = Depends(get_db)
  ):
      row = service.get_personal_details(db, profile.id)
      if row is None:
          raise HTTPException(status_code=404, detail="Personal details not found")
      return row

  @router.patch("/personal", response_model=PersonalDetailsResponse)
  def update_personal_details(
      data: PersonalDetailsCreate,
      profile: UserProfile = Depends(get_profile_or_404),
      db: Session = Depends(get_db)
  ):
      return service.upsert_personal_details(db, profile.id, data)
  ```
- Register the aggregated router(s) in `main.py`

**Dependencies**: P2.T2.S1, P1.T2.S2  
**Effort**: S / 1–2 hours  
**Acceptance Criteria**:
- `POST /profile` returns `201` with a new profile (minimal body, no nested sections)
- `POST /profile` called twice returns `409`
- `GET /profile/personal` returns `404` when profile exists but personal details were never upserted (or match the documented contract in `features.md`)
- `GET /profile/personal` returns personal details when present
- `PATCH /profile/personal` upserts personal details correctly
- All endpoints return `401` without auth
- There is no `GET /profile` that returns the entire profile

---

### Task P2.T3: Core Profile Tests

**Feature**: F2, F3  
**Effort**: M / 4 hours  
**Dependencies**: P2.T2.S2, P1.T4.S2  
**Risk Level**: Low

#### Sub-task P2.T3.S1: Write tests for core profile and personal details endpoints

**Description**: Write the full test suite for `POST /profile`, `GET /profile/personal`, and `PATCH /profile/personal`. Cover happy paths, auth enforcement, duplicate creation, and not-found cases. These tests establish the pattern that all P3 test files will follow.

**Implementation Hints**:
- File: `backend/app/features/user_profile/personal/tests/test_profile_core.py` (or shared `user_profile/tests/test_profile_core.py` — align with chosen test layout)
- Test cases to cover:
  - `test_create_profile_success` — authenticated user, `201` returned, DB record exists
  - `test_create_profile_duplicate` — second call returns `409`
  - `test_create_profile_unauthenticated` — no session, `401` returned
  - `test_get_personal_profile_missing` — authenticated but no `UserProfile` yet, `404` on `GET /profile/personal` (via `get_profile_or_404`)
  - `test_get_personal_not_yet_upserted` — profile exists but no personal row, expect `404` (or documented alternative)
  - `test_get_personal_success` — after patch, returns personal details
  - `test_get_personal_unauthenticated` — `401`
  - `test_patch_personal_create` — first patch creates personal details
  - `test_patch_personal_update` — second patch updates same fields
  - `test_patch_personal_invalid_email` — `422` on bad email
  - `test_patch_personal_html_stripped` — verify `<script>` in name is sanitized
  - `test_ownership_isolation` — user B cannot read user A's personal section (create two users, two profiles, verify `404` or isolation)
- Use `authenticated_client` fixture from conftest for all auth tests
- The ownership test is the most important — do not skip it

**Dependencies**: P2.T2.S2, P1.T4.S2  
**Effort**: M / 3–4 hours  
**Acceptance Criteria**:
- All test cases listed above pass with `pytest -v`
- `test_ownership_isolation` explicitly verifies a different user's request returns `404`
- 0 test failures, 0 warnings about unclosed DB sessions

---

## Phase 3: Profile Sections

### Overview
- **Goal**: Implement all 6 remaining profile sections. Each section follows an identical pattern: schemas → service functions → router endpoints → tests. The fastest approach is to implement one section end-to-end first (Education), then use it as a template for the remaining five.
- **Features addressed**: F4–F9
- **Entry criteria**: Phase 2 complete and all tests passing
- **Exit criteria**: All 6 sections expose **GET (collection + by id)** where applicable, full mutating operations (POST/PATCH/DELETE or PATCH-only for skills per design), are tested, and are connected to the master profile

> **Implementation note**: Tasks P3.T1 through P3.T6 follow the same internal structure. Rather than repeating identical sub-task patterns six times, each task below specifies what is unique about that section. The implementation pattern from P3.T1 (Education) is the template for all subsequent sections.

---

### Task P3.T1: Education CRUD

**Feature**: F4  
**Effort**: M / 4–6 hours  
**Dependencies**: P2.T2.S2  
**Risk Level**: Low

#### Sub-task P3.T1.S1: Education schemas, service, router, and tests

**Description**: Implement full CRUD for the Education section following the established pattern. Education is the first list-section implementation and sets the template for all others. Particular attention to: date validation (`end_month_year` can be null for ongoing), `bullet_points` and `reference_links` as JSONB lists, and response ordering (most recent `start_month_year` first).

**Implementation Hints**:
- Schema file: `education/schemas.py` — `EducationCreate`, `EducationUpdate`, `EducationResponse`
  - `start_month_year` and `end_month_year`: use `str` with a regex validator enforcing `MM/YYYY` format: `@field_validator("start_month_year") def validate_date_format(cls, v): ...`
  - `end_month_year`: `Optional[str] = None` (null = currently studying)
  - Add a cross-field validator: if both dates are present, verify `end >= start` by parsing as `datetime(year, month, 1)`
  - `bullet_points`: `list[str] = []` — each item gets `sanitize_text(item, max_length=500)` in a list validator
  - `reference_links`: `list[HttpUrl] = []`
- Service functions in `education/service.py`:
  - `add_education(db, profile_id, data) -> Education`
  - `get_education(db, profile_id, education_id) -> Education | None` — ownership at item level
  - `update_education(db, profile_id, education_id, data) -> Education` — verify `education.profile_id == profile_id` before updating (ownership at item level)
  - `delete_education(db, profile_id, education_id) -> None` — same ownership check
  - `list_educations(db, profile_id) -> list[Education]` — order by `start_month_year DESC`
- Router endpoints: `GET /profile/education` (200 list), `GET /profile/education/{id}` (200), `POST /profile/education` (201), `PATCH /profile/education/{id}` (200), `DELETE /profile/education/{id}` (204)
- Optional: route handlers in `education/endpoints/` imported by `education/router.py`
- Test file: `education/tests/test_education.py`
  - Happy path create/update/delete; GET list and GET by id
  - `end_month_year` before `start_month_year` → `422`
  - Attempt to delete another user's education entry → `404`
  - HTML in `bullet_points` items is stripped

**Dependencies**: P2.T2.S2, P1.T3.S1  
**Effort**: M / 4–6 hours  
**Acceptance Criteria**:
- All mutating and GET endpoints return correct status codes and payloads
- Date validation correctly rejects `end < start`
- Deleting another user's education entry returns `404`, not `403` (do not reveal existence)
- All test cases pass; GET list and GET by id enforce ownership

---

### Task P3.T2: Professional Experience CRUD

**Feature**: F5  
**Effort**: L / 1–2 days  
**Dependencies**: P3.T1.S1  
**Risk Level**: Low-Medium (largest schema, large text field)

#### Sub-task P3.T2.S1: Experience schemas, service, router, and tests

**Description**: Implement full CRUD for the Professional Experience section. This is the most complex section due to the `context` large text field (up to 10,000 chars), `work_sample_links`, and `bullet_points`. The `context` field is the primary repository for detailed job responsibilities — sanitize carefully with a higher max length than other fields.

**Implementation Hints**:
- Follow the exact same pattern as P3.T1.S1 with these differences:
  - `context` field: `str` with `sanitize_text(v, max_length=10000)` — this is the free-text job description field
  - `role_title` and `company_name`: max_length=255, sanitized
  - `work_sample_links`: `list[HttpUrl] = []`
  - `bullet_points`: `list[str] = []`, each sanitized to max_length=500
  - Same date validation as Education (`MM/YYYY` format, end >= start)
- Endpoints: `GET /profile/experience`, `GET /profile/experience/{id}`, `POST /profile/experience`, `PATCH /profile/experience/{id}`, `DELETE /profile/experience/{id}`
- Test file: `experience/tests/test_experience.py`
  - Include a test with a very long `context` field (at the 10,000 char limit) — verify it saves correctly
  - Include a test with a `context` field over 10,000 chars — verify `422`
  - HTML stripping in `context` field

**Dependencies**: P3.T1.S1  
**Effort**: L / 1–1.5 days  
**Acceptance Criteria**:
- `context` field accepts up to 10,000 characters after sanitization
- `context` field with HTML tags has tags stripped before storage
- All other acceptance criteria same as Education section

---

### Task P3.T3: Projects CRUD

**Feature**: F6  
**Effort**: M / 3–4 hours  
**Dependencies**: P3.T1.S1  
**Risk Level**: Low

#### Sub-task P3.T3.S1: Projects schemas, service, router, and tests

**Description**: Implement full CRUD for the Projects section. Projects are structurally simpler than Experience — no `bullet_points`, just a `description` text field and `reference_links`. Follow the Education template exactly with these field differences.

**Implementation Hints**:
- Fields: `project_name` (str, max 255), `description` (Text, max 2000, sanitized), `start_month_year`, `end_month_year` (nullable), `reference_links` (list[HttpUrl])
- No `bullet_points` on this model
- Endpoints: `GET /profile/projects`, `GET /profile/projects/{id}`, `POST /profile/projects`, `PATCH /profile/projects/{id}`, `DELETE /profile/projects/{id}`
- Test file: `projects/tests/test_projects.py` — same test pattern as Education

**Dependencies**: P3.T1.S1  
**Effort**: M / 3–4 hours  
**Acceptance Criteria**:
- Same pattern as Education section
- `reference_links` rejects non-HTTP URLs

---

### Task P3.T4: Research CRUD

**Feature**: F7  
**Effort**: S / 2–3 hours  
**Dependencies**: P3.T1.S1  
**Risk Level**: Low

#### Sub-task P3.T4.S1: Research schemas, service, router, and tests

**Description**: Implement full CRUD for the Research section. This is the simplest list section — only 3 fields. No date fields. Primary validation concern is that `publication_link` is a valid URL.

**Implementation Hints**:
- Fields: `paper_name` (str, max 500, sanitized), `publication_link` (HttpUrl, required), `description` (Text, max 2000, nullable, sanitized)
- No date fields on this model
- Endpoints: `GET /profile/research`, `GET /profile/research/{id}`, `POST /profile/research`, `PATCH /profile/research/{id}`, `DELETE /profile/research/{id}`
- Test file: `research/tests/test_research.py`

**Dependencies**: P3.T1.S1  
**Effort**: S / 2–3 hours  
**Acceptance Criteria**:
- `publication_link` with invalid URL returns `422`
- `description` is optional — omitting it is valid

---

### Task P3.T5: Skills CRUD

**Feature**: F8  
**Effort**: M / 4–6 hours  
**Dependencies**: P2.T2.S2, P1.T1.S3 (migrations include `skill_items`)  
**Risk Level**: Medium (normalized model + sync semantics)

#### Sub-task P3.T5.S1: Skills schemas, service, router, and tests

**Description**: Implement Skills using **normalized** `SkillItem` rows (see P1.T1.S1). Skills support **GET collection**, **GET by id**, and a **PATCH** that replaces the full skill set for the profile (delete rows not present in the payload, upsert/update order as needed — document the exact algorithm in `skills/features.md`). Optional: `DELETE /profile/skills/{id}` for single-row delete if desired; minimum is PATCH + GETs per API surface.

**Implementation Hints**:
- Schemas in `skills/schemas.py`:
  - `SkillItemResponse`: `id`, `profile_id`, `kind`, `name`, `sort_order`, …
  - `SkillsUpdate`: body that lists desired technical and competency skills (e.g. two arrays) **or** a list of objects with `kind` + `name` — choose one shape and validate with `field_validator` + `sanitize_text(..., max_length=100)` per name
- Service in `skills/service.py`:
  - `list_skills(db, profile_id) -> list[SkillItem]`
  - `get_skill(db, profile_id, skill_id) -> SkillItem | None`
  - `replace_skills(db, profile_id, data: SkillsUpdate) -> list[SkillItem]` — transactional replace
- Router: `GET /profile/skills`, `GET /profile/skills/{id}`, `PATCH /profile/skills` (200) — `get_profile_or_404` for all
- Test file: `skills/tests/test_skills.py`
  - GET list empty and populated; GET by id 200 and 404 for wrong id / other user
  - PATCH replace semantics; clear all skills
  - HTML in a skill name is stripped; over max length → `422`

**Dependencies**: P2.T2.S2, P1.T3.S1  
**Effort**: M / 4–6 hours  
**Acceptance Criteria**:
- `GET /profile/skills` and `GET /profile/skills/{id}` behave correctly
- `PATCH /profile/skills` applies a consistent full-replace (or documented sync) strategy
- Individual skill names are sanitized and length-limited

---

### Task P3.T6: Certifications CRUD

**Feature**: F9  
**Effort**: S / 2–3 hours  
**Dependencies**: P3.T1.S1  
**Risk Level**: Low

#### Sub-task P3.T6.S1: Certifications schemas, service, router, and tests

**Description**: Implement full CRUD for the Certifications section. This is the simplest list section alongside Research — two required fields, no date or optional text fields. The `verification_link` must be a valid URL.

**Implementation Hints**:
- Fields: `certification_name` (str, max 255, sanitized), `verification_link` (HttpUrl, required)
- No date fields, no optional text fields
- Endpoints: `GET /profile/certifications`, `GET /profile/certifications/{id}`, `POST /profile/certifications`, `PATCH /profile/certifications/{id}`, `DELETE /profile/certifications/{id}`
- Test file: `certifications/tests/test_certifications.py`
- Follow Education template exactly — this is the fastest section to implement

**Dependencies**: P3.T1.S1  
**Effort**: S / 2–3 hours  
**Acceptance Criteria**:
- `verification_link` with invalid URL returns `422`
- All GET, POST, PATCH, and DELETE endpoints function correctly
- Ownership check prevents cross-user access

---

## Appendix

### Glossary

| Term | Definition |
|------|-----------|
| **Master Profile** | The 1:1 `UserProfile` record tied to a user account. The root of all profile data. |
| **List Section** | A profile section that supports multiple entries (Education, Experience, Projects, Research, Certifications). Stored as separate tables with FK to `user_profiles`. |
| **JSONB** | PostgreSQL's binary JSON column type. Used for list fields such as `bullet_points` and `reference_links` on section rows. Faster than `JSON` for read operations and supports indexing. Skills are stored as **normalized `SkillItem` rows**, not JSONB blobs on `UserProfile`. |
| **SAVEPOINT** | A PostgreSQL transaction feature that allows partial rollback. Used in Pytest fixtures to isolate test data. |
| **Ownership validation** | The check that `profile.user_id == current_user.id` performed in `get_profile_or_404` before any read/write operation. |
| **Upsert** | Insert if not exists, update if exists. Used for `PersonalDetails` (which has no separate create endpoint). |
| **bleach** | Python library for sanitizing HTML. Strips all tags from user input text fields. |

---

### Full Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R1 | Alembic generates `sa.JSON` instead of `postgresql.JSONB` | Medium | Medium | Always review migration file before `alembic upgrade`. Manually fix if needed. |
| R2 | SAVEPOINT rollback breaks if session scoping is wrong | Medium | High | Run canary test (P1.T4.S3) before writing any feature tests. |
| R3 | Session auth key name mismatch in `get_current_user` | Low | High | Check existing auth code before writing the dependency. |
| R4 | `bleach` version incompatibility with Python version | Low | Low | Pin `bleach>=6.0.0` in requirements and verify Python 3.8+. |
| R5 | Date validation edge cases (`MM/YYYY` format varies) | Medium | Low | Use strict regex `^(0[1-9]|1[0-2])\/\d{4}$` and test with boundary values. |
| R6 | `cascade="all, delete-orphan"` not propagating in Alembic migration | Low | High | After migration, manually test a user deletion and verify cascade removes profile + sections. |

---

### Assumptions Log

| ID | Assumption | Impact if Wrong |
|----|-----------|----------------|
| A1 | Existing `User` model has an integer or UUID `id` PK | FK definition in `UserProfile` must be updated to match actual PK type |
| A2 | Session stores user identifier under `request.session["user_id"]` | `get_current_user` dependency must be updated to use the correct key |
| A3 | Alembic is already initialised (`alembic/` directory exists) | Run `alembic init alembic` as a prerequisite if not |
| A4 | Python 3.8+ is in use | `bleach` 6.x requires Python 3.8+ |
| A5 | SQLAlchemy 1.4+ or 2.0 is in use | Some syntax in implementation hints uses 2.0 `select()` API; adjust to `session.query()` if on older version |
| A6 | A shared declarative `Base` is used across all models | If feature uses its own `Base`, register it separately in Alembic `env.py` |
| A7 | Clients load profile data **per section** via dedicated GET routes; there is no monolithic full-profile response | Pagination or ETags on large lists may be added later if needed |

---

### File Structure Reference

Each sub-feature under `user_profile/` owns **schemas**, **routes**, **service** (when needed), **tests**, optional **endpoints/** (handler modules imported by `router.py`), **`features.md`**, and a temporary **`To-test.md`** (manual QA — delete after QA; see [Documentation and testing standards](#documentation-and-testing-standards)). Shared **dependencies** (`get_current_user`, `get_profile_or_404`) and **validators** (`sanitize_text`) live at the feature root — import them from sub-features.

```
backend/
└── app/
    ├── core/
    │   └── errors.py
    ├── features/
    │   └── user_profile/
    │       ├── __init__.py                  # May aggregate sub-routers
    │       ├── dependencies.py              # get_current_user, get_profile_or_404 (shared)
    │       ├── validators.py                # sanitize_text() (shared)
    │       ├── models/
    │       │   └── __init__.py              # Barrel: imports all sub-feature models for Alembic
    │       ├── tests/                       # Shared: conftest, canary
    │       │   ├── conftest.py
    │       │   └── test_fixtures_canary.py
    │       ├── personal/
    │       │   ├── __init__.py
    │       │   ├── models.py                # UserProfile, PersonalDetails (coordinate with barrel)
    │       │   ├── schemas.py
    │       │   ├── router.py
    │       │   ├── service.py
    │       │   ├── dependencies.py
    │       │   ├── validators.py
    │       │   ├── endpoints/
    │       │   ├── features.md
    │       │   ├── To-test.md
    │       │   └── tests/
    │       │       └── test_profile_core.py
    │       ├── education/
    │       │   ├── __init__.py
    │       │   ├── models.py
    │       │   ├── schemas.py
    │       │   ├── router.py
    │       │   ├── service.py
    │       │   ├── dependencies.py
    │       │   ├── validators.py
    │       │   ├── endpoints/
    │       │   ├── features.md
    │       │   ├── To-test.md
    │       │   └── tests/
    │       │       └── test_education.py
    │       ├── experience/                  # … same pattern as education …
    │       ├── projects/
    │       ├── research/
    │       ├── skills/
    │       └── certifications/
└── alembic/
    └── versions/
        ├── xxxx_add_user_profile_base.py
        └── xxxx_add_user_profile_sections.py  # skill_items, educations, experiences, …
```

### Documentation and testing standards

- **Docstrings (required)**: Every **endpoint handler**, **service function**, and **non-trivial** dependency or validator must have a docstring (purpose, parameters, returns, raises, and side effects where relevant).
- **`To-test.md` (per sub-feature)**: Write one `To-test.md` in each sub-feature directory with manual QA steps (e.g. curl/httpie, session auth, happy paths, 401/404/422). These files are **for QA only**; **delete** them after manual testing is complete. Optionally add `To-test.md` to `.gitignore` if you prefer they never enter version control.

### Engineering workflow (Superpowers)

**Entry point — skill id `using-superpowers`:** Invoke relevant skills **before** acting; user instructions take precedence; use **process skills before implementation skills**.

| When | Skill id (invoke this name) | Notes |
|------|------------------------------|-------|
| Designing behavior / new features | `brainstorming` | Before creative or ambiguous design work |
| Multi-step work before coding | `writing-plans` | Multi-step implementation from spec |
| Independent parallel workstreams | `subagent-driven-development` or `executing-plans` | Parallel tasks vs checkpointed execution |
| Before claiming done / before commit / PR | `verification-before-completion` | Run verification commands; evidence before success claims |
| Before merge | `requesting-code-review` | Use `receiving-code-review` when acting on feedback |
| Bugs / failures | `systematic-debugging` | Before proposing fixes |

**Claude Code — which Skill to load:** Use the **Skill** tool to load `using-superpowers` first on any profile task. Then load the skill **id** from the table above that matches the current phase. Skill ids match Superpowers directories: `.../skills/<id>/SKILL.md`.

**Typical sequence**

| Step | Action | Skill id to load |
|------|--------|-------------------|
| 1 | New feature slice or unclear scope | `brainstorming` (and `using-superpowers` if not already loaded) |
| 2 | Multi-step change with no written plan | `writing-plans` |
| 3 | Execute plan with parallel subtasks | `subagent-driven-development` |
| 4 | Execute plan across sessions with checkpoints | `executing-plans` |
| 5 | Before done / commit / PR | `verification-before-completion` |
| 6 | Before merge | `requesting-code-review` |
| 7 | Review comments need changes | `receiving-code-review` |
| 8 | Test failure or bug | `systematic-debugging` |

*Use the Skill tool to load `using-superpowers` first; then load the skill id from the workflow table for your current phase. Do not skip skill loading when the task matches the “When” column.*

**Cursor / other IDEs:** Use the same skill **ids** when skills are exposed as agent skills or workspace rules.

### Development order

Execute tasks in the following order to respect dependencies and reuse patterns. Use the [Engineering workflow](#engineering-workflow-superpowers) above during implementation.

| Order | Task / feature | Rationale |
|-------|----------------|-----------|
| 1 | **P1** — Foundation: migrations, barrel `models/`, `dependencies.py`, `validators.py`, shared `tests/` + canary | All features depend on DB, auth deps, and fixtures |
| 2 | **P2** — `POST /profile`, personal sub-feature: `GET /profile/personal`, `PATCH /profile/personal`, tests | Parent `UserProfile` row and `get_profile_or_404` required for section routes |
| 3 | **P3.T1 Education** — GET list + GET by id + POST/PATCH/DELETE, tests | Template for remaining list sections |
| 4 | **P3.T2 Experience** | Same pattern as Education |
| 5 | **P3.T3 Projects** | Same pattern |
| 6 | **P3.T4 Research** | Same pattern |
| 7 | **P3.T6 Certifications** | Same pattern |
| 8 | **P3.T5 Skills** | Normalized `SkillItem` model and sync semantics — after list-section patterns are proven |

Parallelism: after Education (order 3) is stable, Experience, Projects, Research, and Certifications (orders 4–7) may proceed in parallel by different contributors if branches are coordinated.

---

### Plan verification checklist (for editors of this document)

- Search for obsolete phrases: monolithic `get_full_profile`, `GET /profile` returning the full profile (except `POST /profile` bootstrap), and JSONB skill arrays on `UserProfile`.
- Confirm the [API surface](#api-surface-read-paths) section lists every GET route in one place.
- Confirm Skills are documented as **normalized `SkillItem`** rows with stable IDs, not JSONB-only on `UserProfile`.
