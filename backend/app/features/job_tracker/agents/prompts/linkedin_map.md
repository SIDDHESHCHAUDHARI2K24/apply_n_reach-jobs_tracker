# LinkedIn Profile Mapping

## Role
Map scraped LinkedIn profile data to the application's `user_profile` section schemas. This is a structured output prompt — it produces a JSON object that can be directly submitted to the profile API endpoints. There are no tools; this is a pure transformation.

## Input
Raw LinkedIn profile data (scraped JSON or text) containing some or all of:
- Name, headline, location, summary/about
- Work experience entries
- Education entries
- Skills (LinkedIn skills list)
- Certifications / licenses
- Projects
- Publications / research

## Output
A structured JSON object conforming to the `user_profile` schema, ready for API submission.

---

## Mapping Rules

### Personal Section
Map to: `POST /profile` (personal details)

| LinkedIn Field | Profile Schema Field | Notes |
|---|---|---|
| `firstName` + `lastName` | `full_name` | Concatenate with a space |
| `headline` | `headline` | Keep as-is; may be edited later |
| `location.city` + `location.country` | `location` | "City, Country" format |
| `summary` / `about` | `summary` | Preserve line breaks as `\n`; max 2000 chars |
| `email` (if available) | `email` | May not be present in scrape |
| `publicProfileUrl` | `linkedin_url` | Full URL |
| `websites[0]` | `website_url` | First listed personal site |
| `github` (if detected in websites/contact) | `github_url` | Extract from contact info |

**Thought**: If `summary` is missing or empty, leave `summary` as `null` — do not synthesize from the headline.

---

### Experience Section
Map to: `POST /profile/experience` (one request per entry)

For each `positions` entry in LinkedIn:

| LinkedIn Field | Experience Schema Field | Notes |
|---|---|---|
| `title` | `job_title` | Exact title |
| `companyName` | `company` | Exact company name |
| `location` | `location` | City/Remote as provided |
| `startDate.year` + `startDate.month` | `start_date` | Format as `"YYYY-MM"` |
| `endDate.year` + `endDate.month` | `end_date` | `null` if `isCurrent: true` |
| `isCurrent` | `is_current` | Boolean |
| `description` | `bullets` | **Transform required — see below** |

**Transforming description to bullets**:
LinkedIn descriptions are unstructured paragraphs or bullet lists. Convert them as follows:

1. If the description contains line-separated bullet points (beginning with `•`, `-`, `*`, or newline-separated sentences):
   - Split on those delimiters
   - Trim whitespace
   - Store each as a separate string in `bullets: ["...", "...", ...]`

2. If the description is one long paragraph:
   - Split on `. ` (period + space) to approximate sentence boundaries
   - Store each sentence as a bullet
   - Maximum 6 bullets; truncate beyond that

3. If description is empty or missing:
   - Set `bullets: []`

**Ordering**: Preserve LinkedIn's original ordering (usually reverse-chronological).

---

### Education Section
Map to: `POST /profile/education`

For each `educations` entry:

| LinkedIn Field | Education Schema Field | Notes |
|---|---|---|
| `schoolName` | `institution` | Exact name |
| `degreeName` | `degree` | e.g., "Bachelor of Science" |
| `fieldOfStudy` | `field_of_study` | e.g., "Computer Science" |
| `startDate.year` | `start_year` | Integer year |
| `endDate.year` | `end_year` | Integer year; `null` if ongoing |
| `grade` | `gpa` | Parse float if possible; null if non-numeric |
| `activities` | `activities` | Short string; truncate to 500 chars |
| `description` | `notes` | Any additional details |

**GPA parsing**:
- `"3.8/4.0"` → extract `3.8`
- `"First Class Honours"` → map to `null` (non-numeric, store raw in notes)
- `"Magna Cum Laude"` → `null` (store in notes)

---

### Skills Section
Map to: `PATCH /profile/skills` (full replace)

LinkedIn returns a flat list of skill names. Group them into categories using the following heuristics:

