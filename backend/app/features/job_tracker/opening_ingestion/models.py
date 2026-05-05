"""Models for opening_ingestion — DDL reference only; tables managed by Alembic."""

# DDL reference constants — actual tables created via Alembic migrations

CREATE_EXTRACTION_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS job_opening_extraction_runs (
    id               SERIAL PRIMARY KEY,
    opening_id       INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
    status           TEXT NOT NULL DEFAULT 'queued'
                         CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    attempt_number   INTEGER NOT NULL DEFAULT 1,
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    next_retry_at    TIMESTAMPTZ,
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""  # reference only

CREATE_EXTRACTED_DETAILS_TABLE = """
CREATE TABLE IF NOT EXISTS job_opening_extracted_details_versions (
    id                   SERIAL PRIMARY KEY,
    run_id               INTEGER NOT NULL REFERENCES job_opening_extraction_runs(id) ON DELETE CASCADE,
    opening_id           INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
    schema_version       INTEGER NOT NULL DEFAULT 1,
    job_title            TEXT,
    company_name         TEXT,
    location             TEXT,
    employment_type      TEXT,
    description_summary  TEXT,
    required_skills      JSONB,
    preferred_skills     JSONB,
    experience_level     TEXT,
    posted_date          TEXT,
    application_deadline TEXT,
    extracted_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_payload          JSONB,
    extractor_model      TEXT,
    source_url           TEXT
);
"""  # reference only


async def ensure_extraction_schema(conn) -> None:
    """No-op: schema managed by Alembic migrations."""
    pass
