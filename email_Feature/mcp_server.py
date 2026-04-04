"""
mcp_server.py
--------------
Exposes the outreach email graph as an MCP server for Claude Desktop.

Claude Desktop launches this script as a subprocess and communicates
over stdin/stdout (stdio transport — the default for local MCP servers).

Tools exposed to Claude Desktop:
  1. generate_outreach_email  — runs the full graph up to the HITL interrupt
  2. resume_after_review      — resumes the graph after user edits
  3. get_outreach_status      — returns the current state snapshot for a thread
  4. list_valid_recipient_types — helper so Claude knows what values are valid

Usage (Claude Desktop will launch this automatically once configured):
    python mcp_server.py

To test manually before connecting to Claude Desktop:
    npx @modelcontextprotocol/inspector python mcp_server.py
"""

from __future__ import annotations

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv()

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from graph import graph
from state import initial_state

# ---------------------------------------------------------------------------
# In-memory thread registry
# Maps thread_id → last known state snapshot returned by the graph.
# In production replace with a persistent store (Redis, Postgres, etc.)
# ---------------------------------------------------------------------------
_thread_snapshots: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# MCP server instance
# The name "Outreach Email Assistant" appears in Claude Desktop's tool panel.
# ---------------------------------------------------------------------------
mcp = FastMCP("Outreach Email Assistant")


# ---------------------------------------------------------------------------
# Tool 1 — generate_outreach_email
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_outreach_email(
    job_description: str,
    resume: str,
    recipient_type: str,
    thread_id: str,
    linkedin_paste: Optional[str] = None,
) -> str:
    """
    Generate a personalized outreach email using the applicant's resume
    and a job description.

    Runs the full AI pipeline (JD parsing → skill extraction → Apollo
    contact lookup → email generation → subject lines + follow-up draft)
    and returns the results. The graph pauses before the final export step
    so the user can review and edit the email before confirming.

    Args:
        job_description:  Full text of the job description to apply for.
        resume:           Full text of the applicant's resume.
        recipient_type:   Who to write to. Must be one of:
                            "recruiter"      — concise, conversion-focused
                            "team_member"    — warm coffee-chat request
                            "hiring_manager" — outcome-oriented, peer-level
        thread_id:        Unique identifier for this outreach attempt.
                          Use a descriptive string like "stripe-ml-recruiter".
                          Reusing the same thread_id resumes an existing session.
        linkedin_paste:   Optional. Paste the target person's LinkedIn About
                          section, a recent post, or any profile text to
                          personalize the email further (especially useful
                          for the team_member coffee-chat email).

    Returns:
        A formatted summary of the generated email, subject line options,
        follow-up draft, and any warnings from the pipeline.
    """
    valid_types = {"recruiter", "team_member", "hiring_manager"}
    if recipient_type not in valid_types:
        return (
            f"Invalid recipient_type '{recipient_type}'. "
            f"Must be one of: {', '.join(sorted(valid_types))}"
        )

    config = {"configurable": {"thread_id": thread_id}}

    # Build initial state — include linkedin_paste as an extra field
    # (linkedin_input node reads it with state.get("raw_linkedin_paste"))
    state = initial_state(
        raw_jd=job_description,
        raw_resume=resume,
        recipient_type=recipient_type,
    )
    if linkedin_paste and linkedin_paste.strip():
        state["raw_linkedin_paste"] = linkedin_paste  # type: ignore[typeddict-unknown-key]

    try:
        result = graph.invoke(state, config=config)
    except Exception as exc:
        return f"Graph execution failed: {exc}"

    # Cache the snapshot for resume_after_review
    _thread_snapshots[thread_id] = result

    return _format_generation_result(result, thread_id)


# ---------------------------------------------------------------------------
# Tool 2 — resume_after_review
# ---------------------------------------------------------------------------

