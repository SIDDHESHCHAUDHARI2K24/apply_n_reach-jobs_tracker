"""
End-to-end demo: LangGraph resume agent with dummy data.

Usage:
    uv run python scripts/run_agent_demo.py [--output output.pdf]

Prerequisites:
    1. DB accessible & migration applied:
           uv run alembic upgrade head
    2. .env contains:
           OPENROUTER_API_KEY=sk-or-...
           DATABASE_URL=postgresql://...
    3. pdflatex on PATH (TeX Live):
           set PATH=C:\\texlive\\2026\\bin\\windows;%PATH%
           (or set TEXLIVE_BIN env var below)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import argparse
from pathlib import Path

# ── Fix Windows event loop for asyncpg SSL ──────────────────────────────────
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── Add TeX Live to PATH if not already present ─────────────────────────────
TEXLIVE_BIN = os.environ.get("TEXLIVE_BIN", r"C:\texlive\2026\bin\windows")
if TEXLIVE_BIN and TEXLIVE_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = TEXLIVE_BIN + os.pathsep + os.environ.get("PATH", "")

# ── Ensure we run from the backend directory ─────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

# ── Load .env ────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

# ─────────────────────────────────────────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────────────────────────────────────────

JOB_DESCRIPTION = """
Senior Backend Engineer – AI Platform
Acme Intelligence, San Francisco CA (Hybrid)

About the role:
We are building the next generation of AI-powered developer tools. As a Senior Backend
Engineer on the AI Platform team, you will design and implement scalable APIs and
micro-services that power our LLM inference pipeline, developer SDK, and real-time
data ingestion services.

Responsibilities:
- Design, build, and own high-throughput REST and gRPC APIs in Python (FastAPI/aiohttp)
- Implement LangChain and LangGraph pipelines for multi-step AI workflows
- Manage PostgreSQL schemas (async with asyncpg), write complex queries and migrations
- Build real-time streaming endpoints using Server-Sent Events and WebSockets
- Integrate with third-party LLM providers (OpenAI, Anthropic, OpenRouter)
- Own the CI/CD pipeline (GitHub Actions, Docker, AWS ECS)
- Collaborate with frontend and ML teams, contribute to technical design docs

Requirements:
- 4+ years of backend experience; 2+ years with Python async frameworks
- Strong proficiency in Python (FastAPI, asyncio, Pydantic v2)
- Experience with PostgreSQL, asyncpg, and database performance tuning
- Hands-on experience with LangChain, LangGraph, or similar LLM orchestration
- Familiarity with containerisation (Docker, Kubernetes)
- Experience with event-driven architectures (Kafka, Redis Streams, or SQS)

Nice to have:
- Vector databases (Pinecone, pgvector)
- Rust or Go for performance-critical services
- Experience with LangSmith or other LLM observability tools

