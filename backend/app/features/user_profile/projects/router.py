"""Router for projects CRUD endpoints."""
import json
import asyncpg
from fastapi import APIRouter, Depends, status

from app.features.core.dependencies import DbDep
from app.features.user_profile.dependencies import get_profile_or_404
from app.features.user_profile.projects import service
from app.features.user_profile.projects.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/profile/projects", tags=["user-profile"])


def _row_to_response(row) -> ProjectResponse:
    """Convert an asyncpg Record or dict to ProjectResponse, deserializing JSONB fields."""
    data = dict(row)
    for field in ("reference_links", "technologies"):
        if isinstance(data.get(field), str):
            data[field] = json.loads(data[field])
    return ProjectResponse(**data)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> list:
    """List all project entries for the authenticated user's profile."""
    rows = await service.list_projects(conn, profile["id"])
    return [_row_to_response(row) for row in rows]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ProjectResponse:
    """Get a single project entry by id."""
    row = await service.get_project(conn, profile["id"], project_id)
    return _row_to_response(row)


@router.post("", response_model=ProjectResponse, status_code=201)
async def add_project(
    data: ProjectCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ProjectResponse:
    """Create a new project entry."""
    row = await service.add_project(conn, profile["id"], data)
    return _row_to_response(row)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectCreate,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> ProjectResponse:
    """Update an existing project entry."""
    row = await service.update_project(conn, profile["id"], project_id, data)
    return _row_to_response(row)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    profile: asyncpg.Record = Depends(get_profile_or_404),
    conn: asyncpg.Connection = DbDep,
) -> None:
    """Delete a project entry."""
    await service.delete_project(conn, profile["id"], project_id)
