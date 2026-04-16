"""Service functions for job_opening_education section."""
import asyncpg
from fastapi import HTTPException, status

from app.features.job_tracker.opening_resume.service import _get_resume_id
from app.features.job_tracker.opening_resume.education.schemas import (
    EducationCreate,
    EducationUpdate,
)


def _build_update_query(
    table: str,
    where: dict,
    updates: dict,
) -> tuple[str, list]:
    """Build a parameterized UPDATE query without updated_at."""
    params = []
    set_parts = []
    for col, val in updates.items():
        params.append(val)
        set_parts.append(f"{col}=${len(params)}")

    where_parts = []
    for col, val in where.items():
        params.append(val)
        where_parts.append(f"{col}=${len(params)}")

    sql = (
        f"UPDATE {table} SET {', '.join(set_parts)} "
        f"WHERE {' AND '.join(where_parts)} "
        f"RETURNING *"
    )
    return sql, params


async def list_entries(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> list[asyncpg.Record]:
    """List all education entries for a resume, ordered by display_order."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    return await conn.fetch(
        "SELECT * FROM job_opening_education WHERE resume_id=$1 ORDER BY display_order ASC",
        resume_id,
    )


async def get_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
) -> asyncpg.Record:
    """Get a single education entry, verifying ownership."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    row = await conn.fetchrow(
        "SELECT * FROM job_opening_education WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )
    return row


async def create_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    data: EducationCreate,
) -> asyncpg.Record:
    """Create a new education entry for a resume."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    return await conn.fetchrow(
        """
        INSERT INTO job_opening_education
            (resume_id, institution, degree, field_of_study,
             start_date, end_date, grade, description, display_order)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """,
        resume_id,
        data.institution,
        data.degree,
        data.field_of_study,
        data.start_date,
        data.end_date,
        data.grade,
        data.description,
        data.display_order,
    )


async def update_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
    data: EducationUpdate,
) -> asyncpg.Record:
    """Partially update an education entry."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = _build_update_query(
        "job_opening_education",
        {"id": entry_id, "resume_id": resume_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )
    return row


async def delete_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
) -> None:
    """Delete an education entry."""
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    result = await conn.execute(
        "DELETE FROM job_opening_education WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education entry not found",
        )
