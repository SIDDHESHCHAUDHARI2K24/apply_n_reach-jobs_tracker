"""
End-to-end test harness for the Resume AI Agent.

Reads Siddhesh Chaudhari's resume PDF, sets up a clean DB environment,
runs the LangGraph agent against a PM job description, and asserts
quality gates with a final report card.

Usage:
    uv run python scripts/test_resume_agent.py
    uv run python scripts/test_resume_agent.py --pdf "../resume/Siddhesh Chaudhari PM Resume.pdf"
    uv run python scripts/test_resume_agent.py --output tailored_resume.pdf
    uv run python scripts/test_resume_agent.py --keep-data      # don't delete test rows after run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── Path setup ────────────────────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
RESUME_DIR  = BACKEND_DIR.parent / "resume"
DEFAULT_PDF = RESUME_DIR / "Siddhesh Chaudhari PM Resume.pdf"

sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

TEXLIVE_BIN = os.environ.get("TEXLIVE_BIN", r"C:\texlive\2026\bin\windows")
if TEXLIVE_BIN and TEXLIVE_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = TEXLIVE_BIN + os.pathsep + os.environ.get("PATH", "")

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

# ── Colours (no external lib needed) ─────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg: str)   -> str: return f"{GREEN}✔  {msg}{RESET}"
def fail(msg: str) -> str: return f"{RED}✘  {msg}{RESET}"
def warn(msg: str) -> str: return f"{YELLOW}⚠  {msg}{RESET}"
def info(msg: str) -> str: return f"{CYAN}   {msg}{RESET}"


# ── Job description for this test run ────────────────────────────────────────
# Product Manager @ LangChain — realistic PM role that maps well to Siddhesh's background.
JOB_EXTRACTED = {
    "job_title":           "Product Manager, LangSmith",
    "company_name":        "LangChain",
    "location":            "Remote-friendly (USA)",
    "employment_type":     "Full-time",
    "experience_level":    "Senior",
    "description_summary": (
        "LangChain is hiring a PM to own key areas of LangSmith, an observability, evals, "
        "and deployment platform that makes shipping reliable AI systems possible. The role "
        "sits at the intersection of UX and production infrastructure for AI developers."
    ),
    "role_summary": (
        "Own the LangSmith product roadmap; partner with engineering and founders to ship "
        "features that help developers move AI prototypes into production."
    ),
    "problem_being_solved": (
        "Developers lack reliable tooling to debug, evaluate, and deploy AI agents at scale. "
        "This PM will close that gap with observability and evaluation features inside LangSmith."
    ),
    "required_skills": [
        "3+ years product management or engineering experience",
        "Developer tools or technical SaaS platforms",
        "Cross-functional team alignment",
        "API design and system architecture understanding",
        "Strong written and verbal communication",
    ],
    "preferred_skills": [
        "CS/Engineering background",
        "High-growth or developer-focused startup experience",
        "Hands-on LLM / AI agent development",
    ],
    "technical_keywords": [
        "LangSmith", "LangGraph", "LLMs", "AI agents", "Python",
        "API design", "data pipelines", "observability", "evals",
        "developer tools", "prompt engineering",
    ],
    "sector_keywords": [
        "AI/ML infrastructure", "developer tools", "SaaS", "Series B startup",
    ],
    "business_sectors": ["AI Infrastructure", "Developer Tools", "Enterprise SaaS"],
    "useful_experiences": [
        "Led cross-functional teams to ship technical/developer-facing products",
        "Defined product roadmaps and OKRs for platform products",
        "Worked with LLMs, agents, or data pipelines in production",
        "Managed agile backlogs through full development lifecycle",
        "Built or owned API-first / infrastructure products",
    ],
}

# ── Siddhesh's profile (sourced from the PDF at runtime, stored here as ground-truth) ─
SIDDHESH_PROFILE = {
    "personal": {
        "full_name":     "Siddhesh Chaudhari",
        "email":         "s.chaudhari2k24@gmail.com",
        "phone":         "(765) 607 8799",
        "location":      "West Lafayette, IN",
        "linkedin_url":  "https://www.linkedin.com/in/siddhesh-chaudhari",
        "github_url":    "https://github.com/SHADOWDRAGON2K01",
        "portfolio_url": None,
        "summary": (
            "TPM with 3 years' experience developing software products & leading end-to-end "
            "projects across Enterprise, Finance, and AdTech. Open to relocate."
        ),
    },
    "education": [
        {
            "university_name":  "Purdue University",
            "major":            "Engineering Management (Product / Data)",
            "degree_type":      "Master of Science",
            "start_month_year": "08/2024",
            "end_month_year":   "05/2026",
            "bullet_points": [
                "GPA: 3.6 / 4.0 — Courses: Corporate Consulting, Technical Product Management, Business Analytics, Entrepreneurship & Business Strategy",
                "Developing Voice Agents & UI Navigation Agentic Workflows for Job Application Automation with Python, Livekit, LangGraph & React",
            ],
        },
        {
            "university_name":  "University of Mumbai (VJTI)",
            "major":            "Engineering",
            "degree_type":      "Bachelor of Technology",
            "start_month_year": "08/2018",
            "end_month_year":   "05/2022",
            "bullet_points": ["GPA: 3.6 / 4.0"],
        },
    ],
    "experiences": [
        {
            "role_title":       "Product Developer / Team Lead",
            "company_name":     "Feenix Group – Purdue Data Mine",
            "start_month_year": "08/2025",
            "end_month_year":   None,
            "context": (
                "Scoped To-be Features through Requirements Gathering Workshops & drafted a roadmap to develop "
                "6 main features around in-game accessories creation, ads management & user interaction platform "
                "to programmatically perform marketing & interactive branding inside Roblox Games. "
                "Designed system architectures, UI/UX & data flows & developed the prototype (Backend, API "
                "Gateway, Roblox Scripting) using React, Python FastAPI, Lua, automating the entire Ads "
                "Management, Interaction Data Logging & Analytics with a team of 6."
            ),
        },
        {
            "role_title":       "Technical Program Manager",
            "company_name":     "Boxsy – Purdue Data Mine",
            "start_month_year": "08/2025",
            "end_month_year":   "12/2025",
            "context": (
                "Led a team of 14 to streamline development & achieve 4 OKRs by setting up 3 sub-teams for "
                "6 Integrations, 7 AI Agent Developments & JIRA-Github-Vercel CI-CD pipelines, prioritizing "
                "over 3 Epics with 30+ user stories. KPIs Tracked: Development Speed, AI Accuracy."
            ),
        },
        {
            "role_title":       "Venture Capital & Venture Studio Intern",
            "company_name":     "Launch Factory",
            "start_month_year": "08/2025",
            "end_month_year":   "12/2025",
            "context": (
                "Assisted VC arm to scout (Data, Productivity) & facilitate due diligence with market insight "
                "for investment decisions. Consulted 5+ portfolio startups for Tech, GTM & Partnerships. "
                "Maintained CRM dashboards & data automations using n8n & Python."
            ),
        },
        {
            "role_title":       "Technical Program Manager",
            "company_name":     "Evonik – Purdue Data Mine",
            "start_month_year": "01/2025",
            "end_month_year":   "05/2025",
            "context": (
                "Delivered PoC (later adopted & deployed on Evonik's private cloud) directing a 10-person team "
                "through 8 sprints, reducing on-site risks & cutting compatibility research time by over 96% "
                "from 30 min to <1 min. Led requirements analysis & design workshops to determine 3 key "
                "pain-points, OKRs, KPIs & developer efforts. Owned development lifecycle of React & FastAPI "
                "web app, shipping 12 features & consolidating 870,000 data points."
            ),
        },
        {
            "role_title":       "Technical Project Manager",
            "company_name":     "Microsoft – Purdue Data Mine",
            "start_month_year": "08/2024",
            "end_month_year":   "12/2024",
            "context": (
                "Led 5-member team through 8-sprint agile cycle to deliver PoC on schedule, overseeing "
                "30-item product backlog from ideation to deployment. Designed end-to-end sentiment analysis "
                "pipeline processing 1,000 images & 240 videos from 3 media sources, boosting insight "
                "accuracy by 40%. Automated contextual analysis with 4 distinct LLMs, cutting computation "
                "time by 1-2 hours per cycle with auto-translate for broader dataset coverage."
            ),
        },
        {
            "role_title":       "Technology Consultant",
            "company_name":     "PwC (PricewaterhouseCoopers)",
            "start_month_year": "07/2022",
            "end_month_year":   "07/2024",
            "context": (
                "Orchestrated end-to-end SAP Vendor Invoice Management implementations for 3 clients, "
                "delivering 27 custom workflows that enhanced invoice KPIs by 40% & cut cost-per-invoice "
                "to <$4. Directed team of 5 analysts shipping 48 features with 90% improvement in process "
                "automation. Led 6 design workshops & authored 32 technical documents, cutting post-launch "
                "tickets by 60% and signing off 2 weeks ahead of schedule."
            ),
        },
    ],
    "skills": [
        # technical
        ("technical", "Python"),
        ("technical", "SQL"),
        ("technical", "TypeScript"),
        ("technical", "LangChain / LangGraph"),
        ("technical", "FastAPI"),
        ("technical", "PostgreSQL"),
        ("technical", "AWS"),
        ("technical", "Databricks / PySpark"),
        ("technical", "Figma"),
        ("technical", "Jira"),
        ("technical", "Git"),
        ("technical", "RAG / LLMs"),
        ("technical", "n8n"),
        ("technical", "SAP ABAP"),
        ("technical", "Tableau"),
        # competency
        ("competency", "Technical Product Management"),
        ("competency", "Project & Stakeholder Management"),
        ("competency", "System Design"),
        ("competency", "UI/UX Design"),
        ("competency", "Business Documentation"),
        ("competency", "Workflow Automation"),
        ("competency", "Agile / Scrum"),
        # AI tools
        ("ai_tools", "Claude Code"),
        ("ai_tools", "Langchain / Langgraph"),
        ("ai_tools", "HuggingFace"),
        ("ai_tools", "n8n"),
        ("ai_tools", "Replit / Lovable"),
    ],
}


# ── Data class for test result tracking ───────────────────────────────────────
@dataclass
class Assertion:
    name:    str
    passed:  bool
    detail:  str = ""


@dataclass
class TestRun:
    user_id:    int = 0
    opening_id: int = 0
    run_id:     int = 0
    profile_id: int = 0
    events:     list[dict] = field(default_factory=list)
    nodes_seen: set[str]   = field(default_factory=set)
    assertions: list[Assertion] = field(default_factory=list)
    start_time: float = 0.0
    elapsed:    float = 0.0
    pdf_bytes:  bytes | None = None

    def assert_that(self, name: str, condition: bool, detail: str = "") -> None:
        self.assertions.append(Assertion(name, condition, detail))

    @property
    def passed(self) -> int:
        return sum(1 for a in self.assertions if a.passed)

    @property
    def failed_list(self) -> list[Assertion]:
        return [a for a in self.assertions if not a.passed]


# ── PDF reader ────────────────────────────────────────────────────────────────
def read_pdf_text(pdf_path: Path) -> str:
    """Extract raw text from a PDF using pypdf (bundled with the project)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except ImportError:
        return "(pypdf not available — skipping PDF text extraction)"
    except Exception as exc:
        return f"(PDF read error: {exc})"


