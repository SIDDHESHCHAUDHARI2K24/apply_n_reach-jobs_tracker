"""
nodes/email_generator.py
-------------------------
Node: email_generator

Reads:  state["parsed_jd"]
        state["recipient_type"]
        state["relevant_skills"]
        state["relevant_achievements"]
        state["skill_gaps"]
        state["contact_name"]        (optional — personalizes greeting)
        state["contact_title"]       (optional — context for tone)
        state["linkedin_context"]    (optional — personalization signals)
Writes: state["generated_emails"]
        state["errors"]
        state["debug_log"]

Generates one outreach email tailored to the recipient type.
Three distinct prompt templates are used — recruiter, team_member,
and hiring_manager — each with a different structure and tone goal.

Skill gaps are handled gracefully in tone: the email acknowledges the
candidate is actively developing in gap areas rather than ignoring them
or overclaiming proficiency.

LinkedIn context signals (posts, projects, shared connections) are
injected into the prompt when available to add genuine personalization —
especially important for the coffee-chat (team_member) email.
"""

from __future__ import annotations

from llm import chat
from state import OutreachState, GeneratedEmail, LinkedInContext

# ---------------------------------------------------------------------------
# Prompt templates — one per recipient type
# ---------------------------------------------------------------------------

_RECRUITER_SYSTEM = """
You write concise, professional outreach emails from job candidates to recruiters.

Your email must:
- Be 150–200 words maximum (body only, not counting greeting/sign-off).
- Start with a personalized greeting (e.g., "Hi [Name]," or "Dear [Name],").
- Open with one sentence stating the specific role and company the candidate
  is interested in.
- Highlight 2–3 of the candidate's most relevant skills or achievements
  that match the role — be specific, not generic.
- Close with a clear, low-friction call to action (e.g. ask if they can
  connect briefly or share more about the role).
- End with a professional closing and the candidate's name (e.g., "Best regards," 
  or "Looking forward to connecting,").
- Sound confident and professional, never desperate.
- NOT use filler phrases like "I hope this email finds you well",
  "I am writing to express my interest", or "please find attached".

Output the complete email with greeting, body, and closing signature.
""".strip()

_TEAM_MEMBER_SYSTEM = """
You write warm, genuine coffee-chat outreach emails from job candidates
to team members at a company they want to join.

Your email must:
- Be 120–180 words maximum (body only).
- Start with a personalized greeting (e.g., "Hi [Name]," or "Dear [Name],").
- Open by referencing something specific about the person or their team's
  work (use the LinkedIn signals provided if available — a post they shared,
  a project they worked on, or their specific role).
- Briefly introduce the candidate and their background in 1–2 sentences.
- Ask for a 20-minute conversation to learn more about the team, the product,
  or what it's like to work there — be specific about what you want to learn.
- End with a warm closing and the candidate's name (e.g., "Cheers,", 
  "Warm regards,", or "Thanks,").
- Sound genuinely curious and human, not transactional or template-like.
- NOT mention job applications, hiring, or resumes explicitly —
  this is a relationship-building email, not a job request.

Output the complete email with greeting, body, and closing signature.
""".strip()

_HIRING_MANAGER_SYSTEM = """
You write confident, outcome-oriented outreach emails from job candidates
to hiring managers.

Your email must:
- Be 180–220 words maximum (body only).
- Start with a personalized greeting (e.g., "Hi [Name]," or "Dear [Name],").
- Open by demonstrating understanding of what the role is trying to achieve
  (based on the JD responsibilities).
- Connect 2–3 specific candidate achievements directly to the team's apparent
  needs — show, don't tell.
- If there are skill gaps, acknowledge one honestly in a single sentence
  ("I am actively deepening my experience in X") — do not list all gaps
  or dwell on them.
- Close with a specific ask: a brief call to explore whether there could be
  a fit, or to share more about how the candidate could contribute.
- End with a professional closing and the candidate's name (e.g., "Best regards,", 
  "Kind regards,", or "Looking forward to our conversation,").
- Sound senior and peer-level, not supplicant — address the hiring manager
  as a professional equal.

Output the complete email with greeting, body, and closing signature.
""".strip()

_SYSTEM_BY_TYPE = {
    "recruiter":      _RECRUITER_SYSTEM,
    "team_member":    _TEAM_MEMBER_SYSTEM,
    "hiring_manager": _HIRING_MANAGER_SYSTEM,
}


