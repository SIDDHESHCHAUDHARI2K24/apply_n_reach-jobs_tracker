"""
Real run: Siddhesh Chaudhari resume vs LangChain PM – LangSmith role.

Usage:
    set PATH=C:\\texlive\\2026\\bin\\windows;%PATH%
    uv run python scripts/run_agent_real.py --output siddhesh_langchain.pdf
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import argparse
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TEXLIVE_BIN = os.environ.get("TEXLIVE_BIN", r"C:\texlive\2026\bin\windows")
if TEXLIVE_BIN and TEXLIVE_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = TEXLIVE_BIN + os.pathsep + os.environ.get("PATH", "")

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

# ─────────────────────────────────────────────────────────────────────────────
# REAL JOB DESCRIPTION  (Product Manager, LangSmith @ LangChain)
# ─────────────────────────────────────────────────────────────────────────────
JOB_TEXT = """
Product Manager, LangSmith @ LangChain

ABOUT US
At LangChain, our mission is to make intelligent agents ubiquitous. We build the
foundation for agent engineering in the real world, helping developers move from
prototypes to production-ready AI agents. With $125M raised at Series B from IVP,
Sequoia, Benchmark, CapitalG, and Sapphire Ventures.

ABOUT THE ROLE
We're looking for a Product Manager to own key parts of LangSmith — the
observability, evals and deployment platform that makes shipping reliable AI systems
possible.

WHAT YOU'LL DO
- Own the roadmap for a core area of the LangSmith platform.
- Work with customers to understand challenges and define new product features.
- Partner with engineering to define scope, make technical tradeoffs, and ship.
- Help shape product strategy alongside founders and leadership team.
- Build features at the intersection of UX and production infrastructure: versioning
  prompt chains, debugging multi-step agent failures, evaluation systems at scale.

WHAT YOU'LL BRING
- 3+ years of product management or engineering experience building developer tools,
  infrastructure products, or technical SaaS platforms.
- Deeply technical — API design, system architecture, data pipelines, debugging.
- Bias toward action — ship, learn, iterate.
- Strong written and verbal communicator who can align cross-functional teams.

NICE TO HAVE
- CS/Engineering or equivalent technical background.
- Experience at a high-growth startup or developer-focused company.
- Hands-on experience building with LLMs, agents, or AI applications.

