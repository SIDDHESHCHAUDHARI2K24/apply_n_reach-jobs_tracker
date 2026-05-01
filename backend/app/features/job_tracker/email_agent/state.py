"""
email_agent state — adapted from email_Feature/state.py for in-app use.

Node -> field responsibility map:
  jd_parser         -> parsed_jd
  resume_extractor  -> relevant_skills, relevant_achievements, skill_gaps
  contact_lookup    -> apollo_result, verified_email, contact_name, contact_title
  linkedin_input    -> linkedin_context
  email_generator   -> generated_emails
  subject_generator -> subject_lines, followup_drafts
  export_node       -> outreach_status
"""
from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict


class ParsedJD(TypedDict):
    role_title: str
    company_name: str
    team_name: Optional[str]
    location: Optional[str]
    required_skills: list[str]
    responsibilities: list[str]
    tone_signals: list[str]
    raw_text: str


class ApolloResult(TypedDict):
    found: bool
    person_id: Optional[str]
    full_name: Optional[str]
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    email_status: Optional[str]
    linkedin_url: Optional[str]
    source: str


class GeneratedEmail(TypedDict):
    recipient_type: str
    to_name: Optional[str]
    to_email: Optional[str]
    body: str
    word_count: int
    personalization_signals: list[str]


class SubjectLineSet(TypedDict):
    recipient_type: str
    options: list[str]


class FollowUpDraft(TypedDict):
    recipient_type: str
    body: str
    suggested_send_after_days: int


class LinkedInContext(TypedDict):
    full_name: Optional[str]
    current_role: Optional[str]
    current_company: Optional[str]
    recent_posts: list[str]
    notable_projects: list[str]
    shared_connections: list[str]
    raw_paste: str


class EmailAgentEvent(TypedDict, total=False):
    node: str
    status: str
    message: str
    data: dict[str, Any]


class EmailAgentState(TypedDict, total=False):
    """Shared state for the email agent LangGraph workflow.

    Mirrors email_Feature/state.py OutreachState but adapted for in-app use:
    - opening_id and user_id are always present (set by runner)
    - run_id tracks the DB run record
    - events accumulate across nodes
    - error signals early termination
    """
    opening_id: int
    user_id: int
    run_id: int

    raw_jd: str
    raw_resume: str
    recipient_type: str

    parsed_jd: Optional[ParsedJD]
    relevant_skills: Optional[list[str]]
    relevant_achievements: Optional[list[str]]
    skill_gaps: Optional[list[str]]

    apollo_result: Optional[ApolloResult]
    verified_email: Optional[str]
    contact_name: Optional[str]
    contact_title: Optional[str]

    linkedin_context: Optional[LinkedInContext]

    generated_emails: Optional[list[GeneratedEmail]]
    subject_lines: Optional[list[SubjectLineSet]]
    followup_drafts: Optional[list[FollowUpDraft]]

    user_edits: Optional[list[dict[str, Any]]]
    outreach_status: Optional[str]

    events: list[EmailAgentEvent]
    errors: list[str]
    debug_log: list[str]
    error: Optional[str]
