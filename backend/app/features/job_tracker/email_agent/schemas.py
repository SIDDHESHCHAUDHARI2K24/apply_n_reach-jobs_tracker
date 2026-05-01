"""Pydantic schemas for the email agent router."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.features.core.base_model import BaseSchema


class EmailAgentStartRequest(BaseSchema):
    """Request body for starting an email agent run."""
    recipient_type: str = "recruiter"
    # Override JD/resume text (optional; falls back to opening's extracted details)
    raw_jd: str | None = None
    raw_resume: str | None = None


class EmailAgentRunResponse(BaseSchema):
    """Response for POST /run — returns 202 with the new run ID."""
    run_id: int
    opening_id: int
    status: str
    message: str


class EmailAgentStatusResponse(BaseSchema):
    """Response for GET /status — current agent state."""
    run_id: int | None = None
    opening_id: int
    agent_status: str
    current_node: str | None = None
    events: list[dict[str, Any]] = []
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class EmailAgentRunListItem(BaseSchema):
    """Single item in the email agent runs list."""
    id: int
    opening_id: int
    status: str
    current_node: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class EmailAgentResumeRequest(BaseSchema):
    """Request body for resuming a paused email agent run (HITL)."""
    user_edits: list[dict[str, Any]]


class EmailAgentOutputResponse(BaseSchema):
    """The final output of a completed email agent run."""
    generated_emails: list[dict[str, Any]] = []
    subject_lines: list[dict[str, Any]] = []
    followup_drafts: list[dict[str, Any]] = []
    outreach_status: str | None = None
