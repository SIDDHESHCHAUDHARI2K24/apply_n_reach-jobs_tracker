"""Service functions for job_opening_projects section."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.job_tracker.opening_resume.service import _get_resume_id
from app.features.job_tracker.opening_resume.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
)


def _parse_technologies(row: asyncpg.Record) -> dict:
    """Convert row to dict with technologies deserialized from JSONB string if needed.

    asyncpg returns JSONB as a native Python list/dict on plain SELECT queries, so
    the isinstance check is a no-op on list_entries / get_entry paths.  It is only
    needed for INSERT / UPDATE RETURNING paths, where asyncpg delivers the JSONB
    column back as a raw JSON string rather than a decoded Python object.
    """
    d = dict(row)
    if isinstance(d.get("technologies"), str):
        d["technologies"] = json.loads(d["technologies"])
    return d


def _build_update_query(
    table: str,
    where: dict,
    updates: dict,
    jsonb_fields: set,
) -> tuple[str, list]:
    """Build a parameterized UPDATE query without updated_at."""
    params = []
    set_parts = []
    for col, val in updates.items():
        if col in jsonb_fields:
            # Pass json.dumps string without ::jsonb cast — asyncpg handles NULL natively
            # and Postgres coerces non-null strings to jsonb via the column type.
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
        "SELECT * FROM job_opening_projects WHERE resume_id=$1 ORDER BY display_order ASC",
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
        "SELECT * FROM job_opening_projects WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project entry not found",
        )
    return row


async def create_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    data: ProjectCreate,
) -> asyncpg.Record:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    # Pass technologies as plain $7 — asyncpg handles NULL natively without a ::jsonb cast.
    # When non-null, json.dumps produces a string that Postgres coerces to jsonb via the column type.
    technologies = json.dumps(data.technologies) if data.technologies is not None else None
    return await conn.fetchrow(
        """
        INSERT INTO job_opening_projects
            (resume_id, name, description, url, start_date, end_date, technologies, display_order)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
        """,
        resume_id,
        data.name,
        data.description,
        data.url,
        data.start_date,
        data.end_date,
        technologies,
        data.display_order,
    )


async def update_entry(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    entry_id: int,
    data: ProjectUpdate,
) -> asyncpg.Record:
    resume_id = await _get_resume_id(conn, user_id, opening_id)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = _build_update_query(
        "job_opening_projects",
        {"id": entry_id, "resume_id": resume_id},
        updates,
        jsonb_fields={"technologies"},
    )
    row = await conn.fetchrow(query, *params)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project entry not found",
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
        "DELETE FROM job_opening_projects WHERE id=$1 AND resume_id=$2",
        entry_id,
        resume_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project entry not found",
        )
