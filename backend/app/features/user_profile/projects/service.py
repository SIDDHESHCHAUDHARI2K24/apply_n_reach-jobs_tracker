"""Service functions for the projects sub-feature."""
import json
import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.projects import models
from app.features.user_profile.projects.schemas import ProjectCreate


async def list_projects(conn: asyncpg.Connection, profile_id: int) -> list[asyncpg.Record]:
    """List all project entries for a profile, ordered by start_month_year DESC."""
    await models.ensure_projects_schema(conn)
    return await conn.fetch(
        "SELECT id, profile_id, project_name, description, technologies, "
        "start_month_year, end_month_year, reference_links, "
        "created_at, updated_at FROM projects WHERE profile_id = $1 "
        "ORDER BY start_month_year DESC",
        profile_id,
    )


async def get_project(
    conn: asyncpg.Connection, profile_id: int, project_id: int
) -> asyncpg.Record:
    """Fetch a single project entry, verifying ownership."""
    await models.ensure_projects_schema(conn)
    row = await conn.fetchrow(
        "SELECT id, profile_id, project_name, description, technologies, "
        "start_month_year, end_month_year, reference_links, "
        "created_at, updated_at FROM projects WHERE id = $1 AND profile_id = $2",
        project_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found")
    return row


async def add_project(
    conn: asyncpg.Connection, profile_id: int, data: ProjectCreate
) -> asyncpg.Record:
    """Create a new project entry for a profile."""
    await models.ensure_projects_schema(conn)
    row = await conn.fetchrow(
        "INSERT INTO projects (profile_id, project_name, description, technologies, "
        "start_month_year, end_month_year, reference_links) "
        "VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7::jsonb) "
        "RETURNING id, profile_id, project_name, description, technologies, "
        "start_month_year, end_month_year, reference_links, "
        "created_at, updated_at",
        profile_id,
        data.project_name,
        data.description,
        json.dumps(data.technologies),
        data.start_month_year,
        data.end_month_year,
        json.dumps(data.reference_links),
    )
    technologies = json.loads(row["technologies"]) if isinstance(row["technologies"], str) else row["technologies"]
    reference_links = json.loads(row["reference_links"]) if isinstance(row["reference_links"], str) else row["reference_links"]
    return {**dict(row), "technologies": technologies, "reference_links": reference_links}


async def update_project(
    conn: asyncpg.Connection, profile_id: int, project_id: int, data: ProjectCreate
) -> asyncpg.Record:
    """Update an existing project entry, verifying ownership."""
    await models.ensure_projects_schema(conn)
    row = await conn.fetchrow(
        "UPDATE projects SET project_name=$1, description=$2, technologies=$3::jsonb, "
        "start_month_year=$4, end_month_year=$5, reference_links=$6::jsonb, "
        "updated_at=NOW() "
        "WHERE id=$7 AND profile_id=$8 "
        "RETURNING id, profile_id, project_name, description, technologies, "
        "start_month_year, end_month_year, reference_links, "
        "created_at, updated_at",
        data.project_name,
        data.description,
        json.dumps(data.technologies),
        data.start_month_year,
        data.end_month_year,
        json.dumps(data.reference_links),
        project_id,
        profile_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found")
    technologies = json.loads(row["technologies"]) if isinstance(row["technologies"], str) else row["technologies"]
    reference_links = json.loads(row["reference_links"]) if isinstance(row["reference_links"], str) else row["reference_links"]
    return {**dict(row), "technologies": technologies, "reference_links": reference_links}


async def delete_project(
    conn: asyncpg.Connection, profile_id: int, project_id: int
) -> None:
    """Delete a project entry, verifying ownership."""
    await models.ensure_projects_schema(conn)
    result = await conn.execute(
        "DELETE FROM projects WHERE id = $1 AND profile_id = $2",
        project_id,
        profile_id,
    )
    affected = int(result.split()[-1])
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found")
