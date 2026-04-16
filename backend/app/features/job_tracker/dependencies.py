"""Shared FastAPI dependencies for job_tracker feature."""
import asyncpg
from fastapi import Depends, HTTPException, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user


async def get_opening_or_404(
    opening_id: int,
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> asyncpg.Record:
    """Dependency: validates opening_id belongs to the authenticated user."""
    row = await conn.fetchrow(
        "SELECT * FROM job_openings WHERE id = $1 AND user_id = $2",
        opening_id, current_user["id"]
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job opening not found",
        )
    return row
