"""
nodes/subject_generator.py
---------------------------
Node: subject_generator

Reads:  state["generated_emails"]
        state["parsed_jd"]
        state["contact_name"]
        state["recipient_type"]
Writes: state["subject_lines"]
        state["followup_drafts"]
        state["errors"]
        state["debug_log"]

Generates 2–3 subject line options and a pre-drafted follow-up email
for the generated outreach email. Runs after email_generator.

Subject lines are specific to the role, company, and recipient type —
never generic. Follow-up drafts are short (3–4 sentences), add new value,
and are pre-set to send after 7 days with no response.
"""

from __future__ import annotations

import json

from app.features.job_tracker.email_agent.state import (
    EmailAgentState,
    SubjectLineSet,
    FollowUpDraft,
)
from app.features.job_tracker.email_agent.nodes import _chat

_SUBJECT_SYSTEM = """
You write email subject lines for job seeker outreach emails.
Generate exactly 3 subject line options for the email provided.

Rules:
- Each subject line must be specific to the role, company, and recipient.
- Never use generic phrases like "Quick question", "Following up",
  "Reaching out", or "Opportunity".
- Subject lines should be 6–12 words — specific enough to stand out,
  short enough to read in a preview pane.
- Vary the angle: one factual (role + company), one value-forward
  (what the candidate brings), one curiosity-driven (question or hook).
- Return ONLY a valid JSON array of exactly 3 strings.
  Example: ["Subject one", "Subject two", "Subject three"]
""".strip()

_FOLLOWUP_SYSTEM = """
You write short follow-up emails for job seekers who sent an outreach
email and received no response after 7 days.

Rules:
- 3–4 sentences maximum.
- Add one new piece of value not mentioned in the original email
  (a recent achievement, a relevant observation about the company,
  or a specific question about the team).
- Do NOT say "I just wanted to follow up on my previous email"
  or any equivalent opener — assume they read it.
- Keep the same tone and recipient type as the original email.
- End with the same call to action as the original, restated briefly.
- Output the follow-up body only — no subject line, no greeting, no sign-off.
""".strip()


async def subject_generator(state: EmailAgentState) -> dict:
    """
    LangGraph node — generates subject line options and a follow-up draft
    for the outreach email produced by email_generator.
    """
    errors: list[str] = []
    debug_log: list[str] = []
    recipient_type = state["recipient_type"]

    debug_log.append("subject_generator: starting")

    generated_emails = state.get("generated_emails") or []
    if not generated_emails:
        errors.append("subject_generator: no generated emails found — skipping")
        return {
            "subject_lines": [],
            "followup_drafts": [],
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }

    email = generated_emails[0]
    parsed_jd = state.get("parsed_jd")

    role = parsed_jd["role_title"] if parsed_jd else "the role"
    company = parsed_jd["company_name"] if parsed_jd else "your company"
    contact = state.get("contact_name") or "there"

    context = (
        f"Recipient type: {recipient_type}\n"
        f"Role: {role} at {company}\n"
        f"Contact name: {contact}\n\n"
        f"EMAIL BODY:\n{email['body']}"
    )

    # --- Subject lines ---
    subject_options: list[str] = []
    try:
        raw_json = await _chat(system=_SUBJECT_SYSTEM, user=context, max_tokens=256)
        subject_options = json.loads(raw_json)
        if not isinstance(subject_options, list):
            raise ValueError("expected a JSON array")
        subject_options = [s for s in subject_options if isinstance(s, str)][:3]
    except Exception as exc:
        errors.append(f"subject_generator: subject line generation failed — {exc}")
        subject_options = [
            f"{role} at {company} — reaching out",
            f"Interested in the {role} role",
            f"Background in {', '.join((state.get('relevant_skills') or ['the field'])[:2])}",
        ]

    subject_line_set: SubjectLineSet = {
        "recipient_type": recipient_type,
        "options": subject_options,
    }

    debug_log.append(f"subject_generator: generated {len(subject_options)} subject lines")

    # --- Follow-up draft ---
    followup_body: str = ""
    try:
        followup_body = await _chat(system=_FOLLOWUP_SYSTEM, user=context, max_tokens=300)
    except Exception as exc:
        errors.append(f"subject_generator: follow-up generation failed — {exc}")

    followup_draft: FollowUpDraft = {
        "recipient_type": recipient_type,
        "body": followup_body,
        "suggested_send_after_days": 7,
    }

    debug_log.append(
        f"subject_generator: done — "
        f"subjects={len(subject_options)} "
        f"followup_words={len(followup_body.split())}"
    )

    return {
        "subject_lines": [subject_line_set],
        "followup_drafts": [followup_draft],
        "errors": state.get("errors", []) + errors,
        "debug_log": state.get("debug_log", []) + debug_log,
    }
