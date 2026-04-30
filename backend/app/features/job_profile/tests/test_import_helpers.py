"""Integration tests for import_helpers utility functions."""
import uuid
import asyncio
import asyncpg
import pytest

from app.features.core.config import settings
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import hash_password
from app.features.job_profile.import_helpers import validate_source_ownership, get_already_imported


async def _setup_user_with_education():
    """Create a user with profile and one education entry. Returns (user_dict, profile_id, edu_id)."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"import-test-{uuid.uuid4().hex}@example.com"
        user = await create_user(conn, email=email, password_hash=hash_password("x"))
        user = dict(user)

        # Create user_profile
        from app.features.user_profile.personal.models import ensure_profile_schema
        await ensure_profile_schema(conn)
        profile = await conn.fetchrow(
            "INSERT INTO user_profiles (user_id) VALUES ($1) RETURNING id, user_id",
            user["id"]
        )

        # Create education entry
        from app.features.user_profile.education.models import ensure_education_schema
        await ensure_education_schema(conn)
        edu = await conn.fetchrow(
            "INSERT INTO educations (profile_id, university_name, major, degree_type, "
            "start_month_year, bullet_points, reference_links) "
            "VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb) RETURNING id",
            profile["id"], "Test University", "CS", "BS", "09/2020",
            "[]", "[]"
        )

        return user, profile["id"], edu["id"]
    finally:
        await conn.close()


def test_validate_source_ownership_valid_ids():
    """User's own education IDs should be returned as valid."""
    user, profile_id, edu_id = asyncio.run(_setup_user_with_education())

    async def _run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            valid_ids, not_found_ids = await validate_source_ownership(
                conn, "educations", [edu_id], user["id"]
            )
            return valid_ids, not_found_ids
        finally:
            await conn.close()

    valid_ids, not_found_ids = asyncio.run(_run())
    assert edu_id in valid_ids
    assert edu_id not in not_found_ids


def test_validate_source_ownership_cross_user():
    """Education IDs belonging to User B should not be valid for User A."""
    # Create two separate users, each with their own education
    user_a, _, edu_id_a = asyncio.run(_setup_user_with_education())
    user_b, _, edu_id_b = asyncio.run(_setup_user_with_education())

    async def _run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            # User A tries to claim User B's education ID
            valid_ids, not_found_ids = await validate_source_ownership(
                conn, "educations", [edu_id_b], user_a["id"]
            )
            return valid_ids, not_found_ids
        finally:
            await conn.close()

    valid_ids, not_found_ids = asyncio.run(_run())
    # User B's edu should NOT be valid for User A
    assert edu_id_b not in valid_ids
    assert edu_id_b in not_found_ids


def test_validate_source_ownership_nonexistent():
    """Non-existent IDs should be in not_found_ids."""
    user, _, _ = asyncio.run(_setup_user_with_education())
    nonexistent_id = 999999999

    async def _run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            valid_ids, not_found_ids = await validate_source_ownership(
                conn, "educations", [nonexistent_id], user["id"]
            )
            return valid_ids, not_found_ids
        finally:
            await conn.close()

    valid_ids, not_found_ids = asyncio.run(_run())
    assert nonexistent_id not in valid_ids
    assert nonexistent_id in not_found_ids


def test_get_already_imported_none():
    """When nothing has been imported, get_already_imported returns empty list.

    Uses a temporary table with job_profile_id column to test the helper.
    """
    user, _, edu_id = asyncio.run(_setup_user_with_education())

    async def _run():
        conn = await asyncpg.connect(settings.database_url)
        try:
            # Create a job profile to test against
            from app.features.job_profile.core.models import ensure_job_profiles_schema
            await ensure_job_profiles_schema(conn)
            jp = await conn.fetchrow(
                "INSERT INTO job_profiles (user_id, profile_name) VALUES ($1, $2) RETURNING id",
                user["id"], f"Test JP {uuid.uuid4().hex[:8]}"
            )

            # Create a temporary import-like table with job_profile_id column
            await conn.execute("""
                CREATE TEMP TABLE IF NOT EXISTS temp_import_test (
                    id SERIAL PRIMARY KEY,
                    job_profile_id INTEGER NOT NULL,
                    source_edu_id INTEGER NOT NULL
                )
            """)

            # No records inserted yet - should return empty list
            result = await get_already_imported(
                conn,
                "temp_import_test",
                jp["id"],
                "source_edu_id",
                [edu_id, 999999997]
            )
            return result
        finally:
            await conn.close()

    result = asyncio.run(_run())
    assert isinstance(result, list)
    assert len(result) == 0
