"""Pytest fixtures for job_tracker opening_ingestion tests."""
import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings
from app.features.job_tracker.opening_ingestion.router import router as ingestion_router
from app.features.job_tracker.openings_core.router import router as openings_router
from app.features.job_tracker.schemas import ExtractedJobDetails


def make_app():
    """Create a fresh app instance with openings + ingestion routers registered."""
    app = create_app()
    app.include_router(openings_router)
    app.include_router(ingestion_router)
    return app


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def auth_client(app):
    """Yield (client, user_data) with get_current_user overridden to a real DB user."""

    async def _create_test_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-ingestion-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass")
            )
            return dict(user)
        finally:
            await conn.close()

    user_data = asyncio.run(_create_test_user())

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data

    app.dependency_overrides.clear()


@pytest.fixture
def sample_opening(auth_client):
    """Create a sample opening with a source_url via the API and return response JSON."""
    client, user_data = auth_client
    resp = client.post(
        "/job-openings",
        json={
            "company_name": f"Acme Corp {uuid.uuid4().hex[:8]}",
            "role_name": "Software Engineer",
            "source_url": "https://example.com/jobs/software-engineer",
            "notes": "Initial note",
        },
    )
    assert resp.status_code == 201
    opening = resp.json()

    # Opening creation now auto-enqueues extraction; clear auto-created run artifacts
    # so ingestion endpoint tests can control run state explicitly.
    async def reset_auto_extraction_state():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await conn.execute(
                "DELETE FROM job_opening_extracted_details_versions WHERE opening_id=$1",
                opening["id"],
            )
            await conn.execute(
                "DELETE FROM job_opening_extraction_runs WHERE opening_id=$1",
                opening["id"],
            )
        finally:
            await conn.close()

    asyncio.run(reset_auto_extraction_state())
    return opening


SAMPLE_RAW_TEXT = """
Software Engineer - Acme Corp

We are looking for a Software Engineer to join our team.

Location: San Francisco, CA (Remote OK)
Salary: $120,000 - $160,000

Requirements:
- 3+ years of Python experience
- Experience with FastAPI or Django
- PostgreSQL knowledge

Nice to have:
- Kubernetes experience
- Docker experience

Employment Type: Full-time
"""

SAMPLE_EXTRACTED = ExtractedJobDetails(
    job_title="Software Engineer",
    company_name="Acme Corp",
    location="San Francisco, CA (Remote OK)",
    employment_type="Full-time",
    description_summary="Software Engineer role at Acme Corp. Posted salary band: $120,000 - $160,000.",
    required_skills=["Python", "FastAPI", "PostgreSQL"],
    preferred_skills=["Kubernetes", "Docker"],
    experience_level="Mid-level",
    posted_date=None,
    application_deadline=None,
    extractor_model="claude-haiku-4-5-20251001",
    source_url="https://example.com/jobs/software-engineer",
)


@pytest.fixture
def mock_crawl():
    """Patch crawl_url at the service level (where it is imported) to avoid hitting Apify."""
    with patch(
        "app.features.job_tracker.opening_ingestion.service.crawl_url",
        new_callable=AsyncMock,
        return_value=SAMPLE_RAW_TEXT,
    ) as mock:
        yield mock


@pytest.fixture
def mock_extract():
    """Patch extract_job_details at the service level to avoid hitting Claude."""
    with patch(
        "app.features.job_tracker.opening_ingestion.service.extract_job_details",
        new_callable=AsyncMock,
        return_value=SAMPLE_EXTRACTED,
    ) as mock:
        yield mock