Compensation: $180,000–$215,000
Location: Remote-friendly
""".strip()

# ─────────────────────────────────────────────────────────────────────────────
# SIDDHESH'S PROFILE  (extracted from resume)
# ─────────────────────────────────────────────────────────────────────────────
PROFILE = {
    "personal": {
        "full_name": "Siddhesh Chaudhari",
        "email": "s.chaudhari2k24@gmail.com",
        "linkedin_url": "https://www.linkedin.com/in/siddhesh-chaudhari",
        "github_url": "https://github.com/siddhesh-chaudhari",
        "portfolio_url": None,
    },
    "education": [
        {
            "university_name": "Purdue University",
            "major": "Engineering Management (Product / Data)",
            "degree_type": "Master of Science",
            "start_month_year": "08/2024",
            "end_month_year": "05/2026",
            "bullet_points": [
                "Courses: Corporate Consulting, Technical Product Management, Business Analytics, Entrepreneurship & Business Strategy",
                "Developing Voice Agents & UI Navigation Agentic Workflows for Job Application Automation with Python, Livekit, LangGraph & React",
            ],
        },
        {
            "university_name": "University of Mumbai (VJTI)",
            "major": "Engineering",
            "degree_type": "Bachelor of Technology",
            "start_month_year": "08/2018",
            "end_month_year": "05/2022",
            "bullet_points": [],
        },
    ],
    "experiences": [
        {
            "role_title": "Product Developer / Team Lead",
            "company_name": "Feenix Group – Purdue Data Mine",
            "start_month_year": "08/2025",
            "end_month_year": None,  # current
            "context": (
                "Scoped To-be Features through Requirements Gathering Workshops & drafted a roadmap "
                "to develop 6 main features around in-game accessories creation, ads management & user "
                "interaction platform to programmatically perform marketing & interactive branding inside "
                "Roblox Games. Designed system architectures, UI/UX & data flows & developed the prototype "
                "(Backend, API Gateway, Roblox Scripting) using React, Python FastAPI, Lua, automating the "
                "entire Ads Management, Interaction Data Logging & Analytics with a team of 6."
            ),
        },
        {
            "role_title": "Technical Program Manager",
            "company_name": "Boxsy – Purdue Data Mine",
            "start_month_year": "08/2025",
            "end_month_year": "12/2025",
            "context": (
                "Led a team of 14 to streamline development & achieve 4 OKRs by setting up 3 sub-teams "
                "for 6 Integrations, 7 AI Agent Developments & JIRA-Github-Vercel CI-CD pipelines "
                "prioritizing over 3 Epics with 30+ user stories. KPIs Tracked: Development Speed, AI Accuracy."
            ),
        },
        {
            "role_title": "Venture Capital & Venture Studio Intern",
            "company_name": "Launch Factory",
            "start_month_year": "08/2025",
            "end_month_year": "12/2025",
            "context": (
                "Assisted Firm's VC arm to scout (Data, Productivity) & facilitate due diligence with market "
                "insight for investment decisions. Consulted 5+ portfolio startups for Tech, GTM & Partnerships. "
                "Maintained CRM Dashboards & Data automations using n8n & Python."
            ),
        },
        {
            "role_title": "Technical Program Manager",
            "company_name": "Evonik – Purdue Data Mine",
            "start_month_year": "01/2025",
            "end_month_year": "05/2025",
            "context": (
                "Delivered PoC (later adopted & deployed on Evonik's private cloud) directing a 10-person team "
                "through 8 sprints, reducing on-site risks & cutting compatibility research time by over 96% — "
                "from 30 minutes to under one minute. Led requirements analysis & design workshops to determine "
                "3 key pain-points, OKRs, KPIs & developer efforts. Owned development lifecycle of React & "
                "FastAPI web app, shipping 12 features & consolidating 870,000 data points into master table."
            ),
        },
        {
            "role_title": "Technical Project Manager",
            "company_name": "Microsoft – Purdue Data Mine",
            "start_month_year": "08/2024",
            "end_month_year": "12/2024",
            "context": (
                "Led a 5-member team through 8-sprint agile cycle to deliver PoC on schedule, managing full "
                "project lifecycle from ideation to deployment, overseeing 30-item product backlog. Designed "
                "end-to-end sentiment analysis pipeline processing 1,000 images & 240 videos from 3 media "
                "sources, boosting insight accuracy by 40%. Automated contextual analysis with 4 distinct LLMs, "
                "reducing computation time by 1-2 hours per cycle with auto-translate for broader dataset coverage."
            ),
        },
        {
            "role_title": "Technology Consultant",
            "company_name": "PwC (PricewaterhouseCoopers)",
            "start_month_year": "07/2022",
            "end_month_year": "07/2024",
            "context": (
                "Orchestrated end-to-end SAP Vendor Invoice Management implementations for 3 clients, "
                "delivering 27 custom workflows that enhanced invoice processing KPIs by 40% & cut "
                "cost-per-invoice to under $4. Directed team of 5 analysts shipping 48 features with "
                "90% improvement in process automation & reduction of invoice cycle to under 2 days. "
                "Led 6 design workshops & authored 32 technical documents, cutting post-launch tickets "
                "by 60%, signing off 2 weeks ahead of schedule."
            ),
        },
    ],
    "skills": [
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
        ("competency", "Technical Product Management"),
        ("competency", "Project & Stakeholder Management"),
        ("competency", "System Design"),
        ("competency", "UI/UX Design"),
        ("competency", "Business Documentation"),
        ("competency", "Workflow Automation"),
        ("competency", "Agile / Scrum"),
    ],
    "certifications": [],
}


async def setup_real_data(conn) -> tuple[int, int, int]:
    """Create Siddhesh's profile + LangChain job opening. Returns (user_id, opening_id, run_id)."""
    import uuid
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password
    from app.features.job_tracker.opening_ingestion.clients.extraction_chain import extract_job_details

    await ensure_auth_schema(conn)

    uid = uuid.uuid4().hex[:8]
    email = f"siddhesh-demo-{uid}@example.com"
    user = await create_user(conn, email=email, password_hash=hash_password("demopass"))
    user_id = user["id"]
    print(f"  Created user id={user_id}")

    # Job profile
    profile = await conn.fetchrow(
        "INSERT INTO job_profiles (user_id, profile_name, target_role) VALUES ($1, $2, $3) RETURNING *",
        user_id, "Siddhesh – TPM / PM Profile", "Technical Product Manager",
    )
    profile_id = profile["id"]
    print(f"  Created job profile id={profile_id}")

    # Personal
    p = PROFILE["personal"]
    await conn.execute(
        "INSERT INTO job_profile_personal_details "
        "(job_profile_id, full_name, email, linkedin_url, github_url, portfolio_url) "
        "VALUES ($1,$2,$3,$4,$5,$6)",
        profile_id, p["full_name"], p["email"], p["linkedin_url"], p["github_url"], p["portfolio_url"],
    )

    # Education
    for edu in PROFILE["education"]:
        await conn.execute(
            "INSERT INTO job_profile_educations "
            "(job_profile_id, university_name, major, degree_type, start_month_year, end_month_year, "
            "bullet_points, reference_links) VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,'[]'::jsonb)",
            profile_id, edu["university_name"], edu["major"], edu["degree_type"],
            edu["start_month_year"], edu["end_month_year"],
            json.dumps(edu.get("bullet_points", [])),
        )

    # Experience
    for exp in PROFILE["experiences"]:
        await conn.execute(
            "INSERT INTO job_profile_experiences "
            "(job_profile_id, role_title, company_name, start_month_year, end_month_year, "
            "context, work_sample_links, bullet_points) VALUES ($1,$2,$3,$4,$5,$6,'[]'::jsonb,'[]'::jsonb)",
            profile_id, exp["role_title"], exp["company_name"],
            exp["start_month_year"], exp["end_month_year"], exp["context"],
        )

    # Skills
    for i, (kind, name) in enumerate(PROFILE["skills"]):
        await conn.execute(
            "INSERT INTO job_profile_skill_items (job_profile_id, kind, name, sort_order) VALUES ($1,$2,$3,$4)",
            profile_id, kind, name, i,
        )

    print(f"  Populated: {len(PROFILE['education'])} edu, {len(PROFILE['experiences'])} exp, {len(PROFILE['skills'])} skills")

    # Job opening
    opening = await conn.fetchrow(
        "INSERT INTO job_openings (user_id, company_name, role_name, source_url) "
        "VALUES ($1,$2,$3,$4) RETURNING *",
        user_id, "LangChain",
        "Product Manager, LangSmith",
        "https://jobs.ashbyhq.com/langchain/27af5f96-b287-4bcc-8679-f96686dc7c8d",
    )
    opening_id = opening["id"]
    print(f"  Created job opening id={opening_id}")

    # Extract job details via LLM
    print("  Running LLM extraction on job description...")
    extracted = await extract_job_details(JOB_TEXT)
    print(f"  Extracted: {extracted.job_title} @ {extracted.company_name}")

    # Persist extraction run + details
    run_row = await conn.fetchrow(
        "INSERT INTO job_opening_extraction_runs "
        "(opening_id, status, attempt_number, started_at, completed_at) "
        "VALUES ($1,'succeeded',1,NOW(),NOW()) RETURNING id",
        opening_id,
    )
    extraction_run_id = run_row["id"]

    await conn.execute(
        """
        INSERT INTO job_opening_extracted_details_versions (
            run_id, opening_id, schema_version,
            job_title, company_name, location, employment_type,
            description_summary, required_skills, preferred_skills,
            experience_level, posted_date, application_deadline,
            raw_payload, extractor_model, source_url,
            role_summary, technical_keywords, sector_keywords,
            business_sectors, problem_being_solved, useful_experiences
        ) VALUES (
            $1,$2,2,$3,$4,$5,$6,$7,$8::jsonb,$9::jsonb,
            $10,$11,$12,$13::jsonb,$14,$15,
            $16,$17::jsonb,$18::jsonb,$19::jsonb,$20,$21::jsonb
        )
        """,
        extraction_run_id, opening_id,
        extracted.job_title, extracted.company_name, extracted.location,
        extracted.employment_type, extracted.description_summary,
        json.dumps(extracted.required_skills or []),
        json.dumps(extracted.preferred_skills or []),
        extracted.experience_level, extracted.posted_date, extracted.application_deadline,
        json.dumps(extracted.model_dump()),
        extracted.extractor_model or "gpt-5.4-mini",
        extracted.source_url or "https://jobs.ashbyhq.com/langchain/27af5f96-b287-4bcc-8679-f96686dc7c8d",
        extracted.role_summary,
        json.dumps(extracted.technical_keywords or []),
        json.dumps(extracted.sector_keywords or []),
        json.dumps(extracted.business_sectors or []),
        extracted.problem_being_solved,
        json.dumps(extracted.useful_experiences or []),
    )

    # Agent run row
    agent_run = await conn.fetchrow(
        "INSERT INTO job_opening_agent_runs (opening_id, user_id, status) VALUES ($1,$2,'running') RETURNING id",
        opening_id, user_id,
    )
    run_id = agent_run["id"]
    print(f"  Created agent run id={run_id}")

    return user_id, opening_id, run_id


