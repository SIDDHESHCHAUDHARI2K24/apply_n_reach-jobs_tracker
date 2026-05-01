"""Agent state definition for the LangGraph resume-tailoring agent."""
from __future__ import annotations

from typing import Any, TypedDict


class AgentEvent(TypedDict, total=False):
    """Single event emitted during agent execution."""
    node: str
    status: str  # "started" | "completed" | "error"
    message: str
    data: dict[str, Any]


class AgentState(TypedDict, total=False):
    """Full state carried through the LangGraph agent."""
    # Identifiers
    opening_id: int
    user_id: int
    run_id: int

    # Extraction results (set by node 1 / pre-loaded)
    extracted_details: dict[str, Any]

    # Template selection (set by node 2)
    selected_job_profile_id: int | None

    # Resume snapshot (set by node 3)
    resume_created: bool

    # Triage decisions (set by node 4)
    triage: dict[str, Any]

    # Section states after tailoring (set by nodes 5a-5d)
    experience_tailored: bool
    projects_tailored: bool
    skills_tailored: bool
    personal_tailored: bool

    # Skills & certs pass (set by node 6)
    skills_certs_done: bool

    # Render info (set by node 7)
    pdf_page_count: int
    render_count: int

    # Optimiser loop (set by node 8)
    optimiser_iterations: int

    # Event log
    events: list[AgentEvent]

    # Error tracking
    error: str | None
