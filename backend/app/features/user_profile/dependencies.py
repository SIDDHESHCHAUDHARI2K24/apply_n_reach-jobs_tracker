"""Shared dependency callables for the user_profile feature."""
import asyncpg
from fastapi import Depends, HTTPException, status

from app.features.auth.utils import get_current_user
from app.features.core.dependencies import DbDep
from app.features.user_profile.personal import models as personal_models


async def get_profile_or_404(
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> asyncpg.Record:
    """Fetch the UserProfile for the current user, or raise 404.

    Raises:
        HTTPException(404): if no profile exists for the authenticated user.
            This typically means the user hasn't called POST /profile yet.
    """
    await personal_models.ensure_profile_schema(conn)
    profile = await conn.fetchrow(
        "SELECT id, user_id, created_at, updated_at FROM user_profiles WHERE user_id = $1",
        current_user["id"],
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create a profile first via POST /profile",
        )
    return profile


# Re-export for convenience
from app.features.auth.utils import get_current_user as get_current_user  # noqa: F401
