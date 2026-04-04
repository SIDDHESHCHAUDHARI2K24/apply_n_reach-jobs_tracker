"""
eval/rubric.py
---------------
Scoring rubric for T1.5 — Prompt Evaluation Baseline.

Five dimensions, each scored 1–5 by the AI evaluator.
Human reviewers then validate or override each score.

Dimension definitions and scoring anchors are used both as
documentation and as the prompt sent to Claude for AI scoring.
"""

from __future__ import annotations
from typing import TypedDict


class RubricDimension(TypedDict):
    id: str
    name: str
    description: str        # what this dimension measures
    weight: float           # relative importance (must sum to 1.0)
    anchors: dict[int, str] # score → descriptor


RUBRIC: list[RubricDimension] = [
    {
        "id": "D1",
        "name": "Relevance",
        "description": (
            "How well does the email content align with the specific job description "
            "and the candidate's actual background? Does it reference the right role, "
            "company, and matching skills rather than being generic?"
        ),
        "weight": 0.25,
        "anchors": {
            1: "Generic — could apply to any job at any company. No specific JD or resume details used.",
            2: "Mentions the role or company but does not connect candidate background to requirements.",
            3: "Connects some candidate skills to the JD but misses the strongest matches.",
            4: "Clearly connects the best-matched skills and achievements to the JD requirements.",
            5: "Precisely tailored — every sentence earns its place. Strongest matches highlighted, company context woven in naturally.",
        },
    },
    {
        "id": "D2",
        "name": "Tone fit",
        "description": (
            "Does the email's tone match the intended recipient type? "
            "Recruiter emails should be concise and professional. "
            "Team member emails should be warm and genuinely curious. "
            "Hiring manager emails should be confident and peer-level."
        ),
        "weight": 0.25,
        "anchors": {
            1: "Tone is completely wrong for the recipient type (e.g. coffee-chat language in a recruiter email).",
            2: "Tone is mostly off — some correct signals but the overall feel doesn't match.",
            3: "Tone is roughly appropriate but generic — not distinctly recruiter/team-member/hiring-manager.",
            4: "Tone clearly matches the recipient type with only minor inconsistencies.",
            5: "Tone is exactly right — would feel natural and appropriate to the specific recipient.",
        },
    },
    {
        "id": "D3",
        "name": "Specificity",
        "description": (
            "Does the email include specific, concrete details — named skills, "
            "quantified achievements, or referenced LinkedIn signals — rather than "
            "vague generalities? Specificity is what separates a good outreach email "
            "from a template."
        ),
        "weight": 0.20,
        "anchors": {
            1: "Entirely vague — no specific skills, numbers, company details, or personal signals.",
            2: "One or two specifics but mostly filler phrases and generalities.",
            3: "Some concrete details but significant portions remain generic.",
            4: "Mostly specific — concrete skills and achievements present, minimal filler.",
            5: "Highly specific throughout — named skills, quantified impact, and personal signals all present.",
        },
    },
    {
        "id": "D4",
        "name": "Length appropriateness",
        "description": (
            "Is the email the right length for its recipient type? "
            "Recruiter: 150–200 words. Team member: 120–180 words. "
            "Hiring manager: 180–220 words. "
            "Penalize both over-long (rambling) and under-short (too thin)."
        ),
        "weight": 0.15,
        "anchors": {
            1: "Significantly outside the target range (more than 50 words over or under).",
            2: "Noticeably outside range (25–50 words over or under).",
            3: "Slightly outside range (10–25 words) or at the very edge of acceptable.",
            4: "Within target range with minor deviation (under 10 words).",
            5: "Exactly within the target range for the recipient type.",
        },
    },
    {
        "id": "D5",
        "name": "Call to action clarity",
        "description": (
            "Does the email end with a clear, specific, and low-friction call to action "
            "appropriate to the recipient type? Recruiter: ask to connect or learn more. "
            "Team member: ask for a 20-minute conversation. "
            "Hiring manager: propose a brief call to explore fit. "
            "Penalize vague CTAs ('let me know if you're interested') or missing CTAs."
        ),
        "weight": 0.15,
        "anchors": {
            1: "No call to action, or a passive statement ('I would love to hear back').",
            2: "Vague CTA — does not specify what action is being requested.",
            3: "CTA is present and clear but not tailored to the recipient type.",
            4: "CTA is clear and appropriate for the recipient type.",
            5: "CTA is specific, low-friction, and perfectly matched to the recipient type.",
        },
    },
]

# Total weight sanity check
assert abs(sum(d["weight"] for d in RUBRIC) - 1.0) < 0.001, \
    "Rubric weights must sum to 1.0"


def weighted_total(scores: dict[str, float]) -> float:
    """
    Compute the weighted total score from a dict of {dimension_id: score}.

    Args:
        scores: e.g. {"D1": 4, "D2": 5, "D3": 3, "D4": 4, "D5": 5}

    Returns:
        Weighted average on a 1–5 scale, rounded to 2 decimal places.
    """
    total = 0.0
    for dim in RUBRIC:
        score = scores.get(dim["id"], 0)
        total += score * dim["weight"]
    return round(total, 2)


def rubric_prompt_block() -> str:
    """
    Returns the rubric formatted as a prompt block for the AI evaluator.
    Injected into the scoring system prompt.
    """
    lines = ["SCORING RUBRIC (score each dimension 1–5):"]
    for dim in RUBRIC:
        lines.append(f"\n{dim['id']} — {dim['name']} (weight: {dim['weight']:.0%})")
        lines.append(f"  {dim['description']}")
        lines.append("  Anchors:")
        for score, anchor in dim["anchors"].items():
            lines.append(f"    {score}: {anchor}")
    return "\n".join(lines)
