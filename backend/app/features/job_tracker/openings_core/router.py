"""Router for job_tracker openings_core endpoints."""
import asyncpg
from fastapi import APIRouter, Depends, Query, Response, status

from app.features.core.dependencies import DbDep
from app.features.auth.utils import get_current_user
from app.features.job_tracker.openings_core import service
from app.features.job_tracker.openings_core.schemas import (
    OpeningCreate,
    OpeningListParams,
    OpeningListResponse,
    OpeningResponse,
    OpeningStatus,
    OpeningUpdate,
    StatusHistoryEntry,
    StatusTransitionRequest,
)

router = APIRouter(tags=["job-openings"])


def _row_to_response(row: asyncpg.Record) -> OpeningResponse:
    """Convert a database row to an OpeningResponse schema."""
    return OpeningResponse(**dict(row))


@router.post("/job-openings", status_code=201, response_model=OpeningResponse)
async def create_job_opening(
    data: OpeningCreate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> OpeningResponse:
    row = await service.create_opening(conn, current_user["id"], data)
    return _row_to_response(row)


@router.get("/job-openings", response_model=OpeningListResponse)
async def list_job_openings(
    status_filter: OpeningStatus | None = Query(None, alias="status"),
    company_name: str | None = Query(None),
    role_name: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    after_id: int | None = Query(None),
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> OpeningListResponse:
    params = OpeningListParams(
        status=status_filter,
        company_name=company_name,
        role_name=role_name,
        limit=limit,
        after_id=after_id,
    )
    items, has_more = await service.list_openings(conn, current_user["id"], params)
    next_cursor = items[-1]["id"] if has_more and items else None
    return OpeningListResponse(
        items=[_row_to_response(r) for r in items],
        has_more=has_more,
        next_cursor=next_cursor,
    )


@router.get("/job-openings/{opening_id}", response_model=OpeningResponse)
async def get_job_opening(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> OpeningResponse:
    row = await service.get_opening(conn, current_user["id"], opening_id)
    return _row_to_response(row)


@router.patch("/job-openings/{opening_id}", response_model=OpeningResponse)
async def update_job_opening(
    opening_id: int,
    data: OpeningUpdate,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> OpeningResponse:
    row = await service.update_opening(conn, current_user["id"], opening_id, data)
    return _row_to_response(row)


@router.delete("/job-openings/{opening_id}", status_code=204)
async def delete_job_opening(
    opening_id: int,
    confirm: bool = Query(False),
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> Response:
    await service.delete_opening(conn, current_user["id"], opening_id, confirm)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/job-openings/{opening_id}/status", response_model=OpeningResponse)
async def transition_opening_status(
    opening_id: int,
    data: StatusTransitionRequest,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> OpeningResponse:
    row = await service.transition_status(conn, current_user["id"], opening_id, data.status)
    return _row_to_response(row)


@router.get("/job-openings/{opening_id}/status-history", response_model=list[StatusHistoryEntry])
async def get_status_history(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[StatusHistoryEntry]:
    rows = await service.list_status_history(conn, current_user["id"], opening_id)
    return [StatusHistoryEntry(**dict(r)) for r in rows]
