"""Service functions for job_tracker openings_core sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.job_tracker.openings_core.schemas import (
    OpeningCreate,
    OpeningListParams,
    OpeningStatus,
    OpeningUpdate,
)

TRANSITION_MATRIX: dict[OpeningStatus, set[OpeningStatus]] = {
    OpeningStatus.Interested: {
        OpeningStatus.Applied,
        OpeningStatus.Withdrawn,
        OpeningStatus.Rejected,
    },
    OpeningStatus.Applied: {
        OpeningStatus.Interviewing,
        OpeningStatus.Withdrawn,
        OpeningStatus.Rejected,
    },
    OpeningStatus.Interviewing: {
        OpeningStatus.Offer,
        OpeningStatus.Withdrawn,
        OpeningStatus.Rejected,
    },
    OpeningStatus.Offer: {
        OpeningStatus.Withdrawn,
        OpeningStatus.Rejected,
    },
    OpeningStatus.Withdrawn: set(),
    OpeningStatus.Rejected: set(),
}


async def create_opening(
    conn: asyncpg.Connection,
    user_id: int,
    data: OpeningCreate,
) -> asyncpg.Record:
    """Create a new job opening and insert the initial status history entry."""
    row = await conn.fetchrow(
        """
        INSERT INTO job_openings (user_id, source_url, company_name, role_name, current_status, notes)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, user_id, job_profile_id, source_url, company_name, role_name,
                  current_status, notes, created_at, updated_at
        """,
        user_id,
        data.source_url,
        data.company_name,
        data.role_name,
        data.initial_status.value,
        data.notes,
    )
    await conn.execute(
        """
        INSERT INTO job_opening_status_history
            (opening_id, from_status, to_status, changed_by_user_id)
        VALUES ($1, NULL, $2, $3)
        """,
        row["id"],
        data.initial_status.value,
        user_id,
    )
    return row


async def get_opening(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> asyncpg.Record:
    """Fetch a single opening, verifying ownership."""
    row = await conn.fetchrow(
        """
        SELECT id, user_id, job_profile_id, source_url, company_name, role_name,
               current_status, notes, created_at, updated_at
        FROM job_openings
        WHERE id = $1 AND user_id = $2
        """,
        opening_id,
        user_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job opening not found",
        )
    return row


async def list_openings(
    conn: asyncpg.Connection,
    user_id: int,
    params: OpeningListParams,
) -> tuple[list[asyncpg.Record], bool]:
    """List openings for a user with optional filters and cursor pagination."""
    conditions = ["user_id = $1"]
    args: list = [user_id]

    if params.status is not None:
        args.append(params.status.value)
        conditions.append(f"current_status = ${len(args)}")

    if params.company_name is not None:
        args.append(f"%{params.company_name}%")
        conditions.append(f"company_name ILIKE ${len(args)}")

    if params.role_name is not None:
        args.append(f"%{params.role_name}%")
        conditions.append(f"role_name ILIKE ${len(args)}")

    if params.after_id is not None:
        args.append(params.after_id)
        conditions.append(f"id > ${len(args)}")

    where_clause = " AND ".join(conditions)
    fetch_limit = params.limit + 1
    args.append(fetch_limit)

    query = (
        f"SELECT id, user_id, job_profile_id, source_url, company_name, role_name, "
        f"current_status, notes, created_at, updated_at "
        f"FROM job_openings "
        f"WHERE {where_clause} "
        f"ORDER BY id ASC "
        f"LIMIT ${len(args)}"
    )

    rows = await conn.fetch(query, *args)
    has_more = len(rows) > params.limit
    return list(rows[: params.limit]), has_more


async def update_opening(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    data: OpeningUpdate,
) -> asyncpg.Record:
    """Partially update a job opening."""
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = build_partial_update_query(
        "job_openings",
        {"id": opening_id, "user_id": user_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job opening not found",
        )
    return row


async def delete_opening(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    confirm: bool,
) -> None:
    """Delete a job opening. Requires confirm=True."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="confirm=true required to delete",
        )
    result = await conn.execute(
        "DELETE FROM job_openings WHERE id = $1 AND user_id = $2",
        opening_id,
        user_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job opening not found",
        )


async def transition_status(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    to_status: OpeningStatus,
) -> asyncpg.Record:
    """Transition a job opening to a new status, enforcing the transition matrix."""
    opening = await get_opening(conn, user_id, opening_id)
    current_status = OpeningStatus(opening["current_status"])

    allowed = TRANSITION_MATRIX.get(current_status, set())
    if to_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status.value} to {to_status.value}",
        )

    row = await conn.fetchrow(
        """
        UPDATE job_openings
        SET current_status = $1, updated_at = NOW()
        WHERE id = $2 AND user_id = $3
        RETURNING id, user_id, job_profile_id, source_url, company_name, role_name,
                  current_status, notes, created_at, updated_at
        """,
        to_status.value,
        opening_id,
        user_id,
    )
    await conn.execute(
        """
        INSERT INTO job_opening_status_history
            (opening_id, from_status, to_status, changed_by_user_id)
        VALUES ($1, $2, $3, $4)
        """,
        opening_id,
        current_status.value,
        to_status.value,
        user_id,
    )
    return row


async def list_status_history(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> list[asyncpg.Record]:
    """Return all status history entries for an opening, ordered by changed_at ASC."""
    await get_opening(conn, user_id, opening_id)
    return await conn.fetch(
        """
        SELECT id, opening_id, from_status, to_status, changed_at, changed_by_user_id
        FROM job_opening_status_history
        WHERE opening_id = $1
        ORDER BY changed_at ASC
        """,
        opening_id,
    )
