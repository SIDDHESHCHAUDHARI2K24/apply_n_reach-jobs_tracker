"""Service functions for job_opening_experience section."""
import json

import asyncpg
from fastapi import HTTPException, status

from app.features.job_tracker.opening_resume.service import _get_resume_id
from app.features.job_tracker.opening_resume.experience.schemas import (
    ExperienceCreate,
    ExperienceUpdate,
)

_JSONB_FIELDS = frozenset({"bullet_points", "work_sample_links"})


def _parse_row(row: asyncpg.Record) -> dict:
    """Deserialize JSONB columns that asyncpg may return as strings on RETURNING."""
    d = dict(row)
    for key in _JSONB_FIELDS:
        if isinstance(d.get(key), str):
            d[key] = json.loads(d[key])
    return d


def _build_update_query(table: str, where: dict, updates: dict) -> tuple[str, list]:
    """Build a parameterized UPDATE query without updated_at."""
    params = []
    set_parts = []
    for col, val in updates.items():
        if col in _JSONB_FIELDS:
            params.append(json.dumps(val) if val is not None else None)
            set_parts.append(f"{col}=${len(params)}")
        else:
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
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    return await conn.fetch(
        "SELECT * FROM job_opening_experience WHERE resume_id=$1 ORDER BY display_order ASC",
        resume_id,
    )


async def get_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
) -> asyncpg.Record:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    row = await conn.fetchrow(
        "SELECT * FROM job_opening_experience WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )
    return row


async def create_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    data: ExperienceCreate,
) -> asyncpg.Record:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    return await conn.fetchrow(
        """
        INSERT INTO job_opening_experience
            (resume_id, company, title, location, start_date, end_date,
             is_current, description, bullet_points, work_sample_links, display_order)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING *
        """,
        resume_id,
        data.company,
        data.title,
        data.location,
        data.start_date,
        data.end_date,
        data.is_current,
        data.description,
        json.dumps(data.bullet_points),
        json.dumps(data.work_sample_links),
        data.display_order,
    )


async def update_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
    data: ExperienceUpdate,
) -> asyncpg.Record:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = _build_update_query(
        "job_opening_experience",
        {"id": entry_id, "resume_id": resume_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )
    return row


async def delete_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
) -> None:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    result = await conn.execute(
        "DELETE FROM job_opening_experience WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience entry not found",
        )