**Category assignment rules**:
1. Check each skill against known keyword lists (see `skills/determine_technical_keywords.md`):
   - Programming languages → "Languages"
   - Frameworks and libraries → "Frameworks & Libraries"
   - Cloud platforms and DevOps tools → "Infrastructure & DevOps"
   - Databases → "Data & Databases"
   - Methodologies (Agile, TDD, CI/CD) → "Methodologies"
2. Skills that don't match technical categories → "Other" or "Domain"

Output format:
```json
{
  "skills": {
    "Languages": ["Python", "TypeScript", "SQL"],
    "Frameworks & Libraries": ["React", "FastAPI", "Pandas"],
    "Infrastructure & DevOps": ["Docker", "AWS", "Terraform"],
    "Data & Databases": ["PostgreSQL", "Redis", "Snowflake"],
    "Methodologies": ["Agile/Scrum", "CI/CD", "TDD"],
    "Other": ["Public Speaking", "Technical Writing"]
  }
}
```

---

### Certifications Section
Map to: `POST /profile/certifications`

| LinkedIn Field | Certifications Schema Field | Notes |
|---|---|---|
| `name` | `name` | Exact name |
| `authority` | `issuer` | Issuing organization |
| `timePeriod.startDate` | `issued_date` | Format: `"YYYY-MM"` |
| `timePeriod.endDate` | `expiry_date` | `null` if no expiry |
| `licenseNumber` | `credential_id` | Optional |
| `url` | `credential_url` | Verification link |

---

### Projects Section
Map to: `POST /profile/projects`

| LinkedIn Field | Projects Schema Field | Notes |
|---|---|---|
| `title` | `title` | Exact title |
| `description` | `description` | Preserve as-is; max 1000 chars |
| `url` | `project_url` | Optional |
| `startDate` | `start_date` | Format: `"YYYY-MM"` |
| `endDate` | `end_date` | `null` if ongoing |
| (infer from description) | `tech_stack` | Extract tool/language names from description using `skills/determine_technical_keywords.md` patterns; return as list |

---

### Research / Publications Section
Map to: `POST /profile/research`

| LinkedIn Field | Research Schema Field | Notes |
|---|---|---|
| `title` | `title` | Publication/paper title |
| `publisher` | `publisher` | Journal, conference, or platform |
| `date` | `published_date` | Format: `"YYYY-MM"` |
| `description` | `summary` | Abstract or description |
| `url` | `publication_url` | DOI or link |
| `authors` | `authors` | Comma-separated string |

---

## Full Output Structure

The mapping node returns:

```json
{
  "personal": { "full_name": "...", "headline": "...", "summary": "...", "location": "...", "linkedin_url": "...", "github_url": "...", "website_url": "..." },
  "experience": [
    { "job_title": "...", "company": "...", "start_date": "YYYY-MM", "end_date": "YYYY-MM | null", "is_current": false, "bullets": ["...", "..."] }
  ],
  "education": [
    { "institution": "...", "degree": "...", "field_of_study": "...", "start_year": 2018, "end_year": 2022, "gpa": 3.8 }
  ],
  "skills": { "Languages": ["..."], "Frameworks & Libraries": ["..."] },
  "certifications": [
    { "name": "...", "issuer": "...", "issued_date": "YYYY-MM", "expiry_date": "YYYY-MM | null" }
  ],
  "projects": [
    { "title": "...", "description": "...", "tech_stack": ["..."], "project_url": "..." }
  ],
  "research": [
    { "title": "...", "publisher": "...", "published_date": "YYYY-MM", "summary": "..." }
  ],
  "mapping_notes": "string | null (any fields that could not be mapped or had ambiguous data)"
}
```

## Error handling
- Missing required fields (e.g., no `full_name`): Use `null` — do not fabricate
- Truncated descriptions: Note in `mapping_notes`
- Unrecognized date formats: Set the date field to `null` and log in `mapping_notes`
- LinkedIn data that appears incomplete or truncated (e.g., private profile): Note in `mapping_notes`