def validate_pdf_matches_profile(pdf_text: str, result: TestRun) -> None:
    """Spot-check that the PDF text contains expected identity markers."""
    checks = [
        ("Siddhesh Chaudhari",         "Full name present in PDF"),
        ("PwC",                        "PwC experience present in PDF"),
        ("Microsoft",                  "Microsoft experience present in PDF"),
        ("Purdue",                     "Purdue education present in PDF"),
        ("LangGraph",                  "LangGraph skill present in PDF"),
    ]
    for needle, label in checks:
        result.assert_that(f"PDF content — {label}", needle in pdf_text, needle)


# ── DB setup helpers ──────────────────────────────────────────────────────────
async def _setup_profile(conn, user_id: int) -> int:
    """Insert job profile with all sections. Returns profile_id."""
    import uuid
    profile = await conn.fetchrow(
        "INSERT INTO job_profiles (user_id, profile_name, target_role) VALUES ($1,$2,$3) RETURNING *",
        user_id,
        f"Siddhesh – TPM / PM [{uuid.uuid4().hex[:6]}]",
        "Technical Product Manager",
    )
    profile_id = profile["id"]

    p = SIDDHESH_PROFILE["personal"]
    await conn.execute(
        """INSERT INTO job_profile_personal_details
           (job_profile_id, full_name, email, phone, location, linkedin_url, github_url, portfolio_url, summary)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
        profile_id,
        p["full_name"], p["email"], p["phone"], p["location"],
        p["linkedin_url"], p["github_url"], p["portfolio_url"], p["summary"],
    )

    for edu in SIDDHESH_PROFILE["education"]:
        await conn.execute(
            """INSERT INTO job_profile_educations
               (job_profile_id, university_name, major, degree_type,
                start_month_year, end_month_year, bullet_points, reference_links)
               VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,'[]'::jsonb)""",
            profile_id,
            edu["university_name"], edu["major"], edu["degree_type"],
            edu["start_month_year"], edu["end_month_year"],
            json.dumps(edu.get("bullet_points", [])),
        )

    for exp in SIDDHESH_PROFILE["experiences"]:
        await conn.execute(
            """INSERT INTO job_profile_experiences
               (job_profile_id, role_title, company_name, start_month_year, end_month_year,
                context, work_sample_links, bullet_points)
               VALUES ($1,$2,$3,$4,$5,$6,'[]'::jsonb,'[]'::jsonb)""",
            profile_id,
            exp["role_title"], exp["company_name"],
            exp["start_month_year"], exp["end_month_year"],
            exp["context"],
        )

    for i, (kind, name) in enumerate(SIDDHESH_PROFILE["skills"]):
        await conn.execute(
            "INSERT INTO job_profile_skill_items (job_profile_id, kind, name, sort_order) VALUES ($1,$2,$3,$4)",
            profile_id, kind, name, i,
        )

    return profile_id


async def _setup_opening_and_extraction(conn, user_id: int) -> int:
    """Create a job opening and insert pre-built extracted details. Returns opening_id."""
    opening = await conn.fetchrow(
        "INSERT INTO job_openings (user_id, company_name, role_name, source_url) VALUES ($1,$2,$3,$4) RETURNING *",
        user_id,
        JOB_EXTRACTED["company_name"],
        JOB_EXTRACTED["job_title"],
        "https://jobs.ashbyhq.com/langchain/langsmith-pm",
    )
    opening_id = opening["id"]

    run_row = await conn.fetchrow(
        "INSERT INTO job_opening_extraction_runs "
        "(opening_id, status, attempt_number, started_at, completed_at) VALUES ($1,'succeeded',1,NOW(),NOW()) RETURNING id",
        opening_id,
    )
    run_id = run_row["id"]

    d = JOB_EXTRACTED
    await conn.execute(
        """INSERT INTO job_opening_extracted_details_versions (
               run_id, opening_id, schema_version,
               job_title, company_name, location, employment_type,
               description_summary, required_skills, preferred_skills,
               experience_level, raw_payload, extractor_model, source_url,
               role_summary, technical_keywords, sector_keywords,
               business_sectors, problem_being_solved, useful_experiences
           ) VALUES (
               $1,$2,1,$3,$4,$5,$6,$7,$8::jsonb,$9::jsonb,
               $10,$11::jsonb,$12,$13,$14,$15::jsonb,$16::jsonb,
               $17::jsonb,$18,$19::jsonb
           )""",
        run_id, opening_id,
        d["job_title"], d["company_name"], d["location"], d["employment_type"],
        d["description_summary"],
        json.dumps(d["required_skills"]),
        json.dumps(d["preferred_skills"]),
        d["experience_level"],
        json.dumps({"source": "manual_test_fixture", **d}),
        "manual",
        "https://jobs.ashbyhq.com/langchain/langsmith-pm",
        d["role_summary"],
        json.dumps(d["technical_keywords"]),
        json.dumps(d["sector_keywords"]),
        json.dumps(d["business_sectors"]),
        d["problem_being_solved"],
        json.dumps(d["useful_experiences"]),
    )

    return opening_id


async def _create_agent_run(conn, opening_id: int, user_id: int) -> int:
    row = await conn.fetchrow(
        "INSERT INTO job_opening_agent_runs (opening_id, user_id, status) VALUES ($1,$2,'running') RETURNING id",
        opening_id, user_id,
    )
    return row["id"]


async def _teardown(conn, user_id: int) -> None:
    """Remove all test data for this user (cascade deletes handle children)."""
    await conn.execute(
        "UPDATE job_openings SET agent_run_id=NULL WHERE user_id=$1", user_id
    )
    await conn.execute("DELETE FROM users WHERE id=$1", user_id)


# ── Section inspection helpers ────────────────────────────────────────────────
async def _count_resume_sections(conn, user_id: int, opening_id: int) -> dict[str, int]:
    resume = await conn.fetchrow(
        """SELECT r.id FROM job_opening_resumes r
           JOIN job_openings o ON o.id=r.opening_id
           WHERE r.opening_id=$1 AND o.user_id=$2""",
        opening_id, user_id,
    )
    if not resume:
        return {}
    rid = resume["id"]
    counts = {}
    for label, tbl, col in [
        ("experience",     "job_opening_experience",     "resume_id"),
        ("education",      "job_opening_education",      "resume_id"),
        ("projects",       "job_opening_projects",       "resume_id"),
        ("skills",         "job_opening_skills",         "resume_id"),
        ("certifications", "job_opening_certifications", "resume_id"),
    ]:
        counts[label] = await conn.fetchval(f"SELECT count(*) FROM {tbl} WHERE {col}=$1", rid)
    return counts


# ── Main test runner ──────────────────────────────────────────────────────────
async def run_test(pdf_path: Path, output_path: Path | None, keep_data: bool) -> TestRun:
    import uuid
    import asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password
    from app.features.job_tracker.agents.runner import run_agent_stream
    from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf

    result = TestRun()
    result.start_time = time.time()

    # ── 1. Read & validate the PDF ─────────────────────────────────────────
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  Step 1 — Read resume PDF{RESET}")
    print(f"{'─'*60}")

    result.assert_that("PDF file exists", pdf_path.exists(), str(pdf_path))
    if not pdf_path.exists():
        print(fail(f"PDF not found: {pdf_path}"))
        return result

    pdf_size = pdf_path.stat().st_size
    print(info(f"File  : {pdf_path.name}"))
    print(info(f"Size  : {pdf_size:,} bytes"))

    pdf_text = read_pdf_text(pdf_path)
    print(info(f"Pages : {pdf_text.count(chr(12)) + 1}"))
    print(info(f"Chars : {len(pdf_text):,}"))

    validate_pdf_matches_profile(pdf_text, result)
    for a in result.assertions:
        print((ok if a.passed else fail)(f"{a.name}"))

    # ── 2. DB setup ────────────────────────────────────────────────────────
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  Step 2 — Set up test data{RESET}")
    print(f"{'─'*60}")

    conn = await asyncpg.connect(settings.database_url)

    try:
        await ensure_auth_schema(conn)

        uid_hex = uuid.uuid4().hex[:8]
        email   = f"test-agent-{uid_hex}@test.local"
        user    = await create_user(conn, email=email, password_hash=hash_password("testpass"))
        result.user_id = user["id"]
        print(info(f"Created test user id={result.user_id}  email={email}"))

        result.profile_id = await _setup_profile(conn, result.user_id)
        print(info(
            f"Profile id={result.profile_id} — "
            f"{len(SIDDHESH_PROFILE['education'])} edu, "
            f"{len(SIDDHESH_PROFILE['experiences'])} exp, "
            f"{len(SIDDHESH_PROFILE['skills'])} skills"
        ))

        result.opening_id = await _setup_opening_and_extraction(conn, result.user_id)
        print(info(f"Opening id={result.opening_id} — {JOB_EXTRACTED['job_title']} @ {JOB_EXTRACTED['company_name']}"))

        result.run_id = await _create_agent_run(conn, result.opening_id, result.user_id)
        print(info(f"Agent run id={result.run_id}"))

        # ── 3. Run the agent ───────────────────────────────────────────────
        print(f"\n{BOLD}{'─'*60}{RESET}")
        print(f"{BOLD}  Step 3 — Agent execution{RESET}")
        print(f"{'─'*60}")

        node_start: dict[str, float] = {}
        agent_error: str | None = None

        async for event in run_agent_stream(conn, result.user_id, result.opening_id, result.run_id):
            result.events.append(event)
            node   = event.get("node", "?")
            status = event.get("status", "?")
            msg    = event.get("message", "")

            if status == "started":
                node_start[node] = time.time()
                icon = f"{CYAN}→{RESET}"
            elif status in ("completed", "succeeded"):
                elapsed = time.time() - node_start.get(node, time.time())
                icon = f"{GREEN}✔{RESET}"
                result.nodes_seen.add(node)
                msg = f"{msg}  ({elapsed:.1f}s)"
            elif status in ("error", "failed"):
                icon = f"{RED}✘{RESET}"
                agent_error = msg
            else:
                icon = f"{YELLOW}·{RESET}"

            print(f"  {icon} [{node:<15}] {msg}")

        result.elapsed = time.time() - result.start_time

        # ── 4. Fetch rendered PDF ──────────────────────────────────────────
        print(f"\n{BOLD}{'─'*60}{RESET}")
        print(f"{BOLD}  Step 4 — Inspect output{RESET}")
        print(f"{'─'*60}")

        pdf_result = await get_resume_pdf(conn, result.user_id, result.opening_id)
        if pdf_result:
            result.pdf_bytes, _ = pdf_result
            print(info(f"PDF rendered — {len(result.pdf_bytes):,} bytes"))
            if output_path:
                output_path.write_bytes(result.pdf_bytes)
                print(info(f"Saved to: {output_path}"))
        else:
            print(warn("No rendered PDF found"))

        section_counts = await _count_resume_sections(conn, result.user_id, result.opening_id)
        for sec, cnt in section_counts.items():
            print(info(f"  {sec:<16}: {cnt} entries"))

        # ── 5. Quality gate assertions ────────────────────────────────────
        EXPECTED_NODES = {
            "extract", "select_template", "snapshot", "triage",
            "experience", "projects", "skills", "personal",
            "skills_certs", "render", "optimiser",
        }

        result.assert_that(
            "Agent completed without error",
            agent_error is None,
            agent_error or "",
        )

        for node in sorted(EXPECTED_NODES):
            result.assert_that(
                f"Node '{node}' executed",
                node in result.nodes_seen,
                "missing from event log",
            )

        result.assert_that(
            "Resume snapshot created",
            bool(section_counts),
            "no resume rows found",
        )
        result.assert_that(
            "Experience entries >= 5",
            section_counts.get("experience", 0) >= 5,
            f"got {section_counts.get('experience', 0)}",
        )
        result.assert_that(
            "Education entries >= 2",
            section_counts.get("education", 0) >= 2,
            f"got {section_counts.get('education', 0)}",
        )
        result.assert_that(
            "Skill entries >= 10",
            section_counts.get("skills", 0) >= 10,
            f"got {section_counts.get('skills', 0)}",
        )
        result.assert_that(
            "PDF was rendered",
            result.pdf_bytes is not None,
            "no PDF bytes",
        )
        if result.pdf_bytes:
            try:
                from pypdf import PdfReader
                import io
                reader  = PdfReader(io.BytesIO(result.pdf_bytes))
                n_pages = len(reader.pages)
                result.assert_that(
                    "Resume fits 1–2 pages",
                    1 <= n_pages <= 2,
                    f"{n_pages} page(s)",
                )
            except Exception:
                pass

        # check agent status in DB
        final_run = await conn.fetchrow(
            "SELECT status FROM job_opening_agent_runs WHERE id=$1", result.run_id
        )
        db_status = final_run["status"] if final_run else "unknown"
        result.assert_that(
            "DB agent_run.status = 'succeeded'",
            db_status == "succeeded",
            f"got '{db_status}'",
        )

    finally:
        if not keep_data and result.user_id:
            await _teardown(conn, result.user_id)
            print(info("\nTest data cleaned up"))
        elif keep_data:
            print(info(
                f"\nData retained — user_id={result.user_id}, "
                f"opening_id={result.opening_id}, run_id={result.run_id}"
            ))
        await conn.close()

    return result


# ── Report card ───────────────────────────────────────────────────────────────
def print_report(result: TestRun) -> None:
    total  = len(result.assertions)
    passed = result.passed
    pct    = int(passed / total * 100) if total else 0

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  REPORT CARD{RESET}")
    print(f"{'═'*60}")

    for a in result.assertions:
        line = ok(a.name) if a.passed else fail(f"{a.name}  [{a.detail}]")
        print(f"  {line}")

    print(f"{'─'*60}")

    colour = GREEN if pct == 100 else YELLOW if pct >= 70 else RED
    grade  = "A" if pct == 100 else "B" if pct >= 85 else "C" if pct >= 70 else "F"
    print(f"\n  {BOLD}Score  : {colour}{passed}/{total} ({pct}%)  [{grade}]{RESET}")
    print(f"  {BOLD}Time   : {result.elapsed:.1f}s{RESET}")
    print(f"  {BOLD}Nodes  : {sorted(result.nodes_seen)}{RESET}")
    print(f"\n{'═'*60}\n")


# ── CLI entry point ───────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Resume AI Agent test harness")
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF,
        help="Path to the candidate resume PDF",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Save the rendered tailored PDF here",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Don't delete test rows after the run",
    )
    args = parser.parse_args()

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  RESUME AGENT — TEST HARNESS{RESET}")
    print(f"{'═'*60}")
    print(info(f"Candidate : Siddhesh Chaudhari"))
    print(info(f"Role      : {JOB_EXTRACTED['job_title']} @ {JOB_EXTRACTED['company_name']}"))
    print(info(f"PDF       : {args.pdf}"))

    result = asyncio.run(run_test(args.pdf, args.output, args.keep_data))
    print_report(result)

    sys.exit(0 if not result.failed_list else 1)


if __name__ == "__main__":
    main()
