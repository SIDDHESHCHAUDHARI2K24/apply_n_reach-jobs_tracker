"""Service functions for opening resume snapshot creation and retrieval."""
import asyncpg
from fastapi import HTTPException, status


async def create_opening_resume(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    source_job_profile_id: int,
) -> asyncpg.Record:
    """Atomically snapshot a job_profile into a job_opening_resume.

    - Verify opening exists and is owned by user
    - Verify source job_profile is owned by user
    - Check no resume exists yet (409 if it does)
    - INSERT job_opening_resumes root row
    - Bulk INSERT all 7 sections using column-mapped INSERT...SELECT
    All in a single transaction.
    """
    async with conn.transaction():
        # Check opening ownership
        opening = await conn.fetchrow(
            "SELECT id FROM job_openings WHERE id=$1 AND user_id=$2",
            opening_id,
            user_id,
        )
        if not opening:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job opening not found",
            )

        # Check job_profile ownership
        profile = await conn.fetchrow(
            "SELECT id FROM job_profiles WHERE id=$1 AND user_id=$2",
            source_job_profile_id,
            user_id,
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job profile not found",
            )

        # Check no resume exists already
        existing = await conn.fetchrow(
            "SELECT id FROM job_opening_resumes WHERE opening_id=$1",
            opening_id,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resume already exists for this opening",
            )

        # Create resume root row
        resume = await conn.fetchrow(
            """
            INSERT INTO job_opening_resumes
                (opening_id, source_job_profile_id, snapshot_version, source_section_count)
            VALUES ($1, $2, 1, 7)
            RETURNING *
            """,
            opening_id,
            source_job_profile_id,
        )
        resume_id = resume["id"]

        # Copy personal — map job_profile_personal_details -> job_opening_personal
        # Columns available: full_name, email, linkedin_url, github_url, portfolio_url
        # job_opening_personal also has: phone, location, summary (not in source)
        await conn.execute(
            """
            INSERT INTO job_opening_personal
                (resume_id, full_name, email, phone, location, linkedin_url, github_url, portfolio_url, summary)
            SELECT $1, full_name, email, NULL, NULL, linkedin_url, github_url, portfolio_url, NULL
            FROM job_profile_personal_details
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy education — map job_profile_educations -> job_opening_education
        # Source cols: university_name, major, degree_type, start_month_year, end_month_year
        # Target cols: institution, degree, field_of_study, start_date, end_date, grade, description
        await conn.execute(
            """
            INSERT INTO job_opening_education
                (resume_id, institution, degree, field_of_study, start_date, end_date, grade, description, display_order)
            SELECT $1, university_name, degree_type, major, start_month_year, end_month_year, NULL, NULL, 0
            FROM job_profile_educations
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy experience — map job_profile_experiences -> job_opening_experience
        # Source cols: role_title, company_name, start_month_year, end_month_year, context
        # Target cols: company, title, location, start_date, end_date, is_current, description
        await conn.execute(
            """
            INSERT INTO job_opening_experience
                (resume_id, company, title, location, start_date, end_date, is_current, description, display_order)
            SELECT $1, company_name, role_title, NULL, start_month_year, end_month_year,
                   (end_month_year IS NULL), context, 0
            FROM job_profile_experiences
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy projects — map job_profile_projects -> job_opening_projects
        # Source cols: project_name, description, start_month_year, end_month_year, reference_links(JSONB)
        # Target cols: name, description, url, start_date, end_date, technologies(JSONB)
        await conn.execute(
            """
            INSERT INTO job_opening_projects
                (resume_id, name, description, url, start_date, end_date, technologies, display_order)
            SELECT $1, project_name, description, NULL, start_month_year, end_month_year, NULL, 0
            FROM job_profile_projects
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy research — map job_profile_researches -> job_opening_research
        # Source cols: paper_name, publication_link, description
        # Target cols: title, publication, published_date, url, description
        await conn.execute(
            """
            INSERT INTO job_opening_research
                (resume_id, title, publication, published_date, url, description, display_order)
            SELECT $1, paper_name, NULL, NULL, publication_link, description, 0
            FROM job_profile_researches
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy certifications — map job_profile_certifications -> job_opening_certifications
        # Source cols: certification_name, verification_link
        # Target cols: name, issuer, issue_date, expiry_date, credential_id, url
        await conn.execute(
            """
            INSERT INTO job_opening_certifications
                (resume_id, name, issuer, issue_date, expiry_date, credential_id, url, display_order)
            SELECT $1, certification_name, NULL, NULL, NULL, NULL, verification_link, 0
            FROM job_profile_certifications
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        # Copy skills — map job_profile_skill_items -> job_opening_skills
        # Source cols: kind (technical/competency), name, sort_order
        # Target cols: category, name, proficiency_level, display_order
        await conn.execute(
            """
            INSERT INTO job_opening_skills
                (resume_id, category, name, proficiency_level, display_order)
            SELECT $1, kind, name, NULL, sort_order
            FROM job_profile_skill_items
            WHERE job_profile_id=$2
            """,
            resume_id,
            source_job_profile_id,
        )

        return resume


async def get_opening_resume(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> asyncpg.Record:
    """Get resume for opening. 404 if opening not owned or resume not found."""
    opening = await conn.fetchrow(
        "SELECT id FROM job_openings WHERE id=$1 AND user_id=$2",
        opening_id,
        user_id,
    )
    if not opening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job opening not found",
        )
    resume = await conn.fetchrow(
        "SELECT * FROM job_opening_resumes WHERE opening_id=$1",
        opening_id,
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found for this opening",
        )
    return resume


async def _get_resume_id(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> int:
    """Resolve resume_id for an opening while verifying user ownership."""
    row = await conn.fetchrow(
        """
        SELECT r.id FROM job_opening_resumes r
        JOIN job_openings o ON o.id = r.opening_id
        WHERE r.opening_id=$1 AND o.user_id=$2
        """,
        opening_id,
        user_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    return row["id"]
