"""Router for profile bootstrap and personal details endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_current_user, get_profile_or_404
from app.features.user_profile.personal import service
from app.features.user_profile.personal.schemas import (
    PersonalDetailsCreate,
    PersonalDetailsResponse,
    PersonalDetailsUpdate,
    ProfileSummaryResponse,
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
    data: PersonalDetailsUpdate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> PersonalDetailsResponse:
    """Create or partially update personal details for the authenticated user's profile.

    If personal details don't exist yet and all required fields (full_name, email,
    linkedin_url) are provided, creates a new record (upsert). Otherwise, performs
    a partial update on the existing record.

    Returns:
        The upserted or updated personal_details row.

    Raises:
        HTTPException(404): If the profile or personal details do not exist.
        HTTPException(401): If not authenticated.
    """
    # Check if personal details exist
    existing = await service.get_personal_details(conn, profile["id"])
    if existing is None:
        # Try upsert if all required fields are present
        updates = data.model_dump(exclude_unset=True)
        required = {"full_name", "email", "linkedin_url"}
        if required.issubset(updates.keys()):
            # Build a PersonalDetailsCreate from the provided fields
            create_data = PersonalDetailsCreate(
                full_name=data.full_name,
                email=data.email,
                linkedin_url=data.linkedin_url,
                github_url=data.github_url,
                portfolio_url=data.portfolio_url,
                summary=data.summary,
                location=data.location,
                phone=data.phone,
            )
            row = await service.upsert_personal_details(conn, profile["id"], create_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal details not found. Create them first by providing full_name, email, and linkedin_url.",
            )
    else:
        row = await service.update_personal_details(conn, profile["id"], data)
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


@router.get("/summary", response_model=ProfileSummaryResponse)
async def get_profile_summary(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ProfileSummaryResponse:
    """Get a summary of all profile sections for the authenticated user.

    Returns:
        Counts/existence flags for all profile sections.

    Raises:
        HTTPException(401): If not authenticated.
    """
    row = await service.get_profile_summary(conn, profile["id"])
    return ProfileSummaryResponse(
        personal_details_exists=row["personal_details_exists"],
        education_count=row["education_count"],
        experience_count=row["experience_count"],
        projects_count=row["projects_count"],
        research_count=row["research_count"],
        certifications_count=row["certifications_count"],
        skills_count=row["skills_count"],
    )