def email_generator(state: OutreachState) -> dict:
    """
    LangGraph node — generates a personalized outreach email
    for the target recipient type.
    """
    errors: list[str] = []
    debug_log: list[str] = []
    recipient_type = state["recipient_type"]

    debug_log.append(f"email_generator: generating email for recipient_type='{recipient_type}'")

    parsed_jd = state.get("parsed_jd")
    if parsed_jd is None:
        errors.append("email_generator: parsed_jd is None — cannot generate email")
        return {"generated_emails": [], "errors": errors, "debug_log": debug_log}

    system_prompt = _SYSTEM_BY_TYPE.get(recipient_type)
    if system_prompt is None:
        errors.append(f"email_generator: unknown recipient_type '{recipient_type}'")
        return {"generated_emails": [], "errors": errors, "debug_log": debug_log}

    user_message = _build_user_message(state, parsed_jd)
    personalization_signals = _collect_signals(state)

    try:
        email_body = chat(system=system_prompt, user=user_message, max_tokens=600)
    except Exception as exc:
        errors.append(f"email_generator: API call failed — {exc}")
        return {"generated_emails": [], "errors": errors, "debug_log": debug_log}

    word_count = len(email_body.split())

    generated_email: GeneratedEmail = {
        "recipient_type":           recipient_type,
        "to_name":                  state.get("contact_name"),
        "to_email":                 state.get("verified_email"),
        "body":                     email_body,
        "word_count":               word_count,
        "personalization_signals":  personalization_signals,
    }

    debug_log.append(
        f"email_generator: done — "
        f"word_count={word_count} "
        f"signals={personalization_signals}"
    )

    return {
        "generated_emails": [generated_email],
        "errors": errors,
        "debug_log": debug_log,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_user_message(state: OutreachState, parsed_jd: dict) -> str:
    """
    Assembles the user-turn prompt from all available state fields.
    Sections are only included when the relevant state is populated,
    so the prompt stays clean when optional fields are missing.
    """
    parts: list[str] = []

    # JD context
    parts.append(
        f"ROLE: {parsed_jd['role_title']} at {parsed_jd['company_name']}"
        + (f" ({parsed_jd['location']})" if parsed_jd.get("location") else "")
    )
    if parsed_jd.get("team_name"):
        parts.append(f"TEAM: {parsed_jd['team_name']}")
    if parsed_jd.get("responsibilities"):
        parts.append(
            "KEY RESPONSIBILITIES:\n"
            + "\n".join(f"- {r}" for r in parsed_jd["responsibilities"])
        )
    if parsed_jd.get("tone_signals"):
        parts.append(f"COMPANY TONE: {', '.join(parsed_jd['tone_signals'])}")

    # Candidate profile
    skills = state.get("relevant_skills") or []
    achievements = state.get("relevant_achievements") or []
    gaps = state.get("skill_gaps") or []

    if skills:
        parts.append(f"CANDIDATE RELEVANT SKILLS: {', '.join(skills)}")
    if achievements:
        parts.append(
            "CANDIDATE KEY ACHIEVEMENTS:\n"
            + "\n".join(f"- {a}" for a in achievements)
        )
    if gaps:
        parts.append(
            f"SKILL GAPS (handle gracefully — do not ignore, do not overclaim): "
            f"{', '.join(gaps)}"
        )

    # Contact info
    contact_name = state.get("contact_name")
    contact_title = state.get("contact_title")
    if contact_name:
        line = f"RECIPIENT NAME: {contact_name}"
        if contact_title:
            line += f" ({contact_title})"
        parts.append(line)

    # LinkedIn personalization signals
    linkedin: LinkedInContext | None = state.get("linkedin_context")
    if linkedin:
        signals: list[str] = []
        if linkedin.get("recent_posts"):
            signals.append(
                "Recent posts/articles: " + "; ".join(linkedin["recent_posts"])
            )
        if linkedin.get("notable_projects"):
            signals.append(
                "Notable projects: " + "; ".join(linkedin["notable_projects"])
            )
        if linkedin.get("shared_connections"):
            signals.append(
                "Shared connections: " + ", ".join(linkedin["shared_connections"])
            )
        if signals:
            parts.append(
                "LINKEDIN PERSONALIZATION SIGNALS (use at least one):\n"
                + "\n".join(f"- {s}" for s in signals)
            )

    return "\n\n".join(parts)


def _collect_signals(state: OutreachState) -> list[str]:
    """Build a list of personalization signal labels for the GeneratedEmail metadata."""
    signals: list[str] = []

    if state.get("contact_name"):
        signals.append("personalized greeting (contact name found)")
    if state.get("verified_email"):
        signals.append("verified email address found")

    linkedin = state.get("linkedin_context")
    if linkedin:
        if linkedin.get("recent_posts"):
            signals.append("LinkedIn recent post referenced")
        if linkedin.get("notable_projects"):
            signals.append("LinkedIn project referenced")
        if linkedin.get("shared_connections"):
            signals.append("shared connection referenced")

    skills = state.get("relevant_skills") or []
    for skill in skills[:3]:
        signals.append(f"matched skill: {skill}")

    if state.get("skill_gaps"):
        signals.append("skill gap acknowledged in tone")

    return signals
