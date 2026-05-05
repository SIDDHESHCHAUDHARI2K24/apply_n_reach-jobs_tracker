"""
state.py
--------
LangGraph state schema for the AI-Powered Outreach Email feature.

This module defines the single shared state object that flows through
every node in the graph. Each node receives the full state, performs
its work, and returns a dict containing only the fields it updates.
LangGraph merges those updates back into the state automatically.

Design principles:
- Immutability: nodes never mutate state in place — they return updates.
- Clarity: every field is typed and documented so any node author knows
  exactly what they can read and what they are expected to produce.
- Optionality: fields that may not be populated (e.g. when Apollo finds
  no result) are typed as Optional with a None default.

Node → field responsibility map:
  jd_parser         → parsed_jd
  resume_extractor  → relevant_skills, relevant_achievements, skill_gaps
  contact_lookup    → apollo_result, verified_email, contact_name, contact_title
  linkedin_input    → linkedin_context
  email_generator   → generated_emails
  subject_generator → subject_lines, followup_drafts
  review_step       → user_edits  (human-in-the-loop interrupt)
  export_node       → outreach_status
"""

from __future__ import annotations

from typing import Annotated, Optional
from typing_extensions import TypedDict

import operator


# ---------------------------------------------------------------------------
# Sub-types
# These are plain dicts used as structured values inside the main state.
# Using TypedDict for sub-types gives you IDE autocompletion and makes
# the shape of nested data explicit without adding a Pydantic dependency.
# ---------------------------------------------------------------------------

class ParsedJD(TypedDict):
    """Structured representation of a parsed job description."""
    role_title: str
    company_name: str
    team_name: Optional[str]          # e.g. "Platform Engineering" — may not be stated
    location: Optional[str]           # e.g. "Remote", "New York, NY"
    required_skills: list[str]        # extracted hard skills
    responsibilities: list[str]       # key bullet points from the JD
    tone_signals: list[str]           # e.g. ["fast-paced", "collaborative", "data-driven"]
    raw_text: str                     # original JD text, kept for reference


class ApolloResult(TypedDict):
    """Raw result returned by the Apollo.io person search."""
    found: bool                       # True if Apollo returned at least one person
    person_id: Optional[str]          # Apollo internal ID
    full_name: Optional[str]
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    email_status: Optional[str]       # "verified" | "likely valid" | "unverified" | "invalid"
    linkedin_url: Optional[str]       # included when Apollo has it, useful as fallback
    source: str                       # "apollo" | "manual" | "pattern_guess"


class GeneratedEmail(TypedDict):
    """A single generated outreach email with its metadata."""
    recipient_type: str               # "recruiter" | "team_member" | "hiring_manager"
    to_name: Optional[str]            # personalized greeting name if contact was found
    to_email: Optional[str]           # populated if Apollo returned a verified email
    body: str                         # full email body text
    word_count: int
    personalization_signals: list[str]  # e.g. ["referenced LinkedIn post", "matched skill: Python"]


class SubjectLineSet(TypedDict):
    """Subject line options for a specific recipient type."""
    recipient_type: str
    options: list[str]                # 2–3 ranked subject line candidates


class FollowUpDraft(TypedDict):
    """Short follow-up email draft, pre-generated for use after no response."""
    recipient_type: str
    body: str                         # 3–4 sentence follow-up
    suggested_send_after_days: int    # recommended wait before sending (default: 7)


class LinkedInContext(TypedDict):
    """Structured data extracted from a user-pasted LinkedIn profile or post."""
    full_name: Optional[str]
    current_role: Optional[str]
    current_company: Optional[str]
    recent_posts: list[str]           # notable posts or articles the person shared
    notable_projects: list[str]       # projects mentioned in their profile
    shared_connections: list[str]     # mutual connections mentioned by user
    raw_paste: str                    # original user-pasted text, kept for fallback


class UserEdits(TypedDict):
    """Edits made by the user during the human-in-the-loop review step."""
    recipient_type: str               # which email was edited
    edited_body: str                  # final body after user edits
    edited_subject: str               # selected/edited subject line
    reset_to_ai: bool                 # True if user discarded edits and restored AI version


# ---------------------------------------------------------------------------
# Outreach status
# Tracks where this outreach attempt currently stands.
# ---------------------------------------------------------------------------

