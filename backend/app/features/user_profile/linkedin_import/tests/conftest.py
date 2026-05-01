"""Pytest fixtures for LinkedIn import tests."""
import asyncio
import uuid

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings
from app.features.user_profile.linkedin_import.router import router as linkedin_router


def make_app():
    """Create a fresh app with LinkedIn import router registered."""
    app = create_app()
    app.include_router(linkedin_router)
    return app


async def _create_test_user_with_profile():
    """Create a test user with a user_profile."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"test-linkedin-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        user_data = dict(user)

        # Create user_profile
        profile = await conn.fetchrow(
            "INSERT INTO user_profiles (user_id) VALUES ($1) RETURNING *",
            user_data["id"],
        )

        # Add some existing data to verify replace-all works
        await conn.execute(
            """
            INSERT INTO personal_details (profile_id, full_name, email, linkedin_url)
            VALUES ($1, $2, $3, $4)
            """,
            profile["id"], "Old Name", email, "https://linkedin.com/in/old",
        )
        await conn.execute(
            """
            INSERT INTO educations (profile_id, university_name, major, degree_type,
                start_month_year, bullet_points, reference_links)
            VALUES ($1, $2, $3, $4, $5, '[]'::jsonb, '[]'::jsonb)
            """,
            profile["id"], "Old University", "Old Major", "BS", "09/2015",
        )

        return user_data, dict(profile)
    finally:
        await conn.close()


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def auth_client(app):
    """Yield (client, user_data, profile_data)."""
    user_data, profile_data = asyncio.run(_create_test_user_with_profile())

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data, profile_data

    app.dependency_overrides.clear()
