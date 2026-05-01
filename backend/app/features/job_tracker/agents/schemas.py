"""Pydantic schemas for the agent router."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.features.core.base_model import BaseSchema


class AgentRunRequest(BaseSchema):
    """Request body for starting an agent run."""
    pass  # opening_id comes from path param


class AgentRunResponse(BaseSchema):
    """Response for POST /run — returns 202 with the new run ID."""
    run_id: int
    opening_id: int
    status: str
    message: str


class AgentStatusResponse(BaseSchema):
    """Response for GET /status — current agent state."""
    run_id: int | None = None
    opening_id: int
    agent_status: str
    current_node: str | None = None
    events: list[dict[str, Any]] = []
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AgentRunListItem(BaseSchema):
    """Single item in the agent runs list."""
    id: int
    opening_id: int
    status: str
    current_node: str | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