async def run_real(output_path: Path) -> None:
    import asyncpg
    from app.features.core.config import settings
    from app.features.job_tracker.agents.runner import run_agent_stream

    db_url = settings.database_url
    print(f"\n{'='*60}")
    print("  RESUME AGENT — REAL RUN")
    print(f"{'='*60}")
    print(f"\n  Candidate : Siddhesh Chaudhari")
    print(f"  Role      : Product Manager, LangSmith")
    print(f"  Company   : LangChain")
    print(f"  Output    : {output_path}\n")

    conn = await asyncpg.connect(db_url)
    print("Connected to DB [OK]\n")

    try:
        # Clean any previous demo runs for Siddhesh
        async with conn.transaction():
            await conn.execute(
                "UPDATE job_openings SET agent_run_id=NULL WHERE user_id IN "
                "(SELECT id FROM users WHERE email LIKE 'siddhesh-demo-%')"
            )
            await conn.execute(
                "DELETE FROM job_opening_agent_runs WHERE opening_id IN "
                "(SELECT id FROM job_openings WHERE user_id IN "
                "(SELECT id FROM users WHERE email LIKE 'siddhesh-demo-%'))"
            )
            await conn.execute("DELETE FROM users WHERE email LIKE 'siddhesh-demo-%'")

        print("Setting up profile & job data...")
        user_id, opening_id, run_id = await setup_real_data(conn)

        print(f"\nRunning agent (opening_id={opening_id}, run_id={run_id})...")
        print("-" * 60)

        async for event in run_agent_stream(conn, user_id, opening_id, run_id):
            node = event.get("node", "?")
            status = event.get("status", "?")
            message = event.get("message", "")
            icon = "[OK]" if status == "completed" else "[!!]" if status in ("error", "failed") else " ->"
            print(f"  {icon} [{node}] {message}")

        print("-" * 60)
        print("\nFetching rendered PDF...")

        from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf
        result = await get_resume_pdf(conn, user_id, opening_id)

        if result:
            pdf_bytes, _ = result
            output_path.write_bytes(pdf_bytes)
            print(f"\n{'='*60}")
            print(f"  [OK] PDF saved: {output_path}")
            print(f"       Size: {len(pdf_bytes):,} bytes")
            print(f"{'='*60}\n")
        else:
            print("\n  [!!] No PDF found — render node may have failed.\n")

    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(description="Real agent run: Siddhesh vs LangChain PM")
    parser.add_argument("--output", default="siddhesh_langchain.pdf")
    args = parser.parse_args()
    asyncio.run(run_real(Path(args.output).resolve()))


if __name__ == "__main__":
    main()
