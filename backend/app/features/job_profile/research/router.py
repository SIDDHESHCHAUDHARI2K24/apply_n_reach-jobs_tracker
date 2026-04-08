"""Router for job profile research CRUD endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_profile.dependencies import get_job_profile_or_404
from app.features.job_profile.research import service
from app.features.job_profile.research.schemas import (
    JPResearchCreate,
    JPResearchUpdate,
    JPResearchResponse,
)
from app.features.job_profile.import_schemas import ImportRequest, ImportResult

router = APIRouter(prefix="/job-profiles/{job_profile_id}/research", tags=["job-profile"])


def _row_to_response(row: asyncpg.Record) -> JPResearchResponse:
    """Convert an asyncpg Record to JPResearchResponse."""
    return JPResearchResponse(**dict(row))


@router.get("", response_model=list[JPResearchResponse])
async def list_researches(
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all research entries for a job profile."""
    rows = await service.list_researches(conn, job_profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{research_id}", response_model=JPResearchResponse)
async def get_research(
    research_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPResearchResponse:
    """Get a single research entry by id."""
    row = await service.get_research(conn, job_profile["id"], research_id)
    return _row_to_response(row)


@router.post("", response_model=JPResearchResponse, status_code=201)
async def add_research(
    data: JPResearchCreate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPResearchResponse:
    """Create a new research entry for a job profile."""
    row = await service.add_research(conn, job_profile["id"], data)
    return _row_to_response(row)


@router.patch("/{research_id}", response_model=JPResearchResponse)
async def update_research(
    research_id: int,
    data: JPResearchUpdate,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> JPResearchResponse:
    """Partially update an existing research entry."""
    row = await service.update_research(conn, job_profile["id"], research_id, data)
    return _row_to_response(row)


@router.delete("/{research_id}", status_code=204)
async def delete_research(
    research_id: int,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a research entry."""
    await service.delete_research(conn, job_profile["id"], research_id)


@router.post("/import", response_model=ImportResult)
async def import_researches(
    data: ImportRequest,
    job_profile: asyncpg.Record = Depends(get_job_profile_or_404),
    current_user: asyncpg.Record = Depends(get_current_user),
    conn: asyncpg.Connection = DbDep,
) -> ImportResult:
    """Import research entries from the user's master profile."""
    return await service.import_researches_from_profile(
        conn, job_profile["id"], current_user["id"], data.source_ids
    )
