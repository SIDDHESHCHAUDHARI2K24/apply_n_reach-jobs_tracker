"""Router for profile bootstrap and personal details endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_current_user, get_profile_or_404
from app.features.user_profile.personal import service
from app.features.user_profile.personal.schemas import (
    PersonalDetailsCreate,
    PersonalDetailsResponse,
    UserProfileCreatedResponse,
)

router = APIRouter(prefix="/profile", tags=["user-profile"])


@router.post("", response_model=UserProfileCreatedResponse, status_code=201)
async def create_profile(
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> UserProfileCreatedResponse:
    """Bootstrap a new UserProfile for the authenticated user.

    Creates the master profile record. Call this once before using any section endpoints.

    Returns:
        The newly created profile (id, user_id, created_at).

    Raises:
        HTTPException(409): If a profile already exists for this user.
        HTTPException(401): If not authenticated.
    """
    row = await service.create_profile(conn, current_user["id"])
    return UserProfileCreatedResponse(
        id=row["id"],
        user_id=row["user_id"],
        created_at=row["created_at"],
    )


@router.get("/personal", response_model=PersonalDetailsResponse)
async def get_personal(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> PersonalDetailsResponse:
    """Get personal details for the authenticated user's profile.

    Returns:
        The personal_details row.

    Raises:
        HTTPException(404): If personal details have not been set yet.
        HTTPException(401): If not authenticated.
    """
    row = await service.get_personal_details(conn, profile["id"])
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal details not found",
        )
    return PersonalDetailsResponse(
        id=row["id"],
        profile_id=row["profile_id"],
        full_name=row["full_name"],
        email=row["email"],
        linkedin_url=row["linkedin_url"],
        github_url=row["github_url"],
        portfolio_url=row["portfolio_url"],
        summary=row["summary"],
        location=row["location"],
        phone=row["phone"],
    )


@router.patch("/personal", response_model=PersonalDetailsResponse)
async def update_personal_details(
    data: PersonalDetailsCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> PersonalDetailsResponse:
    """Create or update personal details for the authenticated user's profile.

    Idempotent upsert — safe to call multiple times.

    Returns:
        The upserted personal_details row.

    Raises:
        HTTPException(404): If the profile does not exist (no POST /profile yet).
        HTTPException(401): If not authenticated.
    """
    row = await service.upsert_personal_details(conn, profile["id"], data)
    return PersonalDetailsResponse(
        id=row["id"],
        profile_id=row["profile_id"],
        full_name=row["full_name"],
        email=row["email"],
        linkedin_url=row["linkedin_url"],
        github_url=row["github_url"],
        portfolio_url=row["portfolio_url"],
        summary=row["summary"],
        location=row["location"],
        phone=row["phone"],
    )
