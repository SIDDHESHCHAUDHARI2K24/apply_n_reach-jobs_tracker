-- ============================================================
-- FastAPI Tutorial T2 - Complete Database Setup Script
-- Run this in pgAdmin 4 Query Tool on a fresh database
-- ============================================================

-- Auth tables (created lazily by app, must exist before Alembic tables)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- ============================================================
-- Alembic migrations (all versions in sequence)
-- ============================================================
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 1e74ccf552b8

INSERT INTO alembic_version (version_num) VALUES ('1e74ccf552b8') RETURNING alembic_version.version_num;

-- Running upgrade 1e74ccf552b8 -> a1b2c3d4e5f6

CREATE TABLE IF NOT EXISTS user_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS personal_details (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL UNIQUE REFERENCES user_profiles(id) ON DELETE CASCADE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        linkedin_url TEXT NOT NULL,
        github_url TEXT,
        portfolio_url TEXT
    );

UPDATE alembic_version SET version_num='a1b2c3d4e5f6' WHERE alembic_version.version_num = '1e74ccf552b8';

-- Running upgrade a1b2c3d4e5f6 -> b2c3d4e5f6a7

CREATE TABLE IF NOT EXISTS educations (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        university_name TEXT NOT NULL,
        major TEXT NOT NULL,
        degree_type TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        bullet_points JSONB NOT NULL DEFAULT '[]',
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS experiences (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        role_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        context TEXT NOT NULL DEFAULT '',
        work_sample_links JSONB NOT NULL DEFAULT '[]',
        bullet_points JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        project_name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS researches (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        paper_name TEXT NOT NULL,
        publication_link TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS skill_items (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS certifications (
        id SERIAL PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
        certification_name TEXT NOT NULL,
        verification_link TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

UPDATE alembic_version SET version_num='b2c3d4e5f6a7' WHERE alembic_version.version_num = 'a1b2c3d4e5f6';

-- Running upgrade b2c3d4e5f6a7 -> c3d4e5f6a7b8

CREATE TABLE IF NOT EXISTS job_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        profile_name TEXT NOT NULL,
        target_role TEXT,
        target_company TEXT,
        job_posting_url TEXT,
        status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(user_id, profile_name)
    );

CREATE TABLE IF NOT EXISTS job_profile_personal_details (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL UNIQUE REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_personal_id INTEGER REFERENCES personal_details(id) ON DELETE SET NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        linkedin_url TEXT NOT NULL,
        github_url TEXT,
        portfolio_url TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_educations (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_education_id INTEGER REFERENCES educations(id) ON DELETE SET NULL,
        university_name TEXT NOT NULL,
        major TEXT NOT NULL,
        degree_type TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        bullet_points JSONB NOT NULL DEFAULT '[]',
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_experiences (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_experience_id INTEGER REFERENCES experiences(id) ON DELETE SET NULL,
        role_title TEXT NOT NULL,
        company_name TEXT NOT NULL,
        start_month_year TEXT NOT NULL,
        end_month_year TEXT,
        context TEXT NOT NULL DEFAULT '',
        work_sample_links JSONB NOT NULL DEFAULT '[]',
        bullet_points JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_projects (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
        project_name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        start_month_year TEXT,
        end_month_year TEXT,
        reference_links JSONB NOT NULL DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_researches (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_research_id INTEGER REFERENCES researches(id) ON DELETE SET NULL,
        paper_name TEXT NOT NULL,
        publication_link TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_certifications (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        source_certification_id INTEGER REFERENCES certifications(id) ON DELETE SET NULL,
        certification_name TEXT NOT NULL,
        verification_link TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE TABLE IF NOT EXISTS job_profile_skill_items (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL REFERENCES job_profiles(id) ON DELETE CASCADE,
        kind TEXT NOT NULL CHECK (kind IN ('technical', 'competency')),
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

UPDATE alembic_version SET version_num='c3d4e5f6a7b8' WHERE alembic_version.version_num = 'b2c3d4e5f6a7';

-- Running upgrade c3d4e5f6a7b8 -> d4e5f6a7b8c9

CREATE TABLE IF NOT EXISTS rendered_resume (
        id SERIAL PRIMARY KEY,
        job_profile_id INTEGER NOT NULL UNIQUE REFERENCES job_profiles(id) ON DELETE CASCADE,
        latex_source TEXT NOT NULL,
        pdf_content BYTEA NOT NULL,
        layout_json JSONB NOT NULL DEFAULT '{}'::jsonb,
        template_name TEXT NOT NULL DEFAULT 'jakes_resume_v1',
        rendered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

UPDATE alembic_version SET version_num='d4e5f6a7b8c9' WHERE alembic_version.version_num = 'c3d4e5f6a7b8';

-- Running upgrade d4e5f6a7b8c9 -> b81c3184eb7c

CREATE TABLE job_openings (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        job_profile_id INTEGER REFERENCES job_profiles(id) ON DELETE SET NULL,
        source_url TEXT,
        company_name TEXT NOT NULL,
        role_name TEXT NOT NULL,
        current_status TEXT NOT NULL DEFAULT 'Interested' CHECK (current_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected')),
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE INDEX ix_job_openings_user_id ON job_openings(user_id);

CREATE INDEX ix_job_openings_current_status ON job_openings(current_status);

CREATE INDEX ix_job_openings_created_at ON job_openings(created_at);

CREATE TABLE job_opening_status_history (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        from_status TEXT,
        to_status TEXT NOT NULL,
        changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        changed_by_user_id INTEGER NOT NULL REFERENCES users(id)
    );

CREATE INDEX ix_status_history_opening_id ON job_opening_status_history(opening_id);

CREATE TABLE job_opening_extraction_runs (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed')),
        attempt_number INTEGER NOT NULL DEFAULT 1,
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        next_retry_at TIMESTAMPTZ,
        error_message TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE INDEX ix_extraction_runs_opening_id_status ON job_opening_extraction_runs(opening_id, status);

CREATE TABLE job_opening_extracted_details_versions (
        id SERIAL PRIMARY KEY,
        run_id INTEGER NOT NULL REFERENCES job_opening_extraction_runs(id) ON DELETE CASCADE,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
        schema_version INTEGER NOT NULL DEFAULT 1,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        employment_type TEXT,
        salary_range TEXT,
        description_summary TEXT,
        required_skills JSONB,
        preferred_skills JSONB,
        experience_level TEXT,
        posted_date TEXT,
        application_deadline TEXT,
        extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        raw_payload JSONB,
        extractor_model TEXT,
        source_url TEXT
    );

CREATE INDEX ix_extracted_details_opening_id ON job_opening_extracted_details_versions(opening_id);

CREATE TABLE job_opening_resumes (
        id SERIAL PRIMARY KEY,
        opening_id INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE UNIQUE,
        source_job_profile_id INTEGER REFERENCES job_profiles(id) ON DELETE SET NULL,
        snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        snapshot_version INTEGER NOT NULL DEFAULT 1,
        source_section_count INTEGER NOT NULL DEFAULT 7  -- 7 resume sections: personal, education, experience, projects, research, certifications, skills; set by service layer at snapshot time
    );

CREATE TABLE job_opening_personal (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE UNIQUE,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        linkedin_url TEXT,
        github_url TEXT,
        portfolio_url TEXT,
        summary TEXT
    );

CREATE TABLE job_opening_education (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        institution TEXT NOT NULL,
        degree TEXT,
        field_of_study TEXT,
        start_date TEXT,
        end_date TEXT,
        grade TEXT,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE job_opening_experience (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        company TEXT NOT NULL,
        title TEXT NOT NULL,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        is_current BOOLEAN NOT NULL DEFAULT FALSE,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE job_opening_projects (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        url TEXT,
        start_date TEXT,
        end_date TEXT,
        technologies JSONB,
        display_order INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE job_opening_research (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        publication TEXT,
        published_date TEXT,
        url TEXT,
        description TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE job_opening_certifications (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        issuer TEXT,
        issue_date TEXT,
        expiry_date TEXT,
        credential_id TEXT,
        url TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    );

CREATE TABLE job_opening_skills (
        id SERIAL PRIMARY KEY,
        resume_id INTEGER NOT NULL REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        proficiency_level TEXT,
        display_order INTEGER NOT NULL DEFAULT 0
    );

UPDATE alembic_version SET version_num='b81c3184eb7c' WHERE alembic_version.version_num = 'd4e5f6a7b8c9';

-- Running upgrade b81c3184eb7c -> 89bfcfd36bee

ALTER TABLE job_opening_status_history
          ADD CONSTRAINT chk_status_history_to_status
          CHECK (to_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected'));

ALTER TABLE job_opening_status_history
          ADD CONSTRAINT chk_status_history_from_status
          CHECK (from_status IN ('Interested','Applied','Interviewing','Offer','Withdrawn','Rejected') OR from_status IS NULL);

UPDATE alembic_version SET version_num='89bfcfd36bee' WHERE alembic_version.version_num = 'b81c3184eb7c';

-- Running upgrade 89bfcfd36bee -> a9c2e41fd6b0

CREATE TABLE IF NOT EXISTS job_opening_rendered_resumes (
            id SERIAL PRIMARY KEY,
            resume_id INTEGER NOT NULL UNIQUE REFERENCES job_opening_resumes(id) ON DELETE CASCADE,
            latex_source TEXT NOT NULL,
            pdf_bytes BYTEA NOT NULL,
            template_name TEXT NOT NULL DEFAULT 'jakes_resume_v1',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE INDEX IF NOT EXISTS ix_job_opening_rendered_resumes_updated_at ON job_opening_rendered_resumes(updated_at);

UPDATE alembic_version SET version_num='a9c2e41fd6b0' WHERE alembic_version.version_num = '89bfcfd36bee';

-- Running upgrade a9c2e41fd6b0 -> e5f6a7b8c9d0

ALTER TABLE job_openings
            ADD COLUMN agent_status TEXT NOT NULL DEFAULT 'idle'
                CHECK (agent_status IN ('idle', 'running', 'succeeded', 'failed')),
            ADD COLUMN agent_run_id INTEGER,
            ADD COLUMN agent_state JSONB;

CREATE TABLE job_opening_agent_runs (
            id                SERIAL PRIMARY KEY,
            opening_id        INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
            user_id           INTEGER NOT NULL REFERENCES users(id),
            status            TEXT NOT NULL DEFAULT 'running'
                                  CHECK (status IN ('running', 'succeeded', 'failed', 'cancelled')),
            current_node      TEXT,
            state             JSONB,
            events            JSONB NOT NULL DEFAULT '[]'::jsonb,
            error_message     TEXT,
            started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at      TIMESTAMPTZ,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

CREATE INDEX ix_agent_runs_opening ON job_opening_agent_runs(opening_id);

ALTER TABLE job_openings
            ADD CONSTRAINT fk_job_openings_agent_run_id
                FOREIGN KEY (agent_run_id) REFERENCES job_opening_agent_runs(id);

ALTER TABLE job_opening_extracted_details_versions
            ADD COLUMN role_summary TEXT,
            ADD COLUMN technical_keywords JSONB,
            ADD COLUMN sector_keywords JSONB,
            ADD COLUMN business_sectors JSONB,
            ADD COLUMN problem_being_solved TEXT,
            ADD COLUMN useful_experiences JSONB;

ALTER TABLE job_profiles
            ADD COLUMN summary TEXT;

UPDATE alembic_version SET version_num='e5f6a7b8c9d0' WHERE alembic_version.version_num = 'a9c2e41fd6b0';

COMMIT;

-- ============================================================
-- Running upgrade e5f6a7b8c9d0 -> j0j1k2l3m4n5
-- (includes all intermediate migrations: f6a7b8c9d0e1, g7h8i9j0k1l2, h8i9j0k1l2m3, i9j0k1l2m3n4, 0005_jp_parity_schema_updates)
-- ============================================================

-- f6a7b8c9d0e1: add experience location columns
ALTER TABLE experiences ADD COLUMN IF NOT EXISTS location TEXT;

-- g7h8i9j0k1l2: add personal summary/location/phone
ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS location TEXT;
ALTER TABLE personal_details ADD COLUMN IF NOT EXISTS phone TEXT;

-- h8i9j0k1l2m3: add research journal/year
ALTER TABLE researches ADD COLUMN IF NOT EXISTS journal_name TEXT;
ALTER TABLE researches ADD COLUMN IF NOT EXISTS publication_year TEXT;

-- i9j0k1l2m3n4: add projects technologies
ALTER TABLE projects ADD COLUMN IF NOT EXISTS technologies JSONB NOT NULL DEFAULT '[]';

-- 0005_jp_parity_schema_updates: JP parity schema updates
ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS location TEXT;
ALTER TABLE job_profile_personal_details ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE job_profile_researches ADD COLUMN IF NOT EXISTS journal_name TEXT;
ALTER TABLE job_profile_researches ADD COLUMN IF NOT EXISTS publication_year TEXT;
ALTER TABLE job_profile_projects ADD COLUMN IF NOT EXISTS technologies JSONB NOT NULL DEFAULT '[]';

-- j0j1k2l3m4n5: add email agent runs table
CREATE TABLE IF NOT EXISTS job_opening_email_agent_runs (
    id                SERIAL PRIMARY KEY,
    opening_id        INTEGER NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
    user_id           INTEGER NOT NULL REFERENCES users(id),
    status            TEXT NOT NULL DEFAULT 'running'
                          CHECK (status IN ('idle', 'running', 'paused', 'succeeded', 'failed')),
    current_node      TEXT,
    state             JSONB,
    events            JSONB NOT NULL DEFAULT '[]'::jsonb,
    error_message     TEXT,
    started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at      TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_email_agent_runs_opening ON job_opening_email_agent_runs(opening_id);

UPDATE alembic_version SET version_num='j0j1k2l3m4n5' WHERE alembic_version.version_num = 'e5f6a7b8c9d0';

