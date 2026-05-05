"""
Real run: Siddhesh Chaudhari vs OpenAI – Product Manager, API Infrastructure.

Usage:
    set PATH=C:\\texlive\\2026\\bin\\windows;%PATH%
    uv run python scripts/run_openai_pm.py
"""
from __future__ import annotations
import asyncio, json, os, sys, uuid
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TEXLIVE_BIN = r"C:\texlive\2026\bin\windows"
if TEXLIVE_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = TEXLIVE_BIN + os.pathsep + os.environ.get("PATH", "")

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

# ── Job description ──────────────────────────────────────────────────────────
JOB_TEXT = """
Product Manager, API Infrastructure @ OpenAI
Location: San Francisco, CA (Hybrid, 3 days/week)

About the Role:
Seeking an experienced PM to define and scale data processing, data privacy, billing,
and access controls products. Set strategy and execute on projects like expanding
regional data processing footprint, enabling inference caching controls in the API,
and building APIs for organizations to manage spend limits. Ship foundational
capabilities ensuring customers use OpenAI products securely, privately, with
enterprise-grade controls. Partners with engineering, security, legal, compliance,
finance, and leadership.

In this role, you will:
- Develop an enterprise data control plane to securely access and manage enterprise
  data for LLM use
- Drive product strategy for safety controls, privacy features, access management,
  and API usage/cost visibility
- Build and improve data governance: retention, encryption, audit logs, permissions,
  and lifecycle management
- Lead access control models, identity flows (SSO/SAML, SCIM), and admin tooling
- Oversee usage metering, cost dashboards, alerts, budgeting tools, and predictable
  API cost experiences

You might thrive if you have:
- Experience in security, privacy, data infrastructure, or usage-based platform products
- Strong understanding of data governance, access controls, and enterprise identity
- Experience with usage metering, cost-management tooling, or billing-adjacent systems
- Ability to work across security, legal, engineering, compliance, and finance domains
- Strong systems thinking, analytical skills, comfort in high-risk/high-trust areas
- Proven experience leading large, complex, highly technical cross-functional teams
- Excellent communication to drive alignment across technical and regulatory environments
""".strip()

