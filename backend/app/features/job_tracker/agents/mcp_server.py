"""MCP-style tool server for the resume agent.

Wraps opening_resume services as LangChain StructuredTools that the
LangGraph agent can call. Tools receive (user_id, conn) from a context
object injected at runtime.
"""
from __future__ import annotations

import contextvars
import io
import json
from dataclasses import dataclass
from typing import Any

import asyncpg
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


@dataclass
class AgentContext:
    """Runtime context injected into every tool call."""
    user_id: int
    conn: asyncpg.Connection
    opening_id: int


# Per-task context: each asyncio Task (i.e. each background run) gets its own copy.
_context_var: contextvars.ContextVar[AgentContext | None] = contextvars.ContextVar(
    "agent_context", default=None
)


def set_context(ctx: AgentContext) -> None:
    _context_var.set(ctx)


def get_context() -> AgentContext:
    ctx = _context_var.get()
    if ctx is None:
        raise RuntimeError("Agent context not initialized")
    return ctx


def _record_to_dict(row: asyncpg.Record | None) -> dict | None:
    if row is None:
        return None
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith(("[", "{")):
                try:
                    d[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    pass
    return d


def _records_to_list(rows: list[asyncpg.Record]) -> list[dict]:
    return [_record_to_dict(r) for r in rows]


# ──── Tool input schemas ────

class SectionListInput(BaseModel):
    """Input for listing section entries."""
    pass  # opening_id comes from context


class EntryIdInput(BaseModel):
    """Input for operations on a single entry."""
    entry_id: int = Field(description="The ID of the entry to operate on")


class CreateSnapshotInput(BaseModel):
    """Input for creating an opening resume snapshot."""
    source_job_profile_id: int = Field(description="The job profile ID to snapshot from")


# Section-specific create/update schemas
class EducationData(BaseModel):
    institution: str = ""
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    grade: str | None = None
    description: str | None = None
    display_order: int = 0

class ExperienceData(BaseModel):
    company: str = ""
    title: str = ""
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    display_order: int = 0

class ProjectData(BaseModel):
    name: str = ""
    description: str | None = None
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    technologies: list[str] | None = None
    display_order: int = 0

class ResearchData(BaseModel):
    title: str = ""
    publication: str | None = None
    published_date: str | None = None
    url: str | None = None
    description: str | None = None
    display_order: int = 0

class CertificationData(BaseModel):
    name: str = ""
    issuer: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    url: str | None = None
    display_order: int = 0

class SkillData(BaseModel):
    category: str = ""
    name: str = ""
    proficiency_level: str | None = None
    display_order: int = 0

class PersonalData(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    summary: str | None = None

class UpdateEntryInput(BaseModel):
    entry_id: int = Field(description="The ID of the entry to update")

class EducationUpdateInput(UpdateEntryInput, EducationData):
    pass

class ExperienceUpdateInput(UpdateEntryInput, ExperienceData):
    pass

class ProjectUpdateInput(UpdateEntryInput, ProjectData):
    pass

class ResearchUpdateInput(UpdateEntryInput, ResearchData):
    pass

class CertificationUpdateInput(UpdateEntryInput, CertificationData):
    pass

class SkillUpdateInput(UpdateEntryInput, SkillData):
    pass

class AgentStateInput(BaseModel):
    """Input for updating agent state on the opening."""
    current_node: str | None = None
    status: str | None = None
    message: str | None = None


# ──── Tool implementations ────

async def _list_education(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.education.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _list_experience(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.experience.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _list_projects(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.projects.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _list_research(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.research.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _list_certifications(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.certifications.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _list_skills(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.skills.service import list_entries
    rows = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_records_to_list(rows), default=str)

async def _get_personal(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.personal.service import get_personal
    row = await get_personal(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_personal(data: PersonalData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.personal.service import upsert_personal
    from app.features.job_tracker.opening_resume.personal.schemas import PersonalUpdate
    update = PersonalUpdate(**data.model_dump())
    row = await upsert_personal(ctx.conn, ctx.user_id, ctx.opening_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _create_education(data: EducationData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.education.service import create_entry
    from app.features.job_tracker.opening_resume.education.schemas import EducationCreate
    create = EducationCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_education(data: EducationUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.education.service import update_entry
    from app.features.job_tracker.opening_resume.education.schemas import EducationUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = EducationUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_education(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.education.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_experience(data: ExperienceData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.experience.service import create_entry
    from app.features.job_tracker.opening_resume.experience.schemas import ExperienceCreate
    create = ExperienceCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_experience(data: ExperienceUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.experience.service import update_entry
    from app.features.job_tracker.opening_resume.experience.schemas import ExperienceUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = ExperienceUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_experience(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.experience.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_project(data: ProjectData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.projects.service import create_entry
    from app.features.job_tracker.opening_resume.projects.schemas import ProjectCreate
    create = ProjectCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_project(data: ProjectUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.projects.service import update_entry
    from app.features.job_tracker.opening_resume.projects.schemas import ProjectUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = ProjectUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_project(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.projects.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_research(data: ResearchData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.research.service import create_entry
    from app.features.job_tracker.opening_resume.research.schemas import ResearchCreate
    create = ResearchCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_research(data: ResearchUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.research.service import update_entry
    from app.features.job_tracker.opening_resume.research.schemas import ResearchUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = ResearchUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_research(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.research.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_certification(data: CertificationData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.certifications.service import create_entry
    from app.features.job_tracker.opening_resume.certifications.schemas import CertificationCreate
    create = CertificationCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_certification(data: CertificationUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.certifications.service import update_entry
    from app.features.job_tracker.opening_resume.certifications.schemas import CertificationUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = CertificationUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_certification(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.certifications.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_skill(data: SkillData) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.skills.service import create_entry
    from app.features.job_tracker.opening_resume.skills.schemas import SkillCreate
    create = SkillCreate(**data.model_dump())
    row = await create_entry(ctx.conn, ctx.user_id, ctx.opening_id, create)
    return json.dumps(_record_to_dict(row), default=str)

async def _update_skill(data: SkillUpdateInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.skills.service import update_entry
    from app.features.job_tracker.opening_resume.skills.schemas import SkillUpdate
    fields = data.model_dump(exclude={"entry_id"})
    update = SkillUpdate(**fields)
    row = await update_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id, update)
    return json.dumps(_record_to_dict(row), default=str)

async def _delete_skill(data: EntryIdInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.skills.service import delete_entry
    await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, data.entry_id)
    return json.dumps({"deleted": True})

async def _create_snapshot(data: CreateSnapshotInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.service import create_opening_resume
    row = await create_opening_resume(ctx.conn, ctx.user_id, ctx.opening_id, data.source_job_profile_id)
    return json.dumps(_record_to_dict(row), default=str)

async def _get_extracted_details(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_ingestion.service import get_latest_extracted_details
    row = await get_latest_extracted_details(ctx.conn, ctx.user_id, ctx.opening_id)
    return json.dumps(_record_to_dict(row), default=str)

async def _render_resume_pdf(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.latex_resume.service import render_resume
    result = await render_resume(ctx.conn, ctx.user_id, ctx.opening_id, layout=None)
    return json.dumps(result, default=str)

async def _get_resume_pdf_tool(_: SectionListInput) -> str:
    ctx = get_context()
    from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf
    result = await get_resume_pdf(ctx.conn, ctx.user_id, ctx.opening_id)
    if result is None:
        return json.dumps({"error": "No rendered PDF found"})
    pdf_bytes, filename = result
    return json.dumps({"filename": filename, "size_bytes": len(pdf_bytes)})

async def _count_pdf_pages(_: SectionListInput) -> str:
    """Count pages of the most recently rendered PDF."""
    ctx = get_context()
    from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf
    result = await get_resume_pdf(ctx.conn, ctx.user_id, ctx.opening_id)
    if result is None:
        return json.dumps({"error": "No rendered PDF found"})
    pdf_bytes, _ = result
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return json.dumps({"page_count": len(reader.pages)})

async def _update_agent_state(data: AgentStateInput) -> str:
    ctx = get_context()
    updates = {}
    if data.current_node is not None:
        updates["current_node"] = data.current_node
    if data.status is not None:
        updates["status"] = data.status
    if data.message is not None:
        updates["message"] = data.message

    # Update the agent_state JSONB column on job_openings
    current = await ctx.conn.fetchval(
        "SELECT agent_state FROM job_openings WHERE id=$1", ctx.opening_id
    )
    state = json.loads(current) if isinstance(current, str) else (current or {})
    state.update(updates)
    await ctx.conn.execute(
        "UPDATE job_openings SET agent_state=$1::jsonb WHERE id=$2",
        json.dumps(state), ctx.opening_id,
    )
    return json.dumps(state)


def get_agent_tools() -> list[StructuredTool]:
    """Return all agent tools as LangChain StructuredTools."""
    tools = [
        StructuredTool.from_function(coroutine=_list_education, name="list_education",
            description="List all education entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_list_experience, name="list_experience",
            description="List all experience entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_list_projects, name="list_projects",
            description="List all project entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_list_research, name="list_research",
            description="List all research entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_list_certifications, name="list_certifications",
            description="List all certification entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_list_skills, name="list_skills",
            description="List all skill entries on the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_get_personal, name="get_personal",
            description="Get the personal/contact section of the opening resume", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_update_personal, name="update_personal",
            description="Update the personal/contact section (full_name, email, phone, location, urls, summary)", args_schema=PersonalData),

        StructuredTool.from_function(coroutine=_create_education, name="create_education",
            description="Create a new education entry", args_schema=EducationData),
        StructuredTool.from_function(coroutine=_update_education, name="update_education",
            description="Update an existing education entry by ID", args_schema=EducationUpdateInput),
        StructuredTool.from_function(coroutine=_delete_education, name="delete_education",
            description="Delete an education entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_experience, name="create_experience",
            description="Create a new experience entry", args_schema=ExperienceData),
        StructuredTool.from_function(coroutine=_update_experience, name="update_experience",
            description="Update an existing experience entry by ID", args_schema=ExperienceUpdateInput),
        StructuredTool.from_function(coroutine=_delete_experience, name="delete_experience",
            description="Delete an experience entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_project, name="create_project",
            description="Create a new project entry", args_schema=ProjectData),
        StructuredTool.from_function(coroutine=_update_project, name="update_project",
            description="Update an existing project entry by ID", args_schema=ProjectUpdateInput),
        StructuredTool.from_function(coroutine=_delete_project, name="delete_project",
            description="Delete a project entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_research, name="create_research",
            description="Create a new research entry", args_schema=ResearchData),
        StructuredTool.from_function(coroutine=_update_research, name="update_research",
            description="Update an existing research entry by ID", args_schema=ResearchUpdateInput),
        StructuredTool.from_function(coroutine=_delete_research, name="delete_research",
            description="Delete a research entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_certification, name="create_certification",
            description="Create a new certification entry", args_schema=CertificationData),
        StructuredTool.from_function(coroutine=_update_certification, name="update_certification",
            description="Update an existing certification entry by ID", args_schema=CertificationUpdateInput),
        StructuredTool.from_function(coroutine=_delete_certification, name="delete_certification",
            description="Delete a certification entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_skill, name="create_skill",
            description="Create a new skill entry", args_schema=SkillData),
        StructuredTool.from_function(coroutine=_update_skill, name="update_skill",
            description="Update an existing skill entry by ID", args_schema=SkillUpdateInput),
        StructuredTool.from_function(coroutine=_delete_skill, name="delete_skill",
            description="Delete a skill entry by ID", args_schema=EntryIdInput),

        StructuredTool.from_function(coroutine=_create_snapshot, name="create_opening_resume",
            description="Create an opening resume by snapshotting a job profile", args_schema=CreateSnapshotInput),
        StructuredTool.from_function(coroutine=_get_extracted_details, name="get_extracted_details",
            description="Get the latest extracted job details for this opening", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_render_resume_pdf, name="render_resume_pdf",
            description="Render the opening resume as a LaTeX PDF", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_get_resume_pdf_tool, name="get_resume_pdf",
            description="Get metadata about the rendered PDF", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_count_pdf_pages, name="count_pdf_pages",
            description="Count the number of pages in the rendered PDF", args_schema=SectionListInput),
        StructuredTool.from_function(coroutine=_update_agent_state, name="update_agent_state",
            description="Update the agent state (current_node, status, message) on the opening", args_schema=AgentStateInput),
    ]
    return tools
