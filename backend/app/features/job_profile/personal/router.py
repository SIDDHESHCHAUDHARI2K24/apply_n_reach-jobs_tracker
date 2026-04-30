"""Router for job profile personal details endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.personal import service
from app.features.job_profile.personal.schemas import (
    JPPersonalDetailsCreate,
    JPPersonalDetailsResponse,
    JPPersonalDetailsUpdate,
)

router = APIRouter(prefix="/job-profiles/{job_profile_id}/personal", tags=["job-profile"])


def _row_to_response(row: asyncpg.Record) -> JPPersonalDetailsResponse:
    """Map the DB row explicitly so parity fields are preserved in responses."""
    return JPPersonalDetailsResponse(
        id=row["id"],
        job_profile_id=row["job_profile_id"],
        source_personal_id=row["source_personal_id"],
        full_name=row["full_name"],
        email=row["email"],
        linkedin_url=row["linkedin_url"],
        github_url=row["github_url"],
        portfolio_url=row["portfolio_url"],
        summary=row["summary"],
        location=row["location"],
        phone=row["phone"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("", response_model=JPPersonalDetailsResponse)
async def get_personal(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPPersonalDetailsResponse:
    """Get personal details for a job profile."""
    row = await service.get_personal_details(conn, job_profile["id"])
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal details not found",
        )
    return _row_to_response(row)


@router.patch("", response_model=JPPersonalDetailsResponse)
async def update_personal(
    data: JPPersonalDetailsUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPPersonalDetailsResponse:
    """Create or partially update personal details for a job profile."""
    existing = await service.get_personal_details(conn, job_profile["id"])
    if existing is None:
        updates = data.model_dump(exclude_unset=True)
        required = {"full_name", "email", "linkedin_url"}
        if required.issubset(updates.keys()):
            create_data = JPPersonalDetailsCreate(
                full_name=data.full_name,
                email=data.email,
                linkedin_url=data.linkedin_url,
                github_url=data.github_url,
                portfolio_url=data.portfolio_url,
                summary=data.summary,
                location=data.location,
                phone=data.phone,
            )
            row = await service.upsert_personal_details(conn, job_profile["id"], create_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal details not found. Create them by providing full_name, email, and linkedin_url.",
            )
    else:
        row = await service.update_personal_details(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.post("/import", response_model=JPPersonalDetailsResponse, status_code=200)
async def import_personal(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> JPPersonalDetailsResponse:
    """Import personal details from the user's master profile into this job profile."""
    row = await service.import_personal_from_profile(conn, job_profile["id"], current_user["id"])
    return _row_to_response(row)
