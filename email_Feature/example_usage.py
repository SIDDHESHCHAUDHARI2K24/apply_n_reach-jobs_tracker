"""
example_usage.py
-----------------
End-to-end example of the outreach email graph — two-invocation flow.

Run this file directly to see the graph in action with sample data:
    python example_usage.py

Or pass a recipient type as a CLI argument:
    python example_usage.py team_member
    python example_usage.py hiring_manager

Requirements:
    pip install -r requirements.txt

Environment variables (add to .env file at project root):
    ANTHROPIC_API_KEY=your_key
    APOLLO_API_KEY=your_key   # optional — graph handles missing key gracefully
"""

from __future__ import annotations

# Load .env file before any other imports so API keys are available
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

import sys
from graph import graph
from state import initial_state


# ---------------------------------------------------------------------------
# Sample inputs
# ---------------------------------------------------------------------------

SAMPLE_JD = """
Senior Machine Learning Engineer — Stripe

We're looking for a Senior ML Engineer to join our Risk & Fraud team in
San Francisco (remote-friendly). You'll build and maintain production ML
models that process millions of transactions per day, with a focus on
reducing false positives while catching emerging fraud patterns.

What you'll do:
- Design, train, and deploy ML models at scale using Python and PyTorch
- Build and maintain real-time feature pipelines in Kafka and BigQuery
- Collaborate with data scientists, engineers, and product managers
- Own model performance end-to-end — from experimentation to production monitoring

What we're looking for:
- 4+ years of ML engineering experience in a production environment
- Strong Python and PyTorch (or TensorFlow) skills
- Experience with streaming data pipelines (Kafka, Flink, or similar)
- Familiarity with Kubernetes and containerized ML workloads
- SQL / BigQuery proficiency
- Excellent communication skills across technical and non-technical stakeholders
"""

SAMPLE_RESUME = """
Alex Rivera — Senior ML Engineer
alex.rivera@email.com | linkedin.com/in/alexrivera

EXPERIENCE

ML Engineer, DataCo (2021–present)
- Built real-time fraud detection pipeline processing 20M+ events/day using Python,
  Kafka, and BigQuery — reduced false positive rate by 34%
- Trained and deployed 6 production PyTorch models, improving F1 score by 18%
  vs. previous rule-based system
- Led migration of batch ML jobs to Kubernetes-based microservices, cutting
  inference latency by 60%
- Mentored 3 junior engineers on ML best practices and code review

Data Scientist, StartupX (2019–2021)
- Built recommendation engine in Python/scikit-learn serving 500K daily active users
- Designed A/B testing framework that reduced experiment cycle time by 40%

SKILLS
Python, PyTorch, TensorFlow, Kafka, BigQuery, SQL, Kubernetes, Docker,
scikit-learn, MLflow, Airflow, dbt

EDUCATION
M.S. Computer Science (Machine Learning), Purdue University, 2019
B.S. Statistics, University of Illinois, 2017
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(result: dict) -> None:
    """Pretty-prints the key fields from a graph result snapshot."""

    # Generated email
    emails = result.get("generated_emails") or []
    if emails:
        email = emails[0]
        print_section("Generated email")
        print(f"  Recipient type : {email['recipient_type']}")
        print(f"  To             : {email.get('to_name', 'N/A')} "
              f"<{email.get('to_email', 'no email found')}>")
        print(f"  Word count     : {email['word_count']}")
        print(f"  Signals        : {', '.join(email['personalization_signals']) or 'none'}")
        print(f"\n{email['body']}")
    else:
        print("\n  [No email generated]")

    # Subject lines
    subject_sets = result.get("subject_lines") or []
    if subject_sets:
        print_section("Subject line options")
        for i, option in enumerate(subject_sets[0]["options"], 1):
            print(f"  {i}. {option}")

    # Follow-up draft
    followups = result.get("followup_drafts") or []
    if followups:
        fu = followups[0]
        print_section(f"Follow-up draft (send after {fu['suggested_send_after_days']} days)")
        print(fu["body"])

    # Apollo result summary
    apollo = result.get("apollo_result")
    if apollo:
        print_section("Apollo contact lookup")
        print(f"  Found          : {apollo['found']}")
        print(f"  Name           : {apollo.get('full_name', 'N/A')}")
        print(f"  Title          : {apollo.get('title', 'N/A')}")
        print(f"  Email status   : {apollo.get('email_status', 'N/A')}")
        print(f"  Source         : {apollo.get('source', 'N/A')}")

    # Errors / warnings
    errors = result.get("errors") or []
    if errors:
        print_section("Warnings / errors")
        for e in errors:
            print(f"  ⚠  {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_example(recipient_type: str = "recruiter") -> None:
    """
    Runs the full two-invocation outreach graph flow.

    Args:
        recipient_type: one of "recruiter" | "team_member" | "hiring_manager"
    """
    # Thread config — unique per job application + user combination.
    # Reusing the same thread_id resumes an existing interrupted graph.
    config = {"configurable": {"thread_id": "example-thread-001"}}

    # ------------------------------------------------------------------
    # INVOCATION 1 — runs until HITL interrupt before export_node
    # ------------------------------------------------------------------
    print_section(f"INVOCATION 1 — running graph (recipient: {recipient_type})")

    state = initial_state(
        raw_jd=SAMPLE_JD,
        raw_resume=SAMPLE_RESUME,
        recipient_type=recipient_type,
    )

    result = graph.invoke(state, config=config)
    print_result(result)

    # ------------------------------------------------------------------
    # INVOCATION 2 — simulate user reviewing and confirming the email
    # ------------------------------------------------------------------
    print_section("INVOCATION 2 — resuming after user review (simulated)")

    emails = result.get("generated_emails") or []
    subject_sets = result.get("subject_lines") or []

    # Simulate user accepting the AI output as-is (no edits)
    user_edits = [
        {
            "recipient_type": recipient_type,
            "edited_body": emails[0]["body"] if emails else "",
            "edited_subject": subject_sets[0]["options"][0] if subject_sets else "",
            "reset_to_ai": False,
        }
    ]

    final_result = graph.invoke({"user_edits": user_edits}, config=config)

    print(f"\n  outreach_status : {final_result.get('outreach_status')}")
    final_emails = final_result.get("generated_emails") or []
    if final_emails:
        print(f"  final word count: {final_emails[0]['word_count']}")

    print_section("Debug log (last 8 entries)")
    for entry in (final_result.get("debug_log") or [])[-8:]:
        print(f"  {entry}")

    print("\n  Done.\n")


if __name__ == "__main__":
    # Optionally pass recipient type as a CLI argument:
    #   python example_usage.py team_member
    #   python example_usage.py hiring_manager
    recipient = sys.argv[1] if len(sys.argv) > 1 else "recruiter"

    valid = {"recruiter", "team_member", "hiring_manager"}
    if recipient not in valid:
        print(f"Invalid recipient type '{recipient}'. Choose from: {', '.join(valid)}")
        sys.exit(1)

    run_example(recipient_type=recipient)
