"""Email agent runner — executes the LangGraph email agent and yields events."""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

import asyncpg

from app.features.job_tracker.agents.config import configure_langsmith
from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
from app.features.job_tracker.email_agent.graph import build_graph
from app.features.job_tracker.email_agent.state import EmailAgentEvent, EmailAgentState

logger = logging.getLogger(__name__)


async def run_email_agent_stream(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    run_id: int,
    recipient_type: str = "recruiter",
    raw_jd_override: str | None = None,
    raw_resume_override: str | None = None,
) -> AsyncIterator[EmailAgentEvent]:
    """Execute the email agent and yield events as they occur.

    Fetches JD text and resume text from the database, runs the compiled
    graph, persists state to the email_agent_runs table, and yields events
    for SSE streaming.
    """
    configure_langsmith()

    # Mark run as running
    await conn.execute(
        "UPDATE job_opening_email_agent_runs SET status='running', current_node='jd_parser' WHERE id=$1",
        run_id,
    )

    yield EmailAgentEvent(node="agent", status="started", message="Email agent started")

    try:
        # Fetch JD text from the database
        raw_jd = raw_jd_override or await _build_raw_jd(conn, opening_id)

        # Fetch resume text from the database
        raw_resume = raw_resume_override or await _build_raw_resume(conn, opening_id)

        graph = build_graph()
        initial_state: EmailAgentState = {
            "opening_id": opening_id,
            "user_id": user_id,
            "run_id": run_id,
            "raw_jd": raw_jd,
            "raw_resume": raw_resume,
            "recipient_type": recipient_type,
            "events": [],
            "errors": [],
            "debug_log": [],
        }

        # Stream through graph nodes
        final_state = initial_state
        emitted_event_count = 0
        async for event in graph.astream(initial_state, config={"configurable": {"run_id": run_id}}):
            for node_name, state_update in event.items():
                if isinstance(state_update, dict):
                    final_state = {**final_state, **state_update}

                    await conn.execute(
                        "UPDATE job_opening_email_agent_runs SET current_node=$1 WHERE id=$2",
                        node_name, run_id,
                    )

                    all_events = final_state.get("events", [])
                    new_events = all_events[emitted_event_count:]
                    for evt in new_events:
                        yield evt
                    emitted_event_count = len(all_events)

                    if state_update.get("error"):
                        logger.warning(
                            "Email agent error at node %s: %s",
                            node_name, state_update["error"],
                        )

        # Determine final status
        error = final_state.get("error")
        final_status = "failed" if error else "succeeded"

        # Persist final state
        await conn.execute(
            """
            UPDATE job_opening_email_agent_runs
            SET status=$1, state=$2::jsonb, events=$3::jsonb,
                completed_at=NOW(), error_message=$4, current_node=NULL
            WHERE id=$5
            """,
            final_status,
            json.dumps(_sanitize_state(final_state)),
            json.dumps(final_state.get("events", [])),
            error,
            run_id,
        )

        yield EmailAgentEvent(
            node="agent",
            status=final_status,
            message=error or "Email agent completed successfully",
        )

    except Exception as e:
        logger.exception("Email agent runner crashed for run %d", run_id)
        await conn.execute(
            """
            UPDATE job_opening_email_agent_runs
            SET status='failed', error_message=$1, completed_at=NOW()
            WHERE id=$2
            """,
            str(e), run_id,
        )
        yield EmailAgentEvent(node="agent", status="error", message=str(e))


async def _build_raw_jd(conn: asyncpg.Connection, opening_id: int) -> str:
    """Build a raw JD text string from job_openings + latest extracted details."""
    opening = await conn.fetchrow(
        """
        SELECT company_name, role_name, source_url
        FROM job_openings
        WHERE id=$1
        """,
        opening_id,
    )
    if not opening:
        return ""

    parts: list[str] = []
    if opening["company_name"]:
        parts.append(f"Company: {opening['company_name']}")
    if opening["role_name"]:
        parts.append(f"Role: {opening['role_name']}")
    if opening["source_url"]:
        parts.append(f"Source URL: {opening['source_url']}")

    details = await conn.fetchrow(
        """
        SELECT job_title, description_summary, role_summary, location,
               employment_type, salary_range, experience_level,
               required_skills, preferred_skills, technical_keywords,
               sector_keywords, business_sectors, problem_being_solved,
               useful_experiences
        FROM job_opening_extracted_details_versions
        WHERE opening_id=$1
        ORDER BY extracted_at DESC LIMIT 1
        """,
        opening_id,
    )
    if details:
        if details["job_title"]:
            parts.append(f"Job Title: {details['job_title']}")
        if details["location"]:
            parts.append(f"Location: {details['location']}")
        if details["employment_type"]:
            parts.append(f"Employment Type: {details['employment_type']}")
        if details["salary_range"]:
            parts.append(f"Salary Range: {details['salary_range']}")
        if details["experience_level"]:
            parts.append(f"Experience Level: {details['experience_level']}")
        if details["description_summary"]:
            parts.append(f"Description: {details['description_summary']}")
        if details["role_summary"]:
            parts.append(f"Role Summary: {details['role_summary']}")
        if details["problem_being_solved"]:
            parts.append(f"Problem Being Solved: {details['problem_being_solved']}")

        for field, label in [
            ("required_skills", "Required Skills"),
            ("preferred_skills", "Preferred Skills"),
            ("technical_keywords", "Technical Keywords"),
            ("sector_keywords", "Sector Keywords"),
            ("business_sectors", "Business Sectors"),
            ("useful_experiences", "Useful Experiences"),
        ]:
            val = details[field]
            if val:
                if isinstance(val, list):
                    parts.append(f"{label}: {', '.join(val)}")
                elif isinstance(val, str):
                    parts.append(f"{label}: {val}")

    return "\n".join(parts)