OUTREACH_STATUS = (
    "drafted",        # email generated, not yet acted on
    "copied",         # user copied to clipboard
    "sent",           # user marked as sent manually
    "followup_due",   # 7 days passed with no reply logged
    "replied",        # user marked as replied
)

OutreachStatus = str  # one of the values in OUTREACH_STATUS


# ---------------------------------------------------------------------------
# Main graph state
# ---------------------------------------------------------------------------

class OutreachState(TypedDict):
    """
    Shared state object for the AI Outreach Email LangGraph workflow.

    This dict is initialized at graph entry and passed through every node.
    Nodes return partial dicts — only the fields they modify — and LangGraph
    merges them back into the running state.

    Fields marked `Annotated[list, operator.add]` use LangGraph's reducer
    pattern: instead of overwriting the list, new items are appended.
    Use this for fields that accumulate values across multiple nodes
    (e.g. errors, debug logs). All other fields are last-write-wins.
    """

    # ------------------------------------------------------------------
    # INPUT — populated at graph entry by the caller
    # ------------------------------------------------------------------

    raw_jd: str
    """The full raw text of the job description, as pasted by the user."""

    raw_resume: str
    """The full raw text of the applicant's resume."""

    recipient_type: str
    """
    Which type of recipient this outreach is targeting.
    One of: "recruiter" | "team_member" | "hiring_manager"
    Set by the user in the UI wizard (T4.1) before the graph runs.
    """

    # ------------------------------------------------------------------
    # JD PARSER OUTPUT — produced by jd_parser node (T1.1)
    # ------------------------------------------------------------------

    parsed_jd: Optional[ParsedJD]
    """
    Structured representation of the job description.
    None until jd_parser node has run.
    """

    # ------------------------------------------------------------------
    # RESUME EXTRACTOR OUTPUT — produced by resume_extractor node (T1.2)
    # ------------------------------------------------------------------

    relevant_skills: Optional[list[str]]
    """
    Top 4–6 skills from the resume most relevant to the parsed JD.
    Selected by vector similarity ranking.
    None until resume_extractor node has run.
    """

    relevant_achievements: Optional[list[str]]
    """
    Top 3–5 resume bullet points (quantified achievements) most relevant
    to the JD. Used as evidence in the generated email body.
    None until resume_extractor node has run.
    """

    skill_gaps: Optional[list[str]]
    """
    Skills listed in the JD that are absent or unverified in the resume.
    Used by the email generator to handle gaps gracefully in tone
    rather than ignore or overclaim them.
    None until resume_extractor node has run.
    """

    # ------------------------------------------------------------------
    # CONTACT LOOKUP OUTPUT — produced by contact_lookup node (T2.1–T2.3)
    # ------------------------------------------------------------------

    apollo_result: Optional[ApolloResult]
    """
    Raw result from the Apollo.io API search.
    None until contact_lookup node has run.
    Inspected by the conditional router (T5.3) to determine next branch:
      - found + verified email  → proceed to email_generator
      - found + no valid email  → branch to linkedin_context node
      - not found               → branch to manual_input or linkedin_draft
    """

    verified_email: Optional[str]
    """
    The verified email address of the target contact.
    Populated only if apollo_result.email_status is "verified" or "likely valid".
    None if Apollo returned no usable email — downstream nodes must handle this.
    """

    contact_name: Optional[str]
    """Full name of the target contact, used to personalize the email greeting."""

    contact_title: Optional[str]
    """Job title of the target contact, used as context in the email body."""

    # ------------------------------------------------------------------
    # LINKEDIN CONTEXT — produced by linkedin_input node (T3.1)
    # ------------------------------------------------------------------

    linkedin_context: Optional[LinkedInContext]
    """
    Structured data extracted from user-pasted LinkedIn profile content.
    None if the user skipped the LinkedIn context step or if it was not
    needed (Apollo already provided full contact info).
    Used by email_generator to inject personalization signals (T3.2).
    """

    # ------------------------------------------------------------------
    # EMAIL GENERATOR OUTPUT — produced by email_generator node (T1.3)
    # ------------------------------------------------------------------

    generated_emails: Optional[list[GeneratedEmail]]
    """
    List of generated outreach emails — one per recipient type requested.
    In standard flow this contains exactly one email matching recipient_type.
    None until email_generator node has run.
    """

    # ------------------------------------------------------------------
    # SUBJECT + FOLLOW-UP — produced by subject_generator node (T1.4)
    # ------------------------------------------------------------------

    subject_lines: Optional[list[SubjectLineSet]]
    """
    Subject line options grouped by recipient type.
    Each SubjectLineSet contains 2–3 ranked candidates.
    None until subject_generator node has run.
    """

    followup_drafts: Optional[list[FollowUpDraft]]
    """
    Pre-generated short follow-up emails for each recipient type.
    Surfaced in the UI status tracker (T4.4) when follow-up is due.
    None until subject_generator node has run.
    """

    # ------------------------------------------------------------------
    # HUMAN-IN-THE-LOOP — populated during review_step interrupt (T5.4)
    # ------------------------------------------------------------------

    user_edits: Optional[list[UserEdits]]
    """
    Edits made by the user during the review step.
    The graph pauses at review_step via LangGraph interrupt, the UI
    renders the generated emails for editing (T4.3), and when the user
    confirms, the updated content is written here and the graph resumes.
    None until the user completes the review step.
    """

    # ------------------------------------------------------------------
    # EXPORT / STATUS — updated by export_node and the UI (T4.4, T4.5)
    # ------------------------------------------------------------------

    outreach_status: Optional[OutreachStatus]
    """
    Current status of this outreach attempt.
    One of: "drafted" | "copied" | "sent" | "followup_due" | "replied"
    Updated by export_node after the graph completes, and then kept
    in sync by the UI status tracker as the user progresses.
    """

    # ------------------------------------------------------------------
    # DIAGNOSTIC — accumulates across nodes using LangGraph reducer
    # ------------------------------------------------------------------

    errors: Annotated[list[str], operator.add]
    """
    Non-fatal errors and warnings accumulated across nodes.
    Uses operator.add reducer so each node can append without overwriting.
    Examples:
      - "apollo: no verified email found for contact"
      - "jd_parser: team_name not found in JD — using None"
      - "email_generator: skill_gaps present — applied gap-acknowledgment tone"
    Always initialize as an empty list: errors=[]
    """

    debug_log: Annotated[list[str], operator.add]
    """
    Debug trace messages appended by each node for development visibility.
    Uses operator.add reducer — same pattern as errors.
    Strip or gate behind a DEBUG flag before any demo or presentation.
    Always initialize as an empty list: debug_log=[]
    """


