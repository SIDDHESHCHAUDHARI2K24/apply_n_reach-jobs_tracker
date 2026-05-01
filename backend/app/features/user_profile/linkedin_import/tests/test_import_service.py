"""Tests for LinkedIn import service — atomic replace-all."""
import asyncio

import asyncpg
import pytest

from app.features.core.config import settings
from app.features.user_profile.linkedin_import.schemas import (
    MappedLinkedInProfile,
    MappedPersonal,
    MappedEducation,
    MappedExperience,
    MappedCertification,
    MappedSkill,
)
from app.features.user_profile.linkedin_import.service import replace_profile_from_linkedin


async def _run_replace(profile_id: int, mapped: MappedLinkedInProfile) -> dict:
    conn = await asyncpg.connect(settings.database_url)
    try:
        return await replace_profile_from_linkedin(conn, profile_id, mapped)
    finally:
        await conn.close()


async def _count_sections(profile_id: int) -> dict:
    conn = await asyncpg.connect(settings.database_url)
    try:
        personal = await conn.fetchval(
            "SELECT COUNT(*) FROM personal_details WHERE profile_id = $1", profile_id
        )
        edu = await conn.fetchval(
            "SELECT COUNT(*) FROM educations WHERE profile_id = $1", profile_id
        )
        exp = await conn.fetchval(
            "SELECT COUNT(*) FROM experiences WHERE profile_id = $1", profile_id
        )
        certs = await conn.fetchval(
            "SELECT COUNT(*) FROM certifications WHERE profile_id = $1", profile_id
        )
        skills = await conn.fetchval(
            "SELECT COUNT(*) FROM skill_items WHERE profile_id = $1", profile_id
        )
        return {
            "personal": personal,
            "education": edu,
            "experience": exp,
            "certifications": certs,
            "skills": skills,
        }
    finally:
        await conn.close()


class TestReplaceProfileFromLinkedIn:
    """Test the atomic replace-all service function."""

    def test_replace_all_sections(self, auth_client):
        """Should delete existing data and insert new data."""
        _, _, profile_data = auth_client

        mapped = MappedLinkedInProfile(
            personal=MappedPersonal(full_name="New Name", email="new@example.com", linkedin_url="https://linkedin.com/in/new"),
            educations=[
                MappedEducation(
                    university_name="MIT",
                    major="CS",
                    degree_type="MS",
                    start_month_year="09/2020",
                    end_month_year="06/2022",
                ),
                MappedEducation(
                    university_name="Stanford",
                    major="Math",
                    degree_type="BS",
                    start_month_year="09/2016",
                    end_month_year="06/2020",
                ),
            ],
            experiences=[
                MappedExperience(
                    role_title="Senior Engineer",
                    company_name="Google",
                    start_month_year="07/2022",
                    context="Built ML pipelines",
                ),
            ],
            certifications=[
                MappedCertification(certification_name="AWS Solutions Architect", verification_link="https://aws.amazon.com/cert/"),
            ],
            skills=[
                MappedSkill(kind="technical", name="Python", sort_order=0),
                MappedSkill(kind="technical", name="TensorFlow", sort_order=1),
                MappedSkill(kind="competency", name="Leadership", sort_order=2),
            ],
        )

        counts = asyncio.run(_run_replace(profile_data["id"], mapped))
        assert counts["personal"] == 1
        assert counts["education"] == 2
        assert counts["experience"] == 1
        assert counts["certifications"] == 1
        assert counts["skills"] == 3

        # Verify in DB
        db_counts = asyncio.run(_count_sections(profile_data["id"]))
        assert db_counts["personal"] == 1
        assert db_counts["education"] == 2  # Old one replaced
        assert db_counts["experience"] == 1
        assert db_counts["certifications"] == 1
        assert db_counts["skills"] == 3

    def test_replace_with_empty_clears_data(self, auth_client):
        """Replacing with empty sections should clear existing data."""
        _, _, profile_data = auth_client

        mapped = MappedLinkedInProfile()  # All empty

        counts = asyncio.run(_run_replace(profile_data["id"], mapped))
        assert counts.get("education", 0) == 0

        db_counts = asyncio.run(_count_sections(profile_data["id"]))
        assert db_counts["education"] == 0
        assert db_counts["skills"] == 0