async def _build_raw_resume(conn: asyncpg.Connection, opening_id: int) -> str:
    """Build a raw resume text string from the snapshot tables."""
    resume = await conn.fetchrow(
        """
        SELECT id, source_job_profile_id
        FROM job_opening_resumes
        WHERE opening_id=$1
        ORDER BY snapshot_at DESC LIMIT 1
        """,
        opening_id,
    )
    if not resume:
        return ""

    resume_id = resume["id"]
    parts: list[str] = []

    # Personal details
    personal = await conn.fetchrow(
        """
        SELECT full_name, email, phone, location, linkedin_url,
               github_url, portfolio_url, summary
        FROM job_opening_personal
        WHERE resume_id=$1
        """,
        resume_id,
    )
    if personal:
        if personal["full_name"]:
            parts.append(f"Name: {personal['full_name']}")
        if personal["email"]:
            parts.append(f"Email: {personal['email']}")
        if personal["phone"]:
            parts.append(f"Phone: {personal['phone']}")
        if personal["location"]:
            parts.append(f"Location: {personal['location']}")
        if personal["linkedin_url"]:
            parts.append(f"LinkedIn: {personal['linkedin_url']}")
        if personal["github_url"]:
            parts.append(f"GitHub: {personal['github_url']}")
        if personal["portfolio_url"]:
            parts.append(f"Portfolio: {personal['portfolio_url']}")
        if personal["summary"]:
            parts.append(f"Summary: {personal['summary']}")

    # Experience
    exp_rows = await conn.fetch(
        """
        SELECT company, title, location, start_date, end_date, is_current, description
        FROM job_opening_experience
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if exp_rows:
        parts.append("\n--- Experience ---")
        for exp in exp_rows:
            date_range = _format_date_range(exp["start_date"], exp["end_date"], exp["is_current"])
            parts.append(f"{exp['title']} at {exp['company']} ({date_range})")
            if exp["location"]:
                parts.append(f"  Location: {exp['location']}")
            if exp["description"]:
                parts.append(f"  {exp['description']}")

    # Education
    edu_rows = await conn.fetch(
        """
        SELECT institution, degree, field_of_study, start_date, end_date,
               grade, description
        FROM job_opening_education
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if edu_rows:
        parts.append("\n--- Education ---")
        for edu in edu_rows:
            entry = f"{edu.get('degree', '')} {edu.get('field_of_study', '')} - {edu['institution']}"
            parts.append(entry.strip())
            if edu.get("grade"):
                parts.append(f"  Grade: {edu['grade']}")
            if edu.get("description"):
                parts.append(f"  {edu['description']}")

    # Projects
    proj_rows = await conn.fetch(
        """
        SELECT name, description, url, technologies
        FROM job_opening_projects
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if proj_rows:
        parts.append("\n--- Projects ---")
        for proj in proj_rows:
            parts.append(f"Project: {proj['name']}")
            if proj.get("description"):
                parts.append(f"  {proj['description']}")
            if proj.get("url"):
                parts.append(f"  URL: {proj['url']}")
            if proj.get("technologies"):
                techs = proj["technologies"]
                if isinstance(techs, list):
                    parts.append(f"  Technologies: {', '.join(techs)}")

    # Skills
    skill_rows = await conn.fetch(
        """
        SELECT category, name, proficiency_level
        FROM job_opening_skills
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if skill_rows:
        parts.append("\n--- Skills ---")
        for skill in skill_rows:
            entry = skill["name"]
            if skill.get("proficiency_level"):
                entry += f" ({skill['proficiency_level']})"
            parts.append(f"{skill['category']}: {entry}")

    # Certifications
    cert_rows = await conn.fetch(
        """
        SELECT name, issuer, issue_date, expiry_date, credential_id, url
        FROM job_opening_certifications
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if cert_rows:
        parts.append("\n--- Certifications ---")
        for cert in cert_rows:
            parts.append(f"{cert['name']} - {cert.get('issuer', '')}")
            if cert.get("credential_id"):
                parts.append(f"  Credential ID: {cert['credential_id']}")

    # Research
    research_rows = await conn.fetch(
        """
        SELECT title, publication, published_date, url, description
        FROM job_opening_research
        WHERE resume_id=$1
        ORDER BY display_order
        """,
        resume_id,
    )
    if research_rows:
        parts.append("\n--- Research ---")
        for r in research_rows:
            parts.append(f"{r['title']}")
            if r.get("publication"):
                parts.append(f"  Published in: {r['publication']}")
            if r.get("description"):
                parts.append(f"  {r['description']}")

    return "\n".join(parts)


def _format_date_range(start: str | None, end: str | None, is_current: bool) -> str:
    """Format a date range string for display."""
    s = start or "?"
    e = "Present" if is_current else (end or "?")
    return f"{s} - {e}"


def _sanitize_state(state: dict[str, Any]) -> dict[str, Any]:
    """Remove non-serializable values from state for JSON storage."""
    safe = {}
    for k, v in state.items():
        if k == "events":
            continue
        try:
            json.dumps(v)
            safe[k] = v
        except (TypeError, ValueError):
            safe[k] = str(v)
    return safe