# ── Siddhesh's profile (from resume) ─────────────────────────────────────────
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
            "end_month_year": None,
            "context": (
                "Scoped To-be Features through Requirements Gathering Workshops & drafted a roadmap "
                "to develop 6 main features around in-game accessories creation, ads management & user "
                "interaction platform to perform marketing & interactive branding inside Roblox Games. "
                "Designed system architectures, UI/UX & data flows & developed prototype (Backend, API "
                "Gateway, Roblox Scripting) using React, Python FastAPI, Lua, automating Ads Management, "
                "Interaction Data Logging & Analytics with a team of 6."
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
                "Assisted VC arm to scout (Data, Productivity) & facilitate due diligence with market insight "
                "for investment decisions. Consulted 5+ portfolio startups for Tech, GTM & Partnerships. "
                "Maintained CRM Dashboards & data automations using n8n & Python."
            ),
        },
        {
            "role_title": "Technical Program Manager",
            "company_name": "Evonik – Purdue Data Mine",
            "start_month_year": "01/2025",
            "end_month_year": "05/2025",
            "context": (
                "Delivered PoC (later adopted & deployed on Evonik private cloud) directing 10-person team "
                "through 8 sprints, cutting compatibility research time by 96% from 30 min to under 1 min. "
                "Led requirements analysis & design workshops to determine 3 key pain-points, OKRs, KPIs & "
                "developer efforts. Owned development lifecycle of React & FastAPI web app, shipping 12 "
                "features & consolidating 870,000 data points into master table."
            ),
        },
        {
            "role_title": "Technical Project Manager",
            "company_name": "Microsoft – Purdue Data Mine",
            "start_month_year": "08/2024",
            "end_month_year": "12/2024",
            "context": (
                "Led 5-member team through 8-sprint agile cycle to deliver PoC on schedule, managing full "
                "project lifecycle from ideation to deployment, overseeing 30-item product backlog. Designed "
                "end-to-end sentiment analysis pipeline processing 1,000 images & 240 videos from 3 media "
                "sources, boosting insight accuracy by 40%. Deployed 4 distinct LLMs reducing computation "
                "time by 1-2 hours per cycle; added auto-translate for broader dataset coverage."
            ),
        },
        {
            "role_title": "Technology Consultant",
            "company_name": "PwC (PricewaterhouseCoopers)",
            "start_month_year": "07/2022",
            "end_month_year": "07/2024",
            "context": (
                "Orchestrated end-to-end SAP Vendor Invoice Management implementations for 3 clients, "
                "delivering 27 custom workflows enhancing invoice KPIs by 40% & cutting cost-per-invoice "
                "under $4. Directed team of 5 analysts shipping 48 features with 90% improvement in process "
                "automation & invoice cycle reduction to under 2 days. Led 6 design workshops & authored 32 "
                "technical documents, cutting post-launch tickets by 60%, delivering 2 weeks ahead of schedule."
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
}


async def main():
    import asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password
    from app.features.job_tracker.opening_ingestion.clients.extraction_chain import extract_job_details
    from app.features.job_tracker.agents.runner import run_agent_stream
    from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf

    conn = await asyncpg.connect(settings.database_url)

    print("\n" + "="*60)
    print("  RESUME AGENT — OPENAI PM ROLE")
    print("="*60)
    print("  Candidate : Siddhesh Chaudhari")
    print("  Role      : Product Manager, API Infrastructure")
    print("  Company   : OpenAI")
    print("  Output    : siddhesh_openai.pdf\n")

    try:
        # Clean previous runs for this job
        async with conn.transaction():
            await conn.execute(
                "UPDATE job_openings SET agent_run_id=NULL "
                "WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'siddhesh-openai-%')"
            )
            await conn.execute(
                "DELETE FROM job_opening_agent_runs WHERE opening_id IN "
                "(SELECT id FROM job_openings WHERE user_id IN "
                "(SELECT id FROM users WHERE email LIKE 'siddhesh-openai-%'))"
            )
            await conn.execute("DELETE FROM users WHERE email LIKE 'siddhesh-openai-%'")

        print("Setting up profile data...")
        await ensure_auth_schema(conn)
        email = f"siddhesh-openai-{uuid.uuid4().hex[:8]}@example.com"
        user  = await create_user(conn, email=email, password_hash=hash_password("demo"))
        user_id = user["id"]

        # Job profile
        profile = await conn.fetchrow(
            "INSERT INTO job_profiles (user_id, profile_name, target_role) VALUES ($1,$2,$3) RETURNING *",
            user_id, "Siddhesh – TPM / PM Profile", "Technical Product Manager",
        )
        profile_id = profile["id"]

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
                "(job_profile_id, university_name, major, degree_type, "
                "start_month_year, end_month_year, bullet_points, reference_links) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,'[]'::jsonb)",
                profile_id, edu["university_name"], edu["major"], edu["degree_type"],
                edu["start_month_year"], edu["end_month_year"],
                json.dumps(edu.get("bullet_points", [])),
            )

        # Experience
        for exp in PROFILE["experiences"]:
            await conn.execute(
                "INSERT INTO job_profile_experiences "
                "(job_profile_id, role_title, company_name, start_month_year, end_month_year, "
                "context, work_sample_links, bullet_points) "
                "VALUES ($1,$2,$3,$4,$5,$6,'[]'::jsonb,'[]'::jsonb)",
                profile_id, exp["role_title"], exp["company_name"],
                exp["start_month_year"], exp["end_month_year"], exp["context"],
            )

        # Skills
        for i, (kind, name) in enumerate(PROFILE["skills"]):
            await conn.execute(
                "INSERT INTO job_profile_skill_items (job_profile_id, kind, name, sort_order) "
                "VALUES ($1,$2,$3,$4)",
                profile_id, kind, name, i,
            )

        print(f"  Profile populated: {len(PROFILE['education'])} edu, "
              f"{len(PROFILE['experiences'])} exp, {len(PROFILE['skills'])} skills")

        # Job opening
        opening = await conn.fetchrow(
            "INSERT INTO job_openings (user_id, company_name, role_name, source_url) "
            "VALUES ($1,$2,$3,$4) RETURNING *",
            user_id, "OpenAI", "Product Manager, API Infrastructure",
            "https://jobs.ashbyhq.com/openai/7ffa2a14-fa9c-46cb-a30a-1f7a35ae904a",
        )
        opening_id = opening["id"]

        # LLM extraction of job details
        print("  Running LLM extraction on job description...")
        extracted = await extract_job_details(JOB_TEXT)
        print(f"  Extracted: {extracted.job_title} @ {extracted.company_name}")
        print(f"  Required skills: {extracted.required_skills}")

        # Persist extraction
        ext_run = await conn.fetchrow(
            "INSERT INTO job_opening_extraction_runs "
            "(opening_id, status, attempt_number, started_at, completed_at) "
            "VALUES ($1,'succeeded',1,NOW(),NOW()) RETURNING id",
            opening_id,
        )
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
                $1,$2,2,$3,$4,$5,$6,$7,
                $8::jsonb,$9::jsonb,
                $10,$11,$12,
                $13::jsonb,$14,$15,
                $16,$17::jsonb,$18::jsonb,$19::jsonb,$20,$21::jsonb
            )
            """,
            ext_run["id"], opening_id,
            extracted.job_title, extracted.company_name, extracted.location,
            extracted.employment_type, extracted.description_summary,
            json.dumps(extracted.required_skills or []),
            json.dumps(extracted.preferred_skills or []),
            extracted.experience_level, extracted.posted_date, extracted.application_deadline,
            json.dumps(extracted.model_dump()),
            extracted.extractor_model or "gpt-5.4-mini",
            extracted.source_url or "https://jobs.ashbyhq.com/openai/7ffa2a14-fa9c-46cb-a30a-1f7a35ae904a",
            extracted.role_summary,
            json.dumps(extracted.technical_keywords or []),
            json.dumps(extracted.sector_keywords or []),
            json.dumps(extracted.business_sectors or []),
            extracted.problem_being_solved,
            json.dumps(extracted.useful_experiences or []),
        )

        # Create agent run
        agent_run = await conn.fetchrow(
            "INSERT INTO job_opening_agent_runs (opening_id, user_id, status) "
            "VALUES ($1,$2,'running') RETURNING id",
            opening_id, user_id,
        )
        run_id = agent_run["id"]
        print(f"  opening_id={opening_id}  run_id={run_id}\n")

        # Run agent
        print("Running LangGraph agent...")
        print("-"*60)
        async for event in run_agent_stream(conn, user_id, opening_id, run_id):
            node   = event.get("node", "?")
            status = event.get("status", "?")
            msg    = event.get("message", "")
            icon   = "[OK]" if status == "completed" else "[!!]" if status in ("error","failed") else " ->"
            print(f"  {icon} [{node}] {msg}")
        print("-"*60)

        # Fetch and save PDF
        print("\nFetching PDF from DB...")
        result = await get_resume_pdf(conn, user_id, opening_id)
        if result:
            pdf_bytes, _ = result
            out = BACKEND_DIR / "siddhesh_openai.pdf"
            out.write_bytes(pdf_bytes)
            print(f"\n{'='*60}")
            print(f"  [OK] PDF saved: {out}")
            print(f"       Size    : {len(pdf_bytes):,} bytes")
            print(f"{'='*60}\n")
        else:
            print("  [!!] No PDF generated — check agent events above.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
