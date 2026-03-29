"""Router for research CRUD endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.research import service
from app.features.user_profile.research.schemas import ResearchCreate, ResearchResponse

router = APIRouter(prefix="/profile/research", tags=["user-profile"])


def _row_to_response(row: asyncpg.Record) -> ResearchResponse:
    """Convert an asyncpg Record to ResearchResponse."""
    return ResearchResponse(**dict(row))


@router.get("", response_model=list[ResearchResponse])
async def list_researches(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all research entries for the authenticated user's profile."""
    rows = await service.list_researches(conn, profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{research_id}", response_model=ResearchResponse)
async def get_research(
    research_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ResearchResponse:
    """Get a single research entry by id."""
    row = await service.get_research(conn, profile["id"], research_id)
    return _row_to_response(row)


@router.post("", response_model=ResearchResponse, status_code=201)
async def add_research(
    data: ResearchCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ResearchResponse:
    """Create a new research entry."""
    row = await service.add_research(conn, profile["id"], data)
    return _row_to_response(row)


@router.patch("/{research_id}", response_model=ResearchResponse)
async def update_research(
    research_id: int,
    data: ResearchCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ResearchResponse:
    """Update an existing research entry."""
    row = await service.update_research(conn, profile["id"], research_id, data)
    return _row_to_response(row)


@router.delete("/{research_id}", status_code=204)
async def delete_research(
    research_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a research entry."""
    await service.delete_research(conn, profile["id"], research_id)
