"""
eval/run_eval.py
-----------------
T1.5 — Prompt Evaluation Runner

Runs the full evaluation pipeline:
  1. For each test case in test_cases.py, generate an outreach email
     using the real graph (nodes + LLM calls)
  2. Score the generated email using the AI evaluator (rubric.py)
  3. Write results to:
       eval/results/eval_results.csv     ← AI scores + human override columns
       eval/results/eval_report.md       ← Narrative report for academic submission

Usage:
    python -m eval.run_eval

    # Run a single test case for quick iteration:
    python -m eval.run_eval --id TC-01

    # Skip email generation (score pre-written emails from a JSON file):
    python -m eval.run_eval --from-file eval/results/generated_emails.json

Output files are written to eval/results/ (created if it doesn't exist).
"""

from __future__ import annotations

from pathlib import Path

# Load .env before any API calls
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

# Allow running as `python -m eval.run_eval` from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.test_cases import TEST_CASES, TestCase
from eval.rubric import RUBRIC, weighted_total
from eval.evaluator import EvalResult, evaluate_email

RESULTS_DIR = Path(__file__).parent / "results"


# ---------------------------------------------------------------------------
# Step 1 — Generate emails using the real graph
# ---------------------------------------------------------------------------

def generate_emails(test_cases: list[TestCase]) -> dict[str, str]:
    """
    Run each test case through the graph and return {test_case_id: email_body}.
    Saves generated emails to a JSON file so you can re-score without
    re-generating (API calls are expensive).
    """
    # Import here so the module loads even without langgraph installed
    from graph import graph
    from state import initial_state

    generated: dict[str, str] = {}

    for tc in test_cases:
        print(f"  Generating {tc['id']} — {tc['label']}...")
        config = {"configurable": {"thread_id": f"eval-{tc['id']}"}}

        state = initial_state(
            raw_jd=tc["raw_jd"],
            raw_resume=tc["raw_resume"],
            recipient_type=tc["recipient_type"],
        )
        if tc.get("linkedin_paste"):
            state["raw_linkedin_paste"] = tc["linkedin_paste"]  # type: ignore

        try:
            result = graph.invoke(state, config=config)
            emails = result.get("generated_emails") or []
            if emails:
                generated[tc["id"]] = emails[0]["body"]
                print(f"    OK — {len(emails[0]['body'].split())} words")
            else:
                generated[tc["id"]] = "[ERROR: no email generated]"
                print(f"    WARN — no email in result")
        except Exception as exc:
            generated[tc["id"]] = f"[ERROR: {exc}]"
            print(f"    ERROR — {exc}")

        # Small delay to avoid rate limits
        time.sleep(1)

    # Save to file for reuse
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RESULTS_DIR / "generated_emails.json"
    with open(cache_path, "w") as f:
        json.dump(generated, f, indent=2)
    print(f"\n  Saved generated emails to {cache_path}")

    return generated


# ---------------------------------------------------------------------------
# Step 2 — Score all emails
# ---------------------------------------------------------------------------

def score_emails(
    test_cases: list[TestCase],
    generated: dict[str, str],
) -> list[EvalResult]:
    """Score each generated email using the AI evaluator."""
    results: list[EvalResult] = []
    tc_map = {tc["id"]: tc for tc in test_cases}

    for tc_id, email_body in generated.items():
        tc = tc_map.get(tc_id)
        if tc is None:
            print(f"  WARN — no test case found for id '{tc_id}', skipping")
            continue

        if email_body.startswith("[ERROR"):
            print(f"  Skipping {tc_id} — email generation failed")
            from eval.evaluator import _error_result
            results.append(_error_result(tc, email_body, email_body))
            continue

        print(f"  Scoring {tc_id} — {tc['label']}...")
        result = evaluate_email(tc, email_body)
        results.append(result)

        if result.error:
            print(f"    ERROR — {result.error}")
        else:
            print(f"    AI score: {result.ai_weighted_total}/5.0")

        time.sleep(0.5)  # avoid rate limits

    return results


# ---------------------------------------------------------------------------
# Step 3 — Write CSV
# ---------------------------------------------------------------------------

def write_csv(results: list[EvalResult], path: Path) -> None:
    """
    Write results to CSV. Human override columns are included but empty —
    reviewers fill them in directly in the spreadsheet.
    """
    if not results:
        return

    fieldnames = list(results[0].to_dict().keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.to_dict())

    print(f"  CSV written: {path}")


# ---------------------------------------------------------------------------
# Step 4 — Write Markdown report
# ---------------------------------------------------------------------------

