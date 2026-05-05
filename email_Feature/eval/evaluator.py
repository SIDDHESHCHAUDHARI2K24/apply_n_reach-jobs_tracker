"""
eval/evaluator.py
------------------
AI-assisted evaluator for T1.5 — Prompt Evaluation Baseline.

For each test case:
  1. Generates the outreach email using the graph (or accepts pre-generated text)
  2. Sends the email + rubric to Claude for scoring
  3. Returns a structured EvalResult with AI scores and rationale

Human reviewers then fill in override scores in the CSV output.
"""

from __future__ import annotations

import json
import time
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import chat
from eval.rubric import RUBRIC, rubric_prompt_block, weighted_total
from eval.test_cases import TestCase

_EVALUATOR_SYSTEM = """
You are an expert evaluator of professional outreach emails for job seekers.
You will be given a generated outreach email along with the context used to
produce it (job description, resume, recipient type).

Score the email on each rubric dimension from 1 to 5 using the anchors provided.
Be strict and honest — a score of 3 means acceptable but not good.
A score of 5 should be genuinely hard to earn.

Return ONLY a valid JSON object with this exact shape:
{
  "scores": {
    "D1": <int 1-5>,
    "D2": <int 1-5>,
    "D3": <int 1-5>,
    "D4": <int 1-5>,
    "D5": <int 1-5>
  },
  "rationale": {
    "D1": "<one sentence explaining this score>",
    "D2": "<one sentence explaining this score>",
    "D3": "<one sentence explaining this score>",
    "D4": "<one sentence explaining this score>",
    "D5": "<one sentence explaining this score>"
  },
  "overall_notes": "<2-3 sentences: what works well, what could improve>",
  "word_count": <int>
}

No preamble, no markdown, no explanation outside the JSON.
""".strip()


class EvalResult:
    """Stores scores, rationale, and metadata for one evaluated email."""

    def __init__(
        self,
        test_case_id: str,
        label: str,
        recipient_type: str,
        match_level: str,
        email_body: str,
        ai_scores: dict[str, int],
        ai_rationale: dict[str, str],
        overall_notes: str,
        word_count: int,
        error: Optional[str] = None,
    ):
        self.test_case_id = test_case_id
        self.label = label
        self.recipient_type = recipient_type
        self.match_level = match_level
        self.email_body = email_body
        self.ai_scores = ai_scores
        self.ai_rationale = ai_rationale
        self.overall_notes = overall_notes
        self.word_count = word_count
        self.error = error
        self.ai_weighted_total = weighted_total(ai_scores) if ai_scores else 0.0

        # Human override fields — filled in later via CSV
        self.human_scores: dict[str, Optional[int]] = {d["id"]: None for d in RUBRIC}
        self.human_weighted_total: Optional[float] = None
        self.human_notes: str = ""

    def to_dict(self) -> dict:
        """Serialize to a flat dict for CSV export."""
        row = {
            "test_case_id":        self.test_case_id,
            "label":               self.label,
            "recipient_type":      self.recipient_type,
            "match_level":         self.match_level,
            "word_count":          self.word_count,
            "ai_weighted_total":   self.ai_weighted_total,
            "human_weighted_total": self.human_weighted_total or "",
            "overall_notes":       self.overall_notes,
            "error":               self.error or "",
            "email_body_preview":  self.email_body[:120].replace("\n", " ") + "...",
        }
        for dim in RUBRIC:
            did = dim["id"]
            row[f"ai_{did}"]        = self.ai_scores.get(did, "")
            row[f"human_{did}"]     = self.human_scores.get(did) or ""
            row[f"rationale_{did}"] = self.ai_rationale.get(did, "")
        return row


def evaluate_email(
    test_case: TestCase,
    email_body: str,
) -> EvalResult:
    """
    Score a single generated email against the rubric using Claude.

    Args:
        test_case:   The TestCase this email was generated for.
        email_body:  The generated email text to evaluate.

    Returns:
        An EvalResult with AI scores, rationale, and metadata.
    """
    user_message = _build_eval_prompt(test_case, email_body)

    try:
        raw_json = chat(
            system=_EVALUATOR_SYSTEM + "\n\n" + rubric_prompt_block(),
            user=user_message,
            max_tokens=1024,
        )
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return _error_result(test_case, email_body, f"JSON parse error: {exc}")
    except Exception as exc:
        return _error_result(test_case, email_body, f"API error: {exc}")

    scores = {k: int(v) for k, v in data.get("scores", {}).items()}
    rationale = data.get("rationale", {})
    overall_notes = data.get("overall_notes", "")
    word_count = data.get("word_count", len(email_body.split()))

    return EvalResult(
        test_case_id=test_case["id"],
        label=test_case["label"],
        recipient_type=test_case["recipient_type"],
        match_level=test_case["match_level"],
        email_body=email_body,
        ai_scores=scores,
        ai_rationale=rationale,
        overall_notes=overall_notes,
        word_count=word_count,
    )


def _build_eval_prompt(test_case: TestCase, email_body: str) -> str:
    parts = [
        f"RECIPIENT TYPE: {test_case['recipient_type']}",
        f"MATCH LEVEL: {test_case['match_level']}",
        "",
        "JOB DESCRIPTION:",
        test_case["raw_jd"],
        "",
        "RESUME:",
        test_case["raw_resume"],
    ]
    if test_case.get("linkedin_paste"):
        parts += ["", "LINKEDIN CONTEXT PROVIDED:", test_case["linkedin_paste"]]
    parts += ["", "GENERATED EMAIL TO EVALUATE:", email_body]
    return "\n".join(parts)


def _error_result(test_case: TestCase, email_body: str, error: str) -> EvalResult:
    return EvalResult(
        test_case_id=test_case["id"],
        label=test_case["label"],
        recipient_type=test_case["recipient_type"],
        match_level=test_case["match_level"],
        email_body=email_body,
        ai_scores={},
        ai_rationale={},
        overall_notes="",
        word_count=len(email_body.split()),
        error=error,
    )
