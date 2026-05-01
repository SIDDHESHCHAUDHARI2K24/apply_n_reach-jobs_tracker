"""Router for LinkedIn profile import."""
import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.features.auth.utils import get_current_user
from app.features.core.dependencies import DbDep
from app.features.user_profile.linkedin_import.errors import LinkedInImportAppError
from app.features.user_profile.linkedin_import.schemas import (
    LinkedInImportRequest,
    LinkedInImportResponse,
)
from app.features.user_profile.linkedin_import.scraper import scrape_linkedin_profile
from app.features.user_profile.linkedin_import.mapping_chain import map_linkedin_to_profile
from app.features.user_profile.linkedin_import.service import replace_profile_from_linkedin

router = APIRouter(tags=["linkedin-import"])


@router.post(
    "/profile/import/linkedin",
    status_code=200,
    response_model=LinkedInImportResponse,
    responses={
        404: {"description": "User profile not found"},
        422: {"description": "Invalid LinkedIn URL or unprocessable profile data"},
        424: {"description": "LLM mapping failed (failed dependency)"},
        502: {"description": "Apify upstream error (bad credentials, quota, empty result)"},
        503: {"description": "Service unavailable (missing API token, transient upstream)"},
    },
)
async def import_linkedin_profile(
    body: LinkedInImportRequest,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> LinkedInImportResponse:
    """Import a LinkedIn profile, replacing all user_profile sections."""
    profile = await conn.fetchrow(
        "SELECT id FROM user_profiles WHERE user_id = $1",
        current_user["id"],
    )
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found. Create a profile first.")

    try:
        raw_data = await scrape_linkedin_profile(body.linkedin_url)
    except LinkedInImportAppError as e:
        raise HTTPException(status_code=e.http_status, detail=e.to_http_detail())

    try:
        mapped = await map_linkedin_to_profile(raw_data)
    except LinkedInImportAppError as e:
        raise HTTPException(status_code=e.http_status, detail=e.to_http_detail())

    if mapped.personal:
        mapped.personal.linkedin_url = mapped.personal.linkedin_url or body.linkedin_url

    counts = await replace_profile_from_linkedin(conn, profile["id"], mapped)

    return LinkedInImportResponse(
        message="LinkedIn profile imported successfully",
        sections_imported=counts,
    )
