"""
nodes/resume_extractor.py
--------------------------
Node: resume_extractor

Reads:  state["raw_resume"]
        state["parsed_jd"]   (required — run after jd_parser)
Writes: state["relevant_skills"]
        state["relevant_achievements"]
        state["skill_gaps"]
        state["errors"]
        state["debug_log"]

Selects the most relevant skills and achievements from the resume
relative to the parsed JD. Also identifies skill gaps — skills the JD
requires that are absent or unverified in the resume. These gaps are
passed to the email generator to handle gracefully in tone rather than
ignore or overclaim.
"""

from __future__ import annotations

import json

from app.features.job_tracker.email_agent.state import EmailAgentState
from app.features.job_tracker.email_agent.nodes import _chat

_SYSTEM = """
You are a resume analyst. Given a resume and a structured job description,
extract the most relevant information for writing a personalized outreach email.

Return ONLY a valid JSON object — no preamble, no markdown, no explanation.

Return this exact shape:
{
  "relevant_skills": ["string", ...],
  "relevant_achievements": ["string", ...],
  "skill_gaps": ["string", ...]
}

Rules:
- relevant_skills: up to 6 skills from the resume that best match the JD's
  required_skills. Prefer skills that appear in both the resume AND the JD.
  Use the exact skill name as it appears in the JD where possible.
- relevant_achievements: up to 5 resume bullet points or project descriptions
  that demonstrate impact relevant to the JD responsibilities. Prefer
  quantified achievements (numbers, percentages, scale). Keep each under
  20 words — summarize if needed.
- skill_gaps: skills listed in the JD required_skills that are absent or
  not clearly demonstrated in the resume. Max 5 items. Empty list if none.
""".strip()


async def resume_extractor(state: EmailAgentState) -> dict:
    """
    LangGraph node — extracts relevant skills and achievements from the resume
    relative to the parsed job description.
    """
    errors: list[str] = []
    debug_log: list[str] = []

    debug_log.append("resume_extractor: starting extraction")

    parsed_jd = state.get("parsed_jd")
    if parsed_jd is None:
        errors.append("resume_extractor: parsed_jd is None — jd_parser may have failed")
        return {
            "relevant_skills": [],
            "relevant_achievements": [],
            "skill_gaps": [],
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }

    jd_summary = (
        f"Role: {parsed_jd['role_title']} at {parsed_jd['company_name']}\n"
        f"Required skills: {', '.join(parsed_jd['required_skills']) or 'not specified'}\n"
        f"Key responsibilities:\n"
        + "\n".join(f"- {r}" for r in parsed_jd["responsibilities"])
    )

    user_message = (
        f"RESUME:\n{state['raw_resume']}\n\n"
        f"JOB DESCRIPTION (structured):\n{jd_summary}"
    )

    try:
        raw_json = await _chat(system=_SYSTEM, user=user_message, max_tokens=1024)
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"resume_extractor: LLM returned invalid JSON — {exc}")
        return {
            "relevant_skills": [],
            "relevant_achievements": [],
            "skill_gaps": [],
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }
    except Exception as exc:
        errors.append(f"resume_extractor: API call failed — {exc}")
        return {
            "relevant_skills": [],
            "relevant_achievements": [],
            "skill_gaps": [],
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }

    relevant_skills: list[str] = data.get("relevant_skills", [])
    relevant_achievements: list[str] = data.get("relevant_achievements", [])
    skill_gaps: list[str] = data.get("skill_gaps", [])

    if skill_gaps:
        errors.append(
            f"resume_extractor: skill gaps present — "
            f"email generator will apply gap-acknowledgment tone for: {skill_gaps}"
        )

    debug_log.append(
        f"resume_extractor: "
        f"skills={len(relevant_skills)} "
        f"achievements={len(relevant_achievements)} "
        f"gaps={len(skill_gaps)}"
    )

    return {
        "relevant_skills": relevant_skills,
        "relevant_achievements": relevant_achievements,
        "skill_gaps": skill_gaps,
        "errors": state.get("errors", []) + errors,
        "debug_log": state.get("debug_log", []) + debug_log,
    }
