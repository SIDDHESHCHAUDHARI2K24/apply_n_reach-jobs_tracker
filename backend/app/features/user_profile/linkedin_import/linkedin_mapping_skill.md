# LinkedIn Import Mapping Skill

This skill defines how LinkedIn scrape payloads must map into `MappedLinkedInProfile` for `user_profile` import.

## Purpose
- Keep mapping behavior deterministic across agents and implementations.
- Ensure values inserted by `replace_profile_from_linkedin()` fit section schemas.
- Prevent drift between prompt output and database write expectations.

## Source-of-Truth Targets
- Schema target: `backend/app/features/user_profile/linkedin_import/schemas.py`
- Mapping execution: `backend/app/features/user_profile/linkedin_import/mapping_chain.py`
- Persistence behavior: `backend/app/features/user_profile/linkedin_import/service.py`

## Section Mapping Rules

### 1) Personal (`MappedPersonal`)
- `full_name`: person display name.
- `email`: best available email, else `null`.
- `linkedin_url`: profile URL from scrape or request URL fallback.
- `github_url` / `portfolio_url`: include only if confidently present.

### 2) Educations (`MappedEducation`)
- `university_name`: institution name (required).
- `major`: field of study, else empty string.
- `degree_type`: degree label, else empty string.
- `start_month_year`, `end_month_year`: `MM/YYYY` when date known; empty string or `null` when unknown.
- `bullet_points`: concise factual bullets only.
- `reference_links`: source links tied to that education item.

### 3) Experiences (`MappedExperience`)
- `role_title`: job title (required).
- `company_name`: employer (required).
- `start_month_year`, `end_month_year`: normalized month/year fields.
- `context`: one-line scope summary.
- `work_sample_links`: links demonstrably tied to role work.
- `bullet_points`: outcome-focused statements; no fabricated metrics.

### 4) Projects (`MappedProject`)
- `project_name`: project title (required).
- `description`: concise summary.
- `start_month_year`, `end_month_year`: normalized timeline.
- `reference_links`: project/repo/demo links.

### 5) Certifications (`MappedCertification`)
- `certification_name`: certificate/program title (required).
- `verification_link`: URL when present, else `null`.

### 6) Skills (`MappedSkill`)
- `kind`: use `"technical"` by default; use `"competency"` only for soft-skill style entries.
- `name`: canonicalized skill string.
- `sort_order`: dense integer ordering from `0..N`.

## Normalization Standards
- Date format: prefer `MM/YYYY`.
- Unknown values:
  - nullable fields -> `null`
  - string defaults in schema -> empty string
- Arrays default to `[]`, never `null`.
- Dedupe skills case-insensitively after trim.
- Preserve only high-confidence links.

## Example 1 — Happy Path
### Input (simplified LinkedIn-like)
```json
{
  "name": "Ava Stone",
  "linkedin_url": "https://linkedin.com/in/ava-stone",
  "experience": [
    {
      "title": "Product Manager",
      "company": "Northwind",
      "start": "Jan 2022",
      "end": "Present",
      "highlights": ["Launched onboarding revamp", "Improved activation"]
    }
  ],
  "education": [
    {
      "school": "State University",
      "degree": "B.S.",
      "field": "Computer Science",
      "start": "2016",
      "end": "2020"
    }
  ],
  "skills": ["SQL", "A/B Testing", "sql"]
}
```

### Output (mapped)
```json
{
  "personal": {
    "full_name": "Ava Stone",
    "email": null,
    "linkedin_url": "https://linkedin.com/in/ava-stone",
    "github_url": null,
    "portfolio_url": null
  },
  "educations": [
    {
      "university_name": "State University",
      "major": "Computer Science",
      "degree_type": "B.S.",
      "start_month_year": "01/2016",
      "end_month_year": "01/2020",
      "bullet_points": [],
      "reference_links": []
    }
  ],
  "experiences": [
    {
      "role_title": "Product Manager",
      "company_name": "Northwind",
      "start_month_year": "01/2022",
      "end_month_year": null,
      "context": "",
      "work_sample_links": [],
      "bullet_points": [
        "Launched onboarding revamp",
        "Improved activation"
      ]
    }
  ],
  "projects": [],
  "certifications": [],
  "skills": [
    {"kind": "technical", "name": "SQL", "sort_order": 0},
    {"kind": "technical", "name": "A/B Testing", "sort_order": 1}
  ]
}
```

## Example 2 — Sparse/Missing Fields
### Input
```json
{
  "name": "Noah Kim",
  "experience": [
    {
      "title": "Engineer",
      "company": "",
      "start": "",
      "end": "",
      "description": "Worked on internal tools"
    }
  ],
  "skills": []
}
```

### Mapping policy
- Missing `company` fails required experience quality; if unverifiable, omit the experience row.
- Missing dates map to empty string (`start_month_year`) and `null` (`end_month_year`) only when row remains valid.
- Empty skill list maps to `[]`.

## Example 3 — Long Description to Bullets
- Input description paragraph should be transformed into short factual bullets.
- Avoid generating invented numbers or outcomes.
- Keep bullets specific and resume-ready.

## Research / Publications (Not Supported in Current Schema)
- `MappedLinkedInProfile` does **not** include a `research` field.
- The `user_profile` domain has a research/`user_research` endpoint, but LinkedIn import currently does not map into it.
- Research/publication entries from LinkedIn scrapes are **ignored** by the import chain.
- To add research support: define `MappedResearch` in `schemas.py`, add the section to `MappedLinkedInProfile`, wire DELETE + INSERT in `service.py`, and update the LLM prompt and this skill document.

## Agent Instructions
1. Always read this skill before changing LinkedIn mapping behavior.
2. Keep outputs valid for `MappedLinkedInProfile`.
3. Do not change replace-all semantics in `service.py` unless explicitly requested.
4. If schema changes, update this skill in the same change set.
