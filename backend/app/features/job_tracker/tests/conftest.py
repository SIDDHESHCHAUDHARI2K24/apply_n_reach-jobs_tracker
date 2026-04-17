"""Pytest fixtures for job_tracker cross-user isolation tests."""
import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings


async def _create_user_with_profile(email_prefix: str):
    """Create a test user and job_profile with personal details in the DB."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"{email_prefix}-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        user_data = dict(user)

        profile = await conn.fetchrow(
            """
            INSERT INTO job_profiles (user_id, profile_name, target_role)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            user_data["id"],
            f"Profile {uuid.uuid4().hex[:8]}",
            "Software Engineer",
        )
        profile_data = dict(profile)

        # Populate personal details (required for resume snapshot)
        await conn.execute(
            """
            INSERT INTO job_profile_personal_details
                (job_profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            profile_data["id"],
            "Test User",
            email,
            "https://linkedin.com/in/testuser",
            "https://github.com/testuser",
            None,
        )

        return user_data, profile_data
    finally:
        await conn.close()


async def _create_user_only(email_prefix: str):
    """Create a test user (no profile needed)."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"{email_prefix}-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        return dict(user)
    finally:
        await conn.close()


@pytest.fixture(scope="module")
def _user_a_data():
    """Create user A and their profile once for the module."""
    return asyncio.run(_create_user_with_profile("test-jt-isolation-a"))


@pytest.fixture(scope="module")
def _user_b_data():
    """Create user B (no profile needed) once for the module."""
    return asyncio.run(_create_user_only("test-jt-isolation-b"))


@pytest.fixture(scope="module")
def user_a_client(_user_a_data):
    """TestClient authenticated as user A, using its own dedicated app instance."""
    user_data, _ = _user_a_data
    app = create_app()

    async def override():
        return user_data

    app.dependency_overrides[get_current_user] = override
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def user_b_client(_user_b_data):
    """TestClient authenticated as user B, using its own dedicated app instance."""
    user_data = _user_b_data
    app = create_app()

    async def override():
        return user_data

    app.dependency_overrides[get_current_user] = override
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def opening_a(user_a_client):
    """A job opening created by user A."""
    resp = user_a_client.post(
        "/job-openings",
        json={
            "company_name": f"Acme Corp {uuid.uuid4().hex[:8]}",
            "role_name": "Software Engineer",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture(scope="module")
def profile_a(_user_a_data):
    """The job_profile owned by user A."""
    _, profile_data = _user_a_data
    return profile_data


@pytest.fixture(scope="module")
def resume_a(user_a_client, opening_a, profile_a):
    """Opening resume created for opening_a from profile_a, owned by user A."""
    resp = user_a_client.post(
        f"/job-openings/{opening_a['id']}/resume"
        f"?source_job_profile_id={profile_a['id']}"
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
