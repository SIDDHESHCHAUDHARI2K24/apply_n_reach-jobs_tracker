"""Service functions for job_opening_personal section."""
import asyncpg
from fastapi import HTTPException, status

from app.features.job_tracker.opening_resume.service import _get_resume_id
from app.features.job_tracker.opening_resume.personal.schemas import PersonalUpdate


async def get_personal(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> asyncpg.Record:
    """Get personal section for a resume. 404 if not found."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    row = await conn.fetchrow(
        "SELECT * FROM job_opening_personal WHERE resume_id=$1",
        resume_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal section not found",
        )
    return row


async def upsert_personal(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    data: PersonalUpdate,
) -> asyncpg.Record:
    """Upsert personal section (INSERT ON CONFLICT DO UPDATE)."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    fields = data.model_dump()
    row = await conn.fetchrow(
        """
        INSERT INTO job_opening_personal
            (resume_id, full_name, email, phone, location,
             linkedin_url, github_url, portfolio_url, summary)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (resume_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            location = EXCLUDED.location,
            linkedin_url = EXCLUDED.linkedin_url,
            github_url = EXCLUDED.github_url,
            portfolio_url = EXCLUDED.portfolio_url,
            summary = EXCLUDED.summary
        RETURNING *
        """,
        resume_id,
        fields["full_name"],
        fields["email"],
        fields["phone"],
        fields["location"],
        fields["linkedin_url"],
        fields["github_url"],
        fields["portfolio_url"],
        fields["summary"],
    )
    return row
