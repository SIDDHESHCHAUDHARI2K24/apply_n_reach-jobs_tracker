"""Pytest fixtures for job_tracker opening_resume tests."""
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
from app.features.job_tracker.opening_resume.router import router as resume_router
from app.features.job_tracker.opening_resume.personal.router import router as personal_router
from app.features.job_tracker.opening_resume.education.router import router as education_router
from app.features.job_tracker.opening_resume.experience.router import router as experience_router
from app.features.job_tracker.opening_resume.projects.router import router as projects_router
from app.features.job_tracker.opening_resume.research.router import router as research_router
from app.features.job_tracker.opening_resume.certifications.router import router as certifications_router
from app.features.job_tracker.opening_resume.skills.router import router as skills_router
from app.features.job_tracker.opening_resume.latex_resume.router import (
    router as latex_resume_router,
)
from app.features.job_tracker.opening_resume.service import create_opening_resume


def make_app():
    """Create a fresh app instance with all required routers registered."""
    app = create_app()
    app.include_router(openings_router)
    app.include_router(resume_router)
    app.include_router(personal_router)
    app.include_router(education_router)
    app.include_router(experience_router)
    app.include_router(projects_router)
    app.include_router(research_router)
    app.include_router(certifications_router)
    app.include_router(skills_router)
    app.include_router(latex_resume_router)
    return app


async def _create_test_user_and_profile():
    """Create a test user and job_profile with all 7 sections populated."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"test-resume-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        user_data = dict(user)

        # Create a job_profile
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
        profile_data = dict(profile)

        # Populate personal details
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

        # Populate education
        await conn.execute(
            """
            INSERT INTO job_profile_educations
                (job_profile_id, university_name, major, degree_type,
                 start_month_year, end_month_year, bullet_points, reference_links)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
            """,
            profile_data["id"],
            "MIT",
            "Computer Science",
            "Bachelor",
            "09/2018",
            "06/2022",
            "[]",
            "[]",
        )

        # Populate experience
        await conn.execute(
            """
            INSERT INTO job_profile_experiences
                (job_profile_id, role_title, company_name, start_month_year, end_month_year,
                 context, work_sample_links, bullet_points)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
            """,
            profile_data["id"],
            "Software Engineer",
            "Acme Corp",
            "07/2022",
            None,
            "Built cool stuff",
            "[]",
            "[]",
        )

        # Populate projects
        await conn.execute(
            """
            INSERT INTO job_profile_projects
                (job_profile_id, project_name, description, start_month_year, end_month_year,
                 reference_links)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb)
            """,
            profile_data["id"],
            "Cool Project",
            "A cool project description",
            "01/2021",
            "06/2021",
            "[]",
        )

        # Populate research
        await conn.execute(
            """
            INSERT INTO job_profile_researches
                (job_profile_id, paper_name, publication_link, description)
            VALUES ($1, $2, $3, $4)
            """,
            profile_data["id"],
            "My Research Paper",
            "https://doi.org/example",
            "A research paper description",
        )

        # Populate certifications
        await conn.execute(
            """
            INSERT INTO job_profile_certifications
                (job_profile_id, certification_name, verification_link)
            VALUES ($1, $2, $3)
            """,
            profile_data["id"],
            "AWS Certified Developer",
            "https://aws.amazon.com/verify/example",
        )

        # Populate skills
        await conn.execute(
            """
            INSERT INTO job_profile_skill_items
                (job_profile_id, kind, name, sort_order)
            VALUES ($1, $2, $3, $4), ($1, $5, $6, $7)
            """,
            profile_data["id"],
            "technical",
            "Python",
            0,
            "competency",
            "Problem Solving",
            1,
        )

        return user_data, profile_data
    finally:
        await conn.close()


@pytest.fixture
def app():
    return make_app()


@pytest.fixture
def auth_client(app):
    """Yield (client, user_data) with get_current_user overridden to a real DB user."""
    user_data, profile_data = asyncio.run(_create_test_user_and_profile())

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data

    app.dependency_overrides.clear()


@pytest.fixture
def sample_job_profile(auth_client):
    """Return the sample job_profile created for the auth_client user."""
    _, user_data = auth_client

    async def _get_profile():
        conn = await asyncpg.connect(settings.database_url)
        try:
            row = await conn.fetchrow(
                "SELECT * FROM job_profiles WHERE user_id=$1 ORDER BY id ASC LIMIT 1",
                user_data["id"],
            )
            return dict(row)
        finally:
            await conn.close()

    return asyncio.run(_get_profile())


@pytest.fixture
def sample_opening(auth_client):
    """Create a sample job opening via the API and return the response JSON."""
    client, _ = auth_client
    resp = client.post(
        "/job-openings",
        json={
            "company_name": f"Acme Corp {uuid.uuid4().hex[:8]}",
            "role_name": "Software Engineer",
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_resume(auth_client, sample_opening, sample_job_profile):
    """Create a resume snapshot via the API and return the response JSON."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume"
        f"?source_job_profile_id={sample_job_profile['id']}"
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_client_b(app):
    """A second user's auth client (for cross-user isolation tests)."""

    async def _create_user_b():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-resume-b-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass")
            )
            return dict(user)
        finally:
            await conn.close()

    user_b = asyncio.run(_create_user_b())

    async def override_get_current_user_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_get_current_user_b

    with TestClient(app) as c:
        yield c, user_b

    app.dependency_overrides.clear()
