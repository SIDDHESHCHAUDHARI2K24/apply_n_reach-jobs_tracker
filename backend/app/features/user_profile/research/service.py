"""Service functions for the research sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.core.query_helpers import build_partial_update_query
from app.features.user_profile.research import models
from app.features.user_profile.research.schemas import ResearchCreate, ResearchUpdate


async def list_researches(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all research entries for a profile, ordered by created_at DESC."""
    await models.ensure_research_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, paper_name, publication_link, description, "
        "created_at, updated_at FROM researches WHERE profile_id = $1 "
        "ORDER BY created_at DESC",
        profile_id,
    )


async def get_research(
    conn: asyncpg.Connection, profile_id: int, research_id: int
) -> asyncpg.Record:
    """Fetch a single research entry, verifying ownership."""
    await models.ensure_research_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, paper_name, publication_link, description, "
        "created_at, updated_at FROM researches WHERE id = $1 AND profile_id = $2",
        research_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    return row


async def add_research(
    conn: asyncpg.Connection, profile_id: int, data: ResearchCreate
) -> asyncpg.Record:
    """Create a new research entry for a profile."""
    await models.ensure_research_schema(conn)
    return await conn.fetchrow(
        "INSERT INTO researches (profile_id, paper_name, publication_link, description) "
        "VALUES ($1, $2, $3, $4) "
        "RETURNING id, profile_id, paper_name, publication_link, description, "
        "created_at, updated_at",
        profile_id,
        data.paper_name,
        data.publication_link,
        data.description,
    )


async def update_research(
    conn: asyncpg.Connection, profile_id: int, research_id: int, data: ResearchUpdate
) -> asyncpg.Record:
    """Partially update an existing research entry, verifying ownership."""
    await models.ensure_research_schema(conn)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, params = build_partial_update_query(
        "researches",
        {"id": research_id, "profile_id": profile_id},
        updates,
    )
    row = await conn.fetchrow(query, *params)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
    return row


async def delete_research(
    conn: asyncpg.Connection, profile_id: int, research_id: int
) -> None:
    """Delete a research entry, verifying ownership."""
    await models.ensure_research_schema(conn)
    result = await conn.execute(
        "DELETE FROM researches WHERE id = $1 AND profile_id = $2",
        research_id,
        profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research entry not found")