Compensation: $180k–$220k + equity + benefits
""".strip()

EXTRACTED_DETAILS = {
    "job_title": "Senior Backend Engineer",
    "company_name": "Acme Intelligence",
    "location": "San Francisco CA (Hybrid)",
    "employment_type": "Full-time",
    "salary_range": "$180k–$220k + equity",
    "description_summary": (
        "AI Platform team building scalable APIs and micro-services for LLM inference "
        "pipeline, developer SDK, and real-time data ingestion."
    ),
    "required_skills": [
        "Python", "FastAPI", "asyncio", "Pydantic v2", "PostgreSQL", "asyncpg",
        "LangChain", "LangGraph", "Docker", "GitHub Actions",
    ],
    "preferred_skills": [
        "Kafka", "Redis", "Kubernetes", "pgvector", "Pinecone",
        "Rust", "Go", "LangSmith",
    ],
    "experience_level": "Senior (4+ years)",
    "posted_date": "2026-04-15",
    "application_deadline": None,
    "extractor_model": "demo-script",
    "source_url": "https://example.com/job/senior-backend-ai",
    # New v2 fields
    "role_summary": (
        "Senior Backend Engineer building Python/FastAPI micro-services and LangGraph "
        "pipelines for an AI developer-tools company. Owns high-throughput REST/gRPC "
        "APIs, PostgreSQL schemas, and LLM provider integrations."
    ),
    "technical_keywords": [
        "FastAPI", "LangChain", "LangGraph", "asyncpg", "asyncio",
        "PostgreSQL", "Docker", "gRPC", "SSE", "WebSockets", "OpenRouter",
    ],
    "sector_keywords": [
        "AI/ML platform", "developer tools", "LLM inference", "real-time data",
    ],
    "business_sectors": ["Artificial Intelligence", "Developer Tools", "SaaS"],
    "problem_being_solved": (
        "Building the infrastructure layer that makes LLMs fast, reliable, and "
        "observable for developers building AI-powered applications."
    ),
    "useful_experiences": [
        "LangChain/LangGraph pipeline development",
        "High-throughput async Python API development",
        "PostgreSQL schema design and asyncpg usage",
        "REST API design and OpenAPI documentation",
        "CI/CD with GitHub Actions and Docker",
    ],
}

PROFILE_DATA = {
    "personal": {
        "full_name": "Alex Johnson",
        "email": "alex.johnson@email.com",
        "linkedin_url": "https://linkedin.com/in/alexjohnson",
        "github_url": "https://github.com/alexjohnson",
        "portfolio_url": "https://alexjohnson.dev",
    },
    "education": {
        "university_name": "University of California, Berkeley",
        "major": "Computer Science",
        "degree_type": "Bachelor of Science",
        "start_month_year": "09/2015",
        "end_month_year": "05/2019",
    },
    "experiences": [
        {
            "role_title": "Senior Software Engineer",
            "company_name": "DataStream Inc.",
            "start_month_year": "06/2022",
            "end_month_year": None,
            "context": (
                "Led development of real-time data ingestion APIs processing 500K events/day "
                "using Python, FastAPI, and Kafka. Designed PostgreSQL schemas and wrote "
                "performance-critical async queries with asyncpg. Reduced API latency by 40% "
                "through connection pooling and query optimisation."
            ),
        },
        {
            "role_title": "Backend Engineer",
            "company_name": "CloudMesh Technologies",
            "start_month_year": "08/2019",
            "end_month_year": "05/2022",
            "context": (
                "Built REST APIs and background job processors in Python (Flask, then FastAPI). "
                "Managed PostgreSQL migrations with Alembic. Integrated third-party LLM APIs "
                "for document analysis features. Containerised services with Docker and "
                "deployed via GitHub Actions to AWS ECS."
            ),
        },
    ],
    "projects": [
        {
            "project_name": "AsyncFlow — LangGraph Pipeline Library",
            "description": (
                "Open-source Python library providing reusable LangGraph nodes for "
                "common LLM workflows (RAG, multi-step reasoning, tool-calling). "
                "900+ GitHub stars. Integrated LangSmith tracing and OpenRouter provider."
            ),
            "start_month_year": "01/2024",
            "end_month_year": None,
        },
        {
            "project_name": "PgVec — Vector Search Microservice",
            "description": (
                "FastAPI microservice wrapping pgvector for semantic search over "
                "1M+ embeddings. Used in production for document similarity at DataStream. "
                "Sub-50ms p99 via connection pooling and HNSW indexing."
            ),
            "start_month_year": "03/2023",
            "end_month_year": "11/2023",
        },
    ],
    "research": [
        {
            "paper_name": "Efficient Async Patterns for LLM Orchestration",
            "publication_link": "https://arxiv.org/abs/example.2024",
            "description": (
                "Survey paper on async concurrency patterns in LangChain/LangGraph "
                "pipelines, published in conference proceedings 2024."
            ),
        }
    ],
    "certifications": [
        {
            "certification_name": "AWS Certified Solutions Architect – Associate",
            "verification_link": "https://aws.amazon.com/verification/example",
        },
        {
            "certification_name": "HashiCorp Certified: Terraform Associate",
            "verification_link": "https://www.credly.com/badges/example",
        },
    ],
    "skills": [
        ("technical", "Python"),
        ("technical", "FastAPI"),
        ("technical", "LangChain / LangGraph"),
        ("technical", "PostgreSQL / asyncpg"),
        ("technical", "Docker / Kubernetes"),
        ("technical", "Kafka / Redis"),
        ("technical", "GitHub Actions / CI-CD"),
        ("technical", "AWS (ECS, Lambda, S3)"),
        ("technical", "REST API Design"),
        ("competency", "System Design"),
        ("competency", "Technical Leadership"),
        ("competency", "Code Review"),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────

async def setup_demo_data(conn) -> tuple[int, int, int]:
    """Create all dummy data and return (user_id, opening_id, run_id)."""
    import uuid
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password

    await ensure_auth_schema(conn)

    # Create user
    uid = uuid.uuid4().hex[:8]
    email = f"demo-agent-{uid}@example.com"
    user = await create_user(conn, email=email, password_hash=hash_password("demopass"))
    user_id = user["id"]
    print(f"  Created user: {email} (id={user_id})")

    # Create job profile
    profile = await conn.fetchrow(
        """
        INSERT INTO job_profiles (user_id, profile_name, target_role)
        VALUES ($1, $2, $3) RETURNING *
        """,
        user_id, "Alex's Backend Profile", "Senior Backend Engineer",
    )
    profile_id = profile["id"]
    print(f"  Created job profile id={profile_id}")

    # Personal details on profile
    p = PROFILE_DATA["personal"]
    await conn.execute(
        """
        INSERT INTO job_profile_personal_details
            (job_profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        profile_id, p["full_name"], p["email"],
        p["linkedin_url"], p["github_url"], p["portfolio_url"],
    )

    # Education
    edu = PROFILE_DATA["education"]
    await conn.execute(
        """
        INSERT INTO job_profile_educations
            (job_profile_id, university_name, major, degree_type,
             start_month_year, end_month_year, bullet_points, reference_links)
        VALUES ($1, $2, $3, $4, $5, $6, '[]'::jsonb, '[]'::jsonb)
        """,
        profile_id, edu["university_name"], edu["major"], edu["degree_type"],
        edu["start_month_year"], edu["end_month_year"],
    )

    # Experience
    for exp in PROFILE_DATA["experiences"]:
        await conn.execute(
            """
            INSERT INTO job_profile_experiences
                (job_profile_id, role_title, company_name,
                 start_month_year, end_month_year, context,
                 work_sample_links, bullet_points)
            VALUES ($1, $2, $3, $4, $5, $6, '[]'::jsonb, '[]'::jsonb)
            """,
            profile_id, exp["role_title"], exp["company_name"],
            exp["start_month_year"], exp["end_month_year"], exp["context"],
        )

    # Projects
    for proj in PROFILE_DATA["projects"]:
        await conn.execute(
            """
            INSERT INTO job_profile_projects
                (job_profile_id, project_name, description,
                 start_month_year, end_month_year, reference_links)
            VALUES ($1, $2, $3, $4, $5, '[]'::jsonb)
            """,
            profile_id, proj["project_name"], proj["description"],
            proj["start_month_year"], proj["end_month_year"],
        )

    # Research
    for res in PROFILE_DATA["research"]:
        await conn.execute(
            """
            INSERT INTO job_profile_researches
                (job_profile_id, paper_name, publication_link, description)
            VALUES ($1, $2, $3, $4)
            """,
            profile_id, res["paper_name"], res["publication_link"], res["description"],
        )

    # Certifications
    for cert in PROFILE_DATA["certifications"]:
        await conn.execute(
            """
            INSERT INTO job_profile_certifications
                (job_profile_id, certification_name, verification_link)
            VALUES ($1, $2, $3)
            """,
            profile_id, cert["certification_name"], cert["verification_link"],
        )

    # Skills
    for i, (kind, name) in enumerate(PROFILE_DATA["skills"]):
        await conn.execute(
            """
            INSERT INTO job_profile_skill_items (job_profile_id, kind, name, sort_order)
            VALUES ($1, $2, $3, $4)
            """,
            profile_id, kind, name, i,
        )
    print(f"  Populated profile with {len(PROFILE_DATA['experiences'])} exp, "
          f"{len(PROFILE_DATA['projects'])} projects, {len(PROFILE_DATA['skills'])} skills")

    # Create job opening
    opening = await conn.fetchrow(
        """
        INSERT INTO job_openings (user_id, company_name, role_name, source_url)
        VALUES ($1, $2, $3, $4) RETURNING *
        """,
        user_id, "Acme Intelligence", "Senior Backend Engineer",
        "https://example.com/job/senior-backend-ai",
    )
    opening_id = opening["id"]
    print(f"  Created job opening id={opening_id}")

    # Create extraction run (mark as succeeded so node_1 can read it)
    run_row = await conn.fetchrow(
        """
        INSERT INTO job_opening_extraction_runs
            (opening_id, status, attempt_number, started_at, completed_at)
        VALUES ($1, 'succeeded', 1, NOW(), NOW())
        RETURNING id
        """,
        opening_id,
    )
    extraction_run_id = run_row["id"]

    # Insert extracted details directly (bypassing Apify + LLM extraction)
    e = EXTRACTED_DETAILS
    await conn.execute(
        """
        INSERT INTO job_opening_extracted_details_versions (
            run_id, opening_id, schema_version,
            job_title, company_name, location, employment_type, salary_range,
            description_summary, required_skills, preferred_skills,
            experience_level, posted_date, application_deadline,
            raw_payload, extractor_model, source_url,
            role_summary, technical_keywords, sector_keywords,
            business_sectors, problem_being_solved, useful_experiences
        ) VALUES (
            $1, $2, 2,
            $3, $4, $5, $6, $7,
            $8, $9::jsonb, $10::jsonb,
            $11, $12, $13,
            $14::jsonb, $15, $16,
            $17, $18::jsonb, $19::jsonb,
            $20::jsonb, $21, $22::jsonb
        )
        """,
        extraction_run_id, opening_id,
        e["job_title"], e["company_name"], e["location"],
        e["employment_type"], e["salary_range"],
        e["description_summary"],
        json.dumps(e["required_skills"]),
        json.dumps(e["preferred_skills"]),
        e["experience_level"], e["posted_date"], e["application_deadline"],
        json.dumps(e),
        e["extractor_model"], e["source_url"],
        e["role_summary"],
        json.dumps(e["technical_keywords"]),
        json.dumps(e["sector_keywords"]),
        json.dumps(e["business_sectors"]),
        e["problem_being_solved"],
        json.dumps(e["useful_experiences"]),
    )
    print(f"  Inserted extracted details (extraction_run_id={extraction_run_id})")

    # Create agent run row (required by runner.py)
    agent_run = await conn.fetchrow(
        """
        INSERT INTO job_opening_agent_runs (opening_id, user_id, status)
        VALUES ($1, $2, 'running') RETURNING id
        """,
        opening_id, user_id,
    )
    run_id = agent_run["id"]
    print(f"  Created agent run id={run_id}")

    return user_id, opening_id, run_id


