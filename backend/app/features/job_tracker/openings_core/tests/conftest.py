"""Pytest fixtures for job_tracker openings_core tests."""
import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings
from app.features.job_tracker.openings_core.router import router as openings_router


def make_app():
    """Create a fresh app instance with the openings router registered."""
    app = create_app()
    # NOTE: openings_router not yet registered in create_app() (done in Unit 5).
    # If it is later registered, remove this override to avoid duplicate routes.
    app.include_router(openings_router)
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
            email = f"test-jobtracker-{uuid.uuid4().hex}@example.com"
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
    """Create a sample opening via the API and return the response JSON."""
    client, user_data = auth_client
    resp = client.post(
        "/job-openings",
        json={
            "company_name": f"Acme Corp {uuid.uuid4().hex[:8]}",
            "role_name": "Software Engineer",
            "notes": "Initial note",
        },
    )
    assert resp.status_code == 201
    return resp.json()
