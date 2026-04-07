"""Shared FastAPI dependencies for job_profile feature."""
import asyncpg
from fastapi import Depends, HTTPException, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.core.models import ensure_job_profiles_schema


async def get_job_profile_or_404(
    job_profile_id: int,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> asyncpg.Record:
    """Dependency: validates job_profile_id belongs to authenticated user."""
    await ensure_job_profiles_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profiles WHERE id = $1 AND user_id = $2",
        job_profile_id, current_user["id"]
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job profile not found",
        )
    return row