async def get_output_pdf(conn, user_id: int, opening_id: int) -> bytes | None:
    """Fetch the rendered PDF bytes from DB."""
    from app.features.job_tracker.opening_resume.latex_resume.service import get_resume_pdf
    result = await get_resume_pdf(conn, user_id, opening_id)
    if result:
        pdf_bytes, _ = result
        return pdf_bytes
    return None


async def run_demo(output_path: Path) -> None:
    import asyncpg
    from app.features.core.config import settings
    from app.features.job_tracker.agents.runner import run_agent_stream

    db_url = settings.database_url
    print(f"\n{'='*60}")
    print("  RESUME AGENT DEMO")
    print(f"{'='*60}")
    print(f"\n[INPUT] Job: {EXTRACTED_DETAILS['job_title']} @ {EXTRACTED_DETAILS['company_name']}")
    print(f"[INPUT] Candidate: {PROFILE_DATA['personal']['full_name']}")
    print(f"[OUTPUT] PDF -> {output_path}\n")

    print("Connecting to database...")
    try:
        conn = await asyncpg.connect(db_url, timeout=15)
    except (OSError, TimeoutError, Exception) as e:
        if not isinstance(e, (OSError, TimeoutError)):
            raise
        print(f"\n  [FAIL] Cannot connect to database: {e}")
        print("\n  The Aiven PostgreSQL service appears to be offline (free-tier auto-pause).")
        print("  To fix:")
        print("    1. Log in at https://console.aiven.io")
        print("    2. Find your PostgreSQL service and click 'Resume' or 'Power On'")
        print("    3. Wait ~60 seconds for the service to start")
        print("    4. Re-run: uv run python scripts/run_agent_demo.py")
        sys.exit(1)
    print("  Connected [OK]\n")

    try:
        # Check OpenRouter API key
        if not settings.openrouter_api_key:
            print("[FAIL] OPENROUTER_API_KEY not set in .env")
            print("  Add: OPENROUTER_API_KEY=sk-or-...")
            sys.exit(1)

        # Check migration has been applied (agent tables must exist)
        agent_table = await conn.fetchval(
            "SELECT to_regclass('public.job_opening_agent_runs')"
        )
        if agent_table is None:
            print("[FAIL] Migration not applied. Run: uv run alembic upgrade head")
            sys.exit(1)

        # Clean any leftover demo data from previous runs
        async with conn.transaction():
            await conn.execute(
                "UPDATE job_openings SET agent_run_id=NULL WHERE user_id IN "
                "(SELECT id FROM users WHERE email LIKE 'demo-agent-%')"
            )
            await conn.execute(
                "DELETE FROM job_opening_agent_runs WHERE opening_id IN "
                "(SELECT id FROM job_openings WHERE user_id IN "
                "(SELECT id FROM users WHERE email LIKE 'demo-agent-%'))"
            )
            await conn.execute("DELETE FROM users WHERE email LIKE 'demo-agent-%'")

        print("Setting up dummy data...")
        user_id, opening_id, run_id = await setup_demo_data(conn)

        print(f"\nRunning agent (opening_id={opening_id}, run_id={run_id})...")
        print("-" * 60)

        async for event in run_agent_stream(conn, user_id, opening_id, run_id):
            node = event.get("node", "?")
            status = event.get("status", "?")
            message = event.get("message", "")
            icon = "[OK]" if status == "completed" else "[FAIL]" if status in ("error", "failed") else "->"
            print(f"  {icon} [{node}] {message}")

        print("-" * 60)
        print("\nFetching rendered PDF...")
        pdf_bytes = await get_output_pdf(conn, user_id, opening_id)

        if pdf_bytes:
            output_path.write_bytes(pdf_bytes)
            print(f"\n{'='*60}")
            print(f"  [OK] PDF saved: {output_path} ({len(pdf_bytes):,} bytes)")
            print(f"{'='*60}\n")
        else:
            print("\n  [FAIL] No PDF found. The render node may have failed.")
            print("    Check agent events above for details.\n")

    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(description="Run the resume agent end-to-end demo")
    parser.add_argument("--output", default="demo_output.pdf", help="Output PDF path")
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    asyncio.run(run_demo(output_path))


if __name__ == "__main__":
    main()