@mcp.tool()
def resume_after_review(
    thread_id: str,
    edited_body: str,
    selected_subject: str,
    reset_to_ai: bool = False,
) -> str:
    """
    Resume the outreach graph after the user has reviewed and optionally
    edited the generated email.

    Call this after generate_outreach_email once the user is satisfied
    with the email content. This triggers the final export step, applies
    any edits, and marks the outreach status as 'drafted'.

    Args:
        thread_id:        The same thread_id used in generate_outreach_email.
        edited_body:      The final email body (edited or unchanged from
                          the AI-generated version).
        selected_subject: The chosen subject line from the options provided.
        reset_to_ai:      Set to True to discard any edits and use the
                          original AI-generated email body instead.

    Returns:
        Confirmation that the outreach package is finalized, with a
        summary of what was saved.
    """
    snapshot = _thread_snapshots.get(thread_id)
    if snapshot is None:
        return (
            f"No active session found for thread_id '{thread_id}'. "
            f"Run generate_outreach_email first."
        )

    recipient_type = snapshot.get("recipient_type", "recruiter")
    config = {"configurable": {"thread_id": thread_id}}

    user_edits = [
        {
            "recipient_type": recipient_type,
            "edited_body": edited_body,
            "edited_subject": selected_subject,
            "reset_to_ai": reset_to_ai,
        }
    ]

    try:
        final_result = graph.invoke({"user_edits": user_edits}, config=config)
    except Exception as exc:
        return f"Graph resume failed: {exc}"

    _thread_snapshots[thread_id] = final_result

    emails = final_result.get("generated_emails") or []
    status = final_result.get("outreach_status", "unknown")
    word_count = emails[0]["word_count"] if emails else 0
    to_email = emails[0].get("to_email") if emails else None

    lines = [
        f"Outreach package finalized.",
        f"  Status       : {status}",
        f"  Subject      : {selected_subject}",
        f"  Word count   : {word_count}",
        f"  Send to      : {to_email or 'no verified email found — use LinkedIn message'}",
        f"  Thread ID    : {thread_id}",
        "",
        "The email is ready to copy and send. Use get_outreach_status to",
        "retrieve the full email body at any time.",
    ]

    if reset_to_ai:
        lines.insert(1, "  Note: reset to AI version (user edits discarded)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3 — get_outreach_status
# ---------------------------------------------------------------------------

@mcp.tool()
def get_outreach_status(thread_id: str) -> str:
    """
    Retrieve the current state snapshot for an outreach session,
    including the full email body, subject lines, follow-up draft,
    contact info found by Apollo, and any warnings from the pipeline.

    Useful for reviewing a previously generated email or checking
    what contact information Apollo returned.

    Args:
        thread_id: The thread_id used when generating the email.

    Returns:
        Full formatted summary of the outreach session state.
    """
    snapshot = _thread_snapshots.get(thread_id)
    if snapshot is None:
        return f"No session found for thread_id '{thread_id}'."

    return _format_generation_result(snapshot, thread_id, verbose=True)


# ---------------------------------------------------------------------------
# Tool 4 — list_valid_recipient_types
# ---------------------------------------------------------------------------

@mcp.tool()
def list_valid_recipient_types() -> str:
    """
    Returns the valid recipient_type values and a description of each.
    Use this to remind yourself of the options before calling
    generate_outreach_email.
    """
    return "\n".join([
        "Valid recipient_type values:",
        "",
        "  recruiter      — Concise (150–200 words), conversion-focused email.",
        "                   Highlights top 2–3 matching skills. Clear call to action.",
        "                   Best for: initial contact with a talent acquisition person.",
        "",
        "  team_member    — Warm, curious coffee-chat request (120–180 words).",
        "                   References the person's work. Asks for a 20-min chat.",
        "                   Does NOT mention job applications explicitly.",
        "                   Best for: building a relationship before applying.",
        "                   Tip: provide linkedin_paste for much better personalization.",
        "",
        "  hiring_manager — Confident, outcome-oriented email (180–220 words).",
        "                   Connects candidate achievements to team needs from JD.",
        "                   Peer-level tone. Addresses skill gaps honestly if present.",
        "                   Best for: direct outreach to the decision-maker.",
    ])


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_generation_result(result: dict, thread_id: str, verbose: bool = False) -> str:
    """Format a graph state snapshot into a readable string for Claude Desktop."""
    lines: list[str] = []

    # Header
    lines.append(f"Thread ID: {thread_id}")
    lines.append(f"Status   : {result.get('outreach_status') or 'pending review'}")

    # Apollo contact
    apollo = result.get("apollo_result")
    if apollo:
        lines.append("")
        lines.append("Contact found:")
        lines.append(f"  Name   : {apollo.get('full_name') or 'not found'}")
        lines.append(f"  Title  : {apollo.get('title') or 'not found'}")
        lines.append(f"  Email  : {result.get('verified_email') or 'not verified'}")
        lines.append(f"  Source : {apollo.get('source', 'apollo')}")

    # Generated email
    emails = result.get("generated_emails") or []
    if emails:
        email = emails[0]
        lines.append("")
        lines.append(f"Generated email ({email['recipient_type']}):")
        lines.append(f"  Word count : {email['word_count']}")
        if email.get("personalization_signals"):
            lines.append(f"  Signals    : {', '.join(email['personalization_signals'])}")
        lines.append("")
        lines.append("--- EMAIL BODY ---")
        lines.append(email["body"])
        lines.append("--- END ---")

    # Subject lines
    subject_sets = result.get("subject_lines") or []
    if subject_sets:
        lines.append("")
        lines.append("Subject line options:")
        for i, option in enumerate(subject_sets[0].get("options", []), 1):
            lines.append(f"  {i}. {option}")

    # Follow-up draft
    followups = result.get("followup_drafts") or []
    if followups and verbose:
        fu = followups[0]
        lines.append("")
        lines.append(f"Follow-up draft (send after {fu['suggested_send_after_days']} days):")
        lines.append(fu["body"])

    # Warnings
    errors = result.get("errors") or []
    if errors:
        lines.append("")
        lines.append("Warnings:")
        for e in errors:
            lines.append(f"  ⚠  {e}")

    # Debug log (verbose only)
    if verbose:
        debug = result.get("debug_log") or []
        if debug:
            lines.append("")
            lines.append("Debug log:")
            for entry in debug[-10:]:
                lines.append(f"  {entry}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()   # stdio transport — Claude Desktop communicates over stdin/stdout