def write_markdown_report(results: list[EvalResult], path: Path) -> None:
    """
    Generate a Markdown report suitable for academic submission.
    Includes methodology, per-case results, and aggregate statistics.
    """
    now = datetime.now().strftime("%B %d, %Y")
    valid = [r for r in results if not r.error and r.ai_scores]

    lines: list[str] = [
        "# T1.5 — Prompt Evaluation Report",
        f"*Generated: {now}*",
        "",
        "---",
        "",
        "## 1. Overview",
        "",
        "This report documents the prompt evaluation baseline for the AI-Powered "
        "Outreach Email feature. Ten test cases covering three recipient types "
        "(recruiter, team_member, hiring_manager), three match levels "
        "(strong, partial, weak), and five industries were evaluated.",
        "",
        "Emails were generated using the production LangGraph pipeline and scored "
        "against a five-dimension rubric by an AI evaluator (Claude). Human reviewer "
        "override scores are recorded in the accompanying CSV file "
        "(`eval_results.csv`).",
        "",
        "---",
        "",
        "## 2. Rubric",
        "",
        "Each email is scored on five dimensions (1–5 scale):",
        "",
        "| ID | Dimension | Weight | Description |",
        "|---|---|---|---|",
    ]

    for dim in RUBRIC:
        lines.append(
            f"| {dim['id']} | {dim['name']} | {dim['weight']:.0%} | "
            f"{dim['description'][:80]}... |"
        )

    lines += [
        "",
        "The weighted total score is computed as: "
        "`Σ(score × weight)` across all dimensions, on a 1–5 scale.",
        "",
        "---",
        "",
        "## 3. Results Summary",
        "",
    ]

    if valid:
        avg_total = round(sum(r.ai_weighted_total for r in valid) / len(valid), 2)
        by_recipient: dict[str, list[float]] = {}
        by_match: dict[str, list[float]] = {}
        for r in valid:
            by_recipient.setdefault(r.recipient_type, []).append(r.ai_weighted_total)
            by_match.setdefault(r.match_level, []).append(r.ai_weighted_total)

        lines += [
            f"**Total test cases:** {len(results)}  ",
            f"**Successfully evaluated:** {len(valid)}  ",
            f"**Overall AI average score:** {avg_total} / 5.0",
            "",
            "### Average score by recipient type",
            "",
            "| Recipient type | Cases | Avg AI score |",
            "|---|---|---|",
        ]
        for rtype, scores in sorted(by_recipient.items()):
            avg = round(sum(scores) / len(scores), 2)
            lines.append(f"| {rtype} | {len(scores)} | {avg} |")

        lines += [
            "",
            "### Average score by match level",
            "",
            "| Match level | Cases | Avg AI score |",
            "|---|---|---|",
        ]
        for mlevel, scores in sorted(by_match.items()):
            avg = round(sum(scores) / len(scores), 2)
            lines.append(f"| {mlevel} | {len(scores)} | {avg} |")

    lines += [
        "",
        "---",
        "",
        "## 4. Per-Case Results",
        "",
    ]

    for r in results:
        lines += [
            f"### {r.test_case_id} — {r.label}",
            "",
            f"- **Recipient type:** {r.recipient_type}",
            f"- **Match level:** {r.match_level}",
            f"- **Word count:** {r.word_count}",
            f"- **AI weighted total:** {r.ai_weighted_total} / 5.0",
            "",
        ]

        if r.error:
            lines += [f"**Error:** {r.error}", ""]
            continue

        lines += [
            "**AI dimension scores:**",
            "",
            "| Dimension | AI score | Rationale |",
            "|---|---|---|",
        ]
        for dim in RUBRIC:
            did = dim["id"]
            score = r.ai_scores.get(did, "—")
            rationale = r.ai_rationale.get(did, "").replace("|", "\\|")
            lines.append(f"| {dim['name']} | {score} | {rationale} |")

        lines += [
            "",
            f"**Overall notes:** {r.overall_notes}",
            "",
            "**Generated email:**",
            "",
            "```",
            r.email_body,
            "```",
            "",
            "---",
            "",
        ]

    lines += [
        "## 5. Methodology Notes",
        "",
        "- All emails were generated using `claude-3-5-sonnet-20241022` via the "
        "production LangGraph pipeline.",
        "- Scoring was performed by a separate `claude-3-5-sonnet-20241022` instance "
        "acting as an independent evaluator — different system prompt, no access to "
        "the generation prompt.",
        "- Human reviewer override scores are recorded in `eval_results.csv`. "
        "Where human and AI scores differ by more than 1 point, the human score "
        "takes precedence for final reporting.",
        "- This evaluation covers the email generation quality only. Apollo contact "
        "lookup was bypassed during evaluation to isolate generation quality from "
        "data availability.",
        "",
        "*End of report*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown report written: {path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="T1.5 — Run prompt evaluation for the outreach email feature"
    )
    parser.add_argument(
        "--id",
        help="Run a single test case by ID (e.g. TC-01). Runs all if omitted.",
    )
    parser.add_argument(
        "--from-file",
        help="Path to a generated_emails.json file. Skips generation, scores only.",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Load generated_emails.json from the default cache path and score only.",
    )
    args = parser.parse_args()

    # Filter test cases
    test_cases = TEST_CASES
    if args.id:
        test_cases = [tc for tc in TEST_CASES if tc["id"] == args.id]
        if not test_cases:
            print(f"No test case found with id '{args.id}'")
            sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Generate or load emails ---
    cache_path = RESULTS_DIR / "generated_emails.json"
    from_file = args.from_file or (cache_path if args.score_only else None)

    if from_file and Path(from_file).exists():
        print(f"\nLoading generated emails from {from_file}...")
        with open(from_file) as f:
            generated = json.load(f)
        # Filter to requested test cases only
        tc_ids = {tc["id"] for tc in test_cases}
        generated = {k: v for k, v in generated.items() if k in tc_ids}
    else:
        print(f"\nStep 1 — Generating emails ({len(test_cases)} test cases)...")
        generated = generate_emails(test_cases)

    # --- Step 2: Score ---
    print(f"\nStep 2 — Scoring {len(generated)} emails...")
    results = score_emails(test_cases, generated)

    # --- Step 3: Write outputs ---
    print("\nStep 3 — Writing outputs...")
    write_csv(results, RESULTS_DIR / "eval_results.csv")
    write_markdown_report(results, RESULTS_DIR / "eval_report.md")

    # --- Summary ---
    valid = [r for r in results if not r.error and r.ai_scores]
    if valid:
        avg = round(sum(r.ai_weighted_total for r in valid) / len(valid), 2)
        print(f"\nDone. {len(valid)}/{len(results)} evaluated successfully.")
        print(f"Overall AI average score: {avg} / 5.0")
    else:
        print("\nDone. No valid results to summarize.")

    print(f"Results in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
