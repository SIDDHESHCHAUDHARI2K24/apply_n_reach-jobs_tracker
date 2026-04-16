"""Router for job opening resume research section endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.opening_resume.research import service
from app.features.job_tracker.opening_resume.research.schemas import (
    ResearchCreate,
    ResearchResponse,
    ResearchUpdate,
)

router = APIRouter(tags=["job-opening-resume"])


@router.get(
    "/job-openings/{opening_id}/resume/research",
    response_model=list[ResearchResponse],
)
async def list_research(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[ResearchResponse]:
    rows = await service.list_entries(conn, current_user["id"], opening_id)
    return [ResearchResponse(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/resume/research",
    response_model=ResearchResponse,
    status_code=201,
)
async def create_research(
    opening_id: int,
    data: ResearchCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ResearchResponse:
    row = await service.create_entry(conn, current_user["id"], opening_id, data)
    return ResearchResponse(**dict(row))


@router.get(
    "/job-openings/{opening_id}/resume/research/{entry_id}",
    response_model=ResearchResponse,
)
async def get_research(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ResearchResponse:
    row = await service.get_entry(conn, current_user["id"], opening_id, entry_id)
    return ResearchResponse(**dict(row))


@router.patch(
    "/job-openings/{opening_id}/resume/research/{entry_id}",
    response_model=ResearchResponse,
)
async def update_research(
    opening_id: int,
    entry_id: int,
    data: ResearchUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> ResearchResponse:
    row = await service.update_entry(conn, current_user["id"], opening_id, entry_id, data)
    return ResearchResponse(**dict(row))


@router.delete(
    "/job-openings/{opening_id}/resume/research/{entry_id}",
    status_code=204,
)
async def delete_research(
    opening_id: int,
    entry_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_entry(conn, current_user["id"], opening_id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
