"""Service functions for job_profile core CRUD."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_profile.core import models
from app.features.job_profile.core.schemas import (
    JobProfileCreate,
    JobProfileListParams,
    JobProfileUpdate,
)

_MAX_JOB_PROFILES = 50


async def create_job_profile(
    conn: asyncpg.Connection, user_id: int, data: JobProfileCreate
) -> asyncpg.Record:
    """Create a new job profile for the user. Cap at 50 profiles."""
    await models.ensure_job_profiles_schema(conn)

    # Count existing profiles
    count = await conn.fetchval(
        "SELECT COUNT(*) FROM job_profiles WHERE user_id = $1", user_id
    )
    if count >= _MAX_JOB_PROFILES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maximum of {_MAX_JOB_PROFILES} job profiles allowed",
        )

    try:
        row = await conn.fetchrow(
            "INSERT INTO job_profiles (user_id, profile_name, target_role, target_company, job_posting_url) "
            "VALUES ($1, $2, $3, $4, $5) "
            "RETURNING *",
            user_id,
            data.profile_name,
            data.target_role,
            data.target_company,
            data.job_posting_url,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job profile with this name already exists",
        )
    return row


async def list_job_profiles(
    conn: asyncpg.Connection, user_id: int, params: JobProfileListParams
) -> tuple[list[asyncpg.Record], int]:
    """List job profiles for the user with optional status filter and pagination."""
    await models.ensure_job_profiles_schema(conn)

    where_parts = ["user_id = $1"]
    args = [user_id]

    if params.status is not None:
        args.append(params.status)
        where_parts.append(f"status = ${len(args)}")

    where_clause = " AND ".join(where_parts)

    total = await conn.fetchval(
        f"SELECT COUNT(*) FROM job_profiles WHERE {where_clause}", *args
    )

    args_data = args + [params.limit, params.offset]
    rows = await conn.fetch(
        f"SELECT * FROM job_profiles WHERE {where_clause} "
        f"ORDER BY created_at DESC "
        f"LIMIT ${len(args_data) - 1} OFFSET ${len(args_data)}",
        *args_data,
    )

    return list(rows), total


async def get_job_profile(
    conn: asyncpg.Connection, user_id: int, job_profile_id: int
) -> asyncpg.Record:
    """Get a single job profile by id, verifying ownership."""
    await models.ensure_job_profiles_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profiles WHERE id = $1 AND user_id = $2",
        job_profile_id, user_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job profile not found",
        )
    return row


async def update_job_profile(
    conn: asyncpg.Connection, user_id: int, job_profile_id: int, data: JobProfileUpdate
) -> asyncpg.Record:
    """Partially update a job profile, verifying ownership."""
    await models.ensure_job_profiles_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        query, params = build_partial_update_query(
            "job_profiles",
            {"id": job_profile_id, "user_id": user_id},
            updates,
        )
        row = await conn.fetchrow(query, *params)
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A job profile with this name already exists",
        )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job profile not found",
        )
    return row


async def delete_job_profile(
    conn: asyncpg.Connection, user_id: int, job_profile_id: int
) -> None:
    """Delete a job profile, verifying ownership."""
    await models.ensure_job_profiles_schema(conn)
    result = await conn.execute(
        "DELETE FROM job_profiles WHERE id = $1 AND user_id = $2",
        job_profile_id, user_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job profile not found",
        )