# ---------------------------------------------------------------------------
# State initializer
# ---------------------------------------------------------------------------

def initial_state(
    raw_jd: str,
    raw_resume: str,
    recipient_type: str,
) -> OutreachState:
    """
    Create a clean initial state to pass as input when invoking the graph.

    Usage:
        state = initial_state(
            raw_jd="Senior ML Engineer at Stripe...",
            raw_resume="Alex Rivera — ML Engineer...",
            recipient_type="recruiter",
        )
        result = graph.invoke(state, config={"configurable": {"thread_id": "thread-001"}})

    Args:
        raw_jd:          Full text of the job description.
        raw_resume:      Full text of the applicant resume.
        recipient_type:  One of "recruiter" | "team_member" | "hiring_manager".

    Returns:
        A fully initialized OutreachState with all optional fields set to None
        and all list fields initialized to empty lists.
    """
    assert recipient_type in ("recruiter", "team_member", "hiring_manager"), (
        f"recipient_type must be one of: recruiter, team_member, hiring_manager. Got: {recipient_type!r}"
    )

    return OutreachState(
        # Inputs
        raw_jd=raw_jd,
        raw_resume=raw_resume,
        recipient_type=recipient_type,

        # JD parser
        parsed_jd=None,

        # Resume extractor
        relevant_skills=None,
        relevant_achievements=None,
        skill_gaps=None,

        # Contact lookup
        apollo_result=None,
        verified_email=None,
        contact_name=None,
        contact_title=None,

        # LinkedIn context
        linkedin_context=None,

        # Email generator
        generated_emails=None,

        # Subject + follow-up
        subject_lines=None,
        followup_drafts=None,

        # Human-in-the-loop
        user_edits=None,

        # Export / status
        outreach_status=None,

        # Diagnostics
        errors=[],
        debug_log=[],
    )
