"""Pytest fixtures for agent tests."""
import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings
from app.features.job_tracker.agents.router import router as agent_router


def make_app():
    """Create a fresh app with agent router registered."""
    app = create_app()
    app.include_router(agent_router)
    return app


async def _create_test_user_and_opening():
    """Create a test user with a job opening that has extracted details."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"test-agent-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        user_data = dict(user)

        # Create a job opening
        opening = await conn.fetchrow(
            """
            INSERT INTO job_openings (user_id, company_name, role_name, source_url)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            user_data["id"],
            f"Test Corp {uuid.uuid4().hex[:8]}",
            "Software Engineer",
            "https://example.com/job",
        )

        # Create a job_profile with sections
        profile = await conn.fetchrow(
            """
            INSERT INTO job_profiles (user_id, profile_name, target_role)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            user_data["id"],
            f"Test Profile {uuid.uuid4().hex[:8]}",
            "Software Engineer",
        )

        # Add personal details to the profile
        await conn.execute(
            """
            INSERT INTO job_profile_personal_details
                (job_profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            profile["id"], "Test User", email,
            "https://linkedin.com/in/test", "https://github.com/test", None,
        )

        # Add skills
        await conn.execute(
            """
            INSERT INTO job_profile_skill_items (job_profile_id, kind, name, sort_order)
            VALUES ($1, 'technical', 'Python', 0), ($1, 'technical', 'FastAPI', 1)
            """,
            profile["id"],
        )

        return user_data, dict(opening), dict(profile)
    finally:
        await conn.close()


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def auth_client(app):
    """Yield (client, user_data, opening_data, profile_data)."""
    user_data, opening_data, profile_data = asyncio.run(
        _create_test_user_and_opening()
    )

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data, opening_data, profile_data

    app.dependency_overrides.clear()
