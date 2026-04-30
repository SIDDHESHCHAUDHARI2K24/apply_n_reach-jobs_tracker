# Development Plan: UI & Data Schema Bug Fixes + Job Profile Section Editors
## apply_n_reach — Jobs Tracker Backend + Frontend

> **Reference Documents:**
>
> - [User Profile Development Plan](../user-profile-development-plan.md)
> - [Job Profile Development Plan](../job-profile%20feature/development-plan.md)
> - [LaTeX Resume Rendering Plan](../latex-resume/latex-render-feature.md)
> - [Frontend Development Plan](../frontend/development-plan.md)

---

## Executive Summary

This plan addresses four interconnected bug-fix and feature gaps discovered during integration testing:

1. **Month & Year Picker** — All user-profile date fields (`start_date`, `end_date`) currently use plain text `<input>` elements with `placeholder="MM/YYYY"` and zero validation. These must be replaced with a proper month/year picker component.
2. **Job Profile Personal Details API Mismatch** — The frontend `jobProfileApi.updatePersonal` sends only 5 of 8 fields, and `mapPersonal` hardcodes `phone`, `location`, `summary` to `null`. The generated OpenAPI spec is also stale (missing 3 fields from commit `153da63`).
3. **Job Profile Section Editors** — Job profile sections show a read-only summary with raw JSON dump. No inline editing exists. This must be upgraded to match the user-profile editing experience with per-section forms, lists, and hooks.
4. **Render Resume 404** — Frontend calls `/job-profiles/{id}/resume/render` but the backend route prefix is `/job-profiles/{job_profile_id}/latex-resume`. This is a path segment mismatch (`resume` vs `latex-resume`).

- **Total phases:** 2 (P1: targeted fixes, P2: section editors)
- **Estimated total effort:** 3–5 days solo / 1.5–3 days with parallel agents
- **Stack:** React + TypeScript + Tailwind (frontend), FastAPI + asyncpg (backend)

**Top 3 Risks**

1. **OpenAPI spec regeneration fails** — The `openapi-ts` tool currently fails with "not a valid JSON Schema" error, blocking generated type updates. Mitigation: manually fix the OpenAPI JSON or regenerate from a running backend instance.
2. **Section editor duplication** — Building 6 separate form+list+hook modules could duplicate user-profile code. Mitigation: extract a shared `SectionCrud` generic pattern or copy-paste-adjust the user-profile patterns (faster, lower risk of breaking existing code).
3. **Import flow after editing** — After importing and then editing a job profile section, re-importing could overwrite edits. Mitigation: keep the additive-only import semantics; user must manually delete items before re-import.

---

## Phase Overview

| Phase | Name | Focus | Key Deliverables | Effort | Depends On |
| --- | --- | --- | --- | --- | --- |
| P1 | Targeted Bug Fixes | Month/Year picker, personal details API fix, render-resume URL fix | `MonthYearPicker` component, fixed `jobProfileApi` personal fields + mapping, fixed resume URLs, regenerated OpenAPI types | M / 1–2 days | — |
| P2 | Job Profile Section Editors | Full CRUD editors for all 6 job-profile sections | Per-section List + Form + Hook for education, experience, projects, research, certifications, skills | XL / 2–3 days | P1 |

---

## Phase 1: Targeted Bug Fixes

### Overview
- **Goal:** Fix the three concrete bugs: (1) replace plain text date inputs with month/year picker, (2) fix job profile personal details API layer, (3) fix render resume URL.
- **Entry criteria:** Dev environment running, frontend `npm run dev` works, backend `uvicorn` serves on port 8000.
- **Exit criteria:** MonthYearPicker renders in all 3 forms, personal details save all 8 fields from JP editor, Render Resume button triggers render successfully.

---

### Task P1.T1: Create Reusable MonthYearPicker Component

**Feature:** Month & Year Picker for date fields
**Effort:** M / 2–3 hours
**Dependencies:** None
**Risk Level:** Low — pure frontend component, no backend changes.

#### Sub-task P1.T1.S1: Create MonthYearPicker component

**Files:** `frontend/src/components/MonthYearPicker.tsx`

**Description:** Create a controlled React component that lets users select a month (1-12) and year (current year ± 50). The component accepts `value: string` (format `MM/YYYY`), `onChange: (value: string) => void`, and standard HTML input props (`placeholder`, `className`, `required`). It renders two `<select>` dropdowns side-by-side: one for month (showing abbreviated names like "Jan", "Feb", ...) and one for year (4-digit). When either changes, it calls `onChange` with the combined `MM/YYYY` string.

**Implementation Hints:**
- Use `useMemo` to generate year options dynamically: `Array.from({length: 100}, (_, i) => new Date().getFullYear() - 50 + i)`
- Use `useState` for local `selectedMonth` and `selectedYear`, synced from `value` prop via `useEffect`
- Month options: `['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']`
- Internal value format: `month` is 1-indexed (01-12), `year` is 4-digit
- Export from a barrel: `frontend/src/components/index.ts`
- Use Tailwind `inputClass` styling matching the project convention

**Dependencies:** None
**Effort:** S / 1–1.5 hours
**Risk Flags:** None.
**Acceptance Criteria:**
- Component renders two select dropdowns (month + year)
- Selecting "Mar" / "2024" calls `onChange("03/2024")`
- Receiving `value="05/2022"` selects "May" and "2022"
- Empty/null value shows placeholder text in month dropdown
- Component is accessible (labels, `aria-label` on selects)

#### Sub-task P1.T1.S2: Integrate MonthYearPicker into EducationForm, ExperienceForm, ProjectForm

**Files:**
- `frontend/src/features/user-profile/sections/education/EducationForm.tsx`
- `frontend/src/features/user-profile/sections/experience/ExperienceForm.tsx`
- `frontend/src/features/user-profile/sections/projects/ProjectForm.tsx`

**Description:** Replace the plain `<input>` elements for `start_date` and `end_date` with the `MonthYearPicker` component. The `handleChange` handler needs a small adapter since MonthYearPicker calls `onChange` with the formatted string directly.

**Implementation Hints:**
- For ExperienceForm: add an "Is Current" checkbox that, when checked, clears `end_date` and disables the MonthYearPicker for end date
- Import: `import { MonthYearPicker } from '@components/MonthYearPicker'`
- The handler becomes: `onChange={(val) => setForm(f => ({ ...f, start_date: val }))}`
- ResearchForm: change the year field from `maxLength={4}` text input to a `<select>` year picker (or keep as number input with `type="number"` and `min`/`max` validation)

**Dependencies:** P1.T1.S1
**Effort:** S / 30–45 mins
**Risk Flags:** Ensure existing form validation (fromForm/toForm) preserves the date format. Add "is_current" toggle to ExperienceForm as a UX improvement.
**Acceptance Criteria:**
- EducationForm shows month+year dropdowns for start/end dates, no more plain text inputs
- ExperienceForm shows month+year dropdowns for start/end dates, with "Is Current" checkbox
- ProjectForm shows month+year dropdowns for start/end dates
- ResearchForm year field is a number input or select (not plain text with maxLength)
- Creating/editing items with dates still works through the API layer

---

### Task P1.T2: Fix Job Profile Personal Details API Layer

**Feature:** Job Profile Personal Details — Backend-Frontend Data Flow
**Effort:** M / 1.5–2 hours
**Dependencies:** None (can run parallel to P1.T1)
**Risk Level:** Medium — OpenAPI spec regeneration may fail.

#### Sub-task P1.T2.S1: Regenerate OpenAPI spec from running backend

**Files:** `frontend/src/generated/openapi.json`

**Description:** Regenerate the OpenAPI spec from the running FastAPI backend to capture the 3 new fields (`summary`, `location`, `phone`) added in commit `153da63`. The existing `openapi.json` is stale and the `openapi-ts` tool errors on it.

**Implementation Hints:**
- Start the backend server: `cd backend && uvicorn app.main:app --reload`
- Fetch the spec: `curl http://localhost:8000/openapi.json -o frontend/src/generated/openapi.json`
- If the `openapi-ts` tool still fails, manually add the 3 fields to `JPPersonalDetailsUpdate`, `JPPersonalDetailsResponse`, `PersonalDetailsUpdate`, `PersonalDetailsResponse` in `openapi.json`
- Run `npm run generate:types` (or equivalent) to regenerate `schema.ts` and `contracts.ts`

**Dependencies:** Backend server running
**Effort:** S / 30 mins
**Risk Flags:** The `openapi-ts` error log shows "is not a valid JSON Schema" — this may require manual JSON patching or a different generation approach.
**Acceptance Criteria:**
- `openapi.json` contains `phone`, `location`, `summary` in `JPPersonalDetailsUpdate` and `JPPersonalDetailsResponse`
- Generated `schema.ts` types reflect the new fields

#### Sub-task P1.T2.S2: Fix mapPersonal to include all 8 fields

**Files:** `frontend/src/features/job-profiles/jobProfileApi.ts`

**Description:** Fix `mapPersonal` (lines 43-57) to stop hardcoding `phone`, `location`, `summary` to `null`. These fields exist in the backend response and should be mapped through.

**Implementation Hints:**
- Change `phone: null` → `phone: (row as any).phone ?? null` (same pattern as user-profile `profileApi.ts`)
- Change `location: null` → `location: (row as any).location ?? null`
- Change `summary: null` → `summary: (row as any).summary ?? null`
- Once types are regenerated, replace `(row as any)` with proper type access

**Dependencies:** P1.T2.S1
**Effort:** XS / 10 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- `getPersonal()` returns non-null `phone`, `location`, `summary` when backend has values
- No type errors in TypeScript

#### Sub-task P1.T2.S3: Fix updatePersonal to send all 8 fields

**Files:** `frontend/src/features/job-profiles/jobProfileApi.ts`

**Description:** Fix `updatePersonal` (lines 162-174) to include `summary`, `location`, `phone` in the PATCH request body. Currently only 5 fields are sent.

**Implementation Hints:**
- Add to the body object:
  ```typescript
  summary: data.summary ?? undefined,
  location: data.location ?? undefined,
  phone: data.phone ?? undefined,
  ```

**Dependencies:** P1.T2.S1
**Effort:** XS / 5 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- `updatePersonal()` sends all 8 fields in the request body
- No data loss when saving personal details from a job profile editor

#### Sub-task P1.T2.S4: Fix JPSectionContent personal display

**Files:** `frontend/src/features/job-profiles/editor/JPSectionContent.tsx`

**Description:** Update the personal section summary to show all 8 fields (including phone, location, summary) instead of only name, email, headline. Remove the `headline` field reference (which doesn't exist in the backend schema).

**Implementation Hints:**
- Add display rows for `phone`, `location`, `summary` in the personal section block
- Remove the `headline` check (dead code — `headline` doesn't exist in `JPPersonal` type)
- Add display for `linkedin_url`, `github_url`, `portfolio_url` as clickable links

**Dependencies:** P1.T2.S2
**Effort:** XS / 15 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- Personal section displays all 8 fields when present
- No reference to non-existent `headline` field
- Social URLs are clickable links

---

### Task P1.T3: Fix Render Resume URL Mismatch

**Feature:** Render Resume Button — 404 Fix
**Effort:** XS / 10 mins
**Dependencies:** None
**Risk Level:** Low — simple string replacement.

#### Sub-task P1.T3.S1: Fix resume endpoint paths in jobProfileApi

**Files:** `frontend/src/features/job-profiles/jobProfileApi.ts`

**Description:** Fix the three resume-related URL paths in `triggerRender`, `getResumeMetadata`, and `downloadPdf` (lines 390-396). The frontend uses `resume` but the backend uses `latex-resume`.

**Current → Fixed:**
- `/job-profiles/${jpId}/resume/render` → `/job-profiles/${jpId}/latex-resume/render`
- `/job-profiles/${jpId}/resume/metadata` → `/job-profiles/${jpId}/latex-resume` (no `/metadata` suffix — backend serves metadata at bare GET)
- `/job-profiles/${jpId}/resume/pdf` → `/job-profiles/${jpId}/latex-resume/pdf`

**Implementation Hints:**
- The backend `latex_resume/router.py` defines prefix `/job-profiles/{job_profile_id}/latex-resume` with endpoints: `POST /render`, `GET ""`, `GET /pdf`

**Dependencies:** None
**Effort:** XS / 5 mins
**Risk Flags:** The frontend `useJPLatexRender.ts` hook may also have hardcoded paths — verify and fix if needed.
**Acceptance Criteria:**
- Clicking "Render Resume" calls `POST /job-profiles/{id}/latex-resume/render` and receives 200 (or 201/202)
- Metadata polling calls `GET /job-profiles/{id}/latex-resume` (correct path)
- PDF download calls `GET /job-profiles/{id}/latex-resume/pdf`

---

## Phase 2: Job Profile Section Editors

### Overview
- **Goal:** Replace the read-only `JPSectionContent` summary for each job-profile section with full CRUD editors matching the user-profile experience.
- **Features addressed:** Education, Experience, Projects, Research, Certifications, Skills editors for job profiles.
- **Entry criteria:** P1 complete (personal details flowing correctly, resume renders).
- **Exit criteria:** All 6 job-profile sections support: view list, add new, inline edit, delete, import from user profile. UI matches user-profile styling.

---

### Task P2.T1: Build JP Education Editor (List + Form + Hook)

**Feature:** Job Profile Education Section Editor
**Effort:** M / 1–1.5 hours
**Dependencies:** P1 complete
**Risk Level:** Medium — needs careful API field name mapping.

#### Sub-task P2.T1.S1: Create JPEducationList component

**Files:** `frontend/src/features/job-profiles/sections/education/JPEducationList.tsx`

**Description:** Create a list component for job profile education entries. Follow the same pattern as `user-profile/sections/education/EducationList.tsx` but using `jobProfileApi` for CRUD operations. Display: institution (bold), degree + field_of_study, date range. Each item has edit and delete actions.

**Implementation Hints:**
- Copy the structure from `EducationList.tsx` as base, adapt:
  - API calls use `jobProfileApi` instead of `profileApi`
  - Props include `jobProfileId: string`
  - Field names use JP conventions: `institution`, `degree`, `field_of_study`, `start_date`, `end_date`
  - Import shared types from `@features/user-profile/types` where applicable (Education interface is identical)
- States: `isEditing`, `isSaving`, `error`, `items`
- Delete shows confirmation dialog

**Dependencies:** None (within P2)
**Effort:** S / 30 mins
**Risk Flags:** Watch for field name differences between JP and UP API (e.g., `university_name` → `institution` in frontend type but `university_name` in API payload).
**Acceptance Criteria:**
- Lists all JP education entries with institution/degree/dates
- Edit button opens inline form
- Delete button with confirmation removes item
- Empty state shows "No education entries" + import prompt

#### Sub-task P2.T1.S2: Create JPEducationForm component

**Files:** `frontend/src/features/job-profiles/sections/education/JPEducationForm.tsx`

**Description:** Create the education editing form, reusing `MonthYearPicker` from P1. Fields: Institution*, Degree*, Field of Study, Start Date, End Date, Reference Links, Bullet Points (textarea, one per line).

**Implementation Hints:**
- Copy `EducationForm.tsx` structure, adapt to JP field naming
- Use `MonthYearPicker` for date fields
- Include `reference_links` field (present in JP API but not in UP education form currently)
- Bullet points: textarea, empty lines filtered, one per line
- Props: `initial` (JPEducation | null), `onSave`, `onCancel`, `isSaving`

**Dependencies:** P2.T1.S1, P1.T1.S1
**Effort:** S / 30 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- All fields render and are editable
- Save calls `jobProfileApi.createEducation` or `jobProfileApi.updateEducation` based on presence of `initial.id`
- Cancel resets form and calls `onCancel`
- Validation: institution and degree are required

#### Sub-task P2.T1.S3: Create useJPEducation hook

**Files:** `frontend/src/features/job-profiles/sections/education/useJPEducation.ts`

**Description:** Custom hook managing education CRUD state for a job profile. Pattern: same as `user-profile/sections/education/useEducation.ts`.

**Implementation Hints:**
- Exports: `{ items, isLoading, error, load, create, update, remove, import: importAll }`
- `load(jobProfileId)` → calls `jobProfileApi.getEducation(jobProfileId)`
- `create(jobProfileId, data)` → calls `jobProfileApi.createEducation(jobProfileId, data)`
- `update(jobProfileId, itemId, data)` → calls `jobProfileApi.updateEducation(jobProfileId, itemId, data)`
- `remove(jobProfileId, itemId)` → calls `jobProfileApi.deleteEducation(jobProfileId, itemId)`
- `import(jobProfileId)` → calls `jobProfileApi.importEducation(jobProfileId)`

**Dependencies:** None
**Effort:** S / 20 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- Hook manages loading, error, and items state
- CRUD operations update local state optimistically
- Import operation refreshes list after success

---

### Task P2.T2: Build JP Experience Editor (List + Form + Hook)

**Feature:** Job Profile Experience Section Editor  
**Effort:** M / 1–1.5 hours  
**Dependencies:** P2 pattern established by T1  
**Risk Level:** Low — follows same pattern as T1, but experience has more fields.

**Files to create:**
- `frontend/src/features/job-profiles/sections/experience/JPExperienceList.tsx`
- `frontend/src/features/job-profiles/sections/experience/JPExperienceForm.tsx`
- `frontend/src/features/job-profiles/sections/experience/useJPExperience.ts`

**Description:** Replicate the experience editing pattern from user-profile. Display: company (bold), title, "Current" badge, date range, location. Form fields: Company*, Title*, Location, Start/End Date (MonthYearPicker), Context/Description (textarea), Bullet Points.

**Acceptance Criteria:**
- Lists all JP experience entries with company/title/dates
- "Current" badge shown when `is_current` is true
- Inline edit form with all fields
- Delete with confirmation
- Import from user profile button

---

### Task P2.T3: Build JP Projects Editor (List + Form + Hook)

**Feature:** Job Profile Projects Section Editor  
**Effort:** M / 1–1.5 hours  
**Dependencies:** P2 pattern established by T1  
**Risk Level:** Low.

**Files to create:**
- `frontend/src/features/job-profiles/sections/projects/JPProjectList.tsx`
- `frontend/src/features/job-profiles/sections/projects/JPProjectForm.tsx`
- `frontend/src/features/job-profiles/sections/projects/useJPProjects.ts`

**Description:** Replicate the projects editing pattern. Display: title (bold), description (clamped), technologies (tags), date range. Form: Title*, Description, Technologies (one per line), Project URL, Start/End Date (MonthYearPicker).

**Note:** The `jobProfileApi.createProject` / `updateProject` currently sends `technologies` as empty arrays. Fix the mapping to properly send and receive technologies (the backend `job_profile_projects` table has a `technologies` column).

**Fix needed:** Update `mapProject` to read `(row as any).technologies ?? []` and update create/update methods to include `technologies` in the body.

**Acceptance Criteria:**
- Lists projects with title, description, technologies as styled badges
- Technologies are editable (one per line in textarea)
- Create/update sends technologies to backend
- URL field renders as clickable globe icon

---

### Task P2.T4: Build JP Research Editor (List + Form + Hook)

**Feature:** Job Profile Research Section Editor  
**Effort:** M / 1–1.5 hours  
**Dependencies:** P2 pattern  
**Risk Level:** Low.

**Files to create:**
- `frontend/src/features/job-profiles/sections/research/JPResearchList.tsx`
- `frontend/src/features/job-profiles/sections/research/JPResearchForm.tsx`
- `frontend/src/features/job-profiles/sections/research/useJPResearch.ts`

**Description:** Replicate research editing pattern. Display: title (bold), journal (italic) + year. Form: Title*, Journal/Conference, Year (select or number input), Description, URL.

**Fix needed:** `mapResearch` hardcodes `institution`, `journal`, `year` to null. Update to read from backend response: `journal: (row as any).journal ?? null`, `year: (row as any).year ?? null`. Also update `createResearch` / `updateResearch` to send `journal` and `year`.

**Acceptance Criteria:**
- Lists research entries with title/journal/year
- Journal and year fields are saved and loaded correctly
- MonthYearPicker or year input works for year field

---

### Task P2.T5: Build JP Certifications Editor (List + Form + Hook)

**Feature:** Job Profile Certifications Section Editor  
**Effort:** S / 0.5–1 hour  
**Dependencies:** P2 pattern  
**Risk Level:** Low — simplest section.

**Files to create:**
- `frontend/src/features/job-profiles/sections/certifications/JPCertList.tsx`
- `frontend/src/features/job-profiles/sections/certifications/JPCertForm.tsx`
- `frontend/src/features/job-profiles/sections/certifications/useJPCertifications.ts`

**Description:** Replicate certifications pattern. Display: Award icon + name (bold), clickable credential link. Form: Certificate Name*, Verification URL.

**Acceptance Criteria:**
- Lists certifications with name and credential link
- Simple 2-field form
- Import from user profile

---

### Task P2.T6: Build JP Skills Editor (Editor + Hook)

**Feature:** Job Profile Skills Section Editor  
**Effort:** M / 0.5–1 hour  
**Dependencies:** P2 pattern (modified — skills uses flat textarea, not list+form)  
**Risk Level:** Low.

**Files to create:**
- `frontend/src/features/job-profiles/sections/skills/JPSkillsEditor.tsx`
- `frontend/src/features/job-profiles/sections/skills/useJPSkills.ts`

**Description:** Replicate the skills editor pattern. Single textarea (comma/newline separated) for skills. For v1, keep skills as a flat list (the JP API doesn't separate technical/competency).

**Note:** The `jobProfileApi.updateSkills` sends all skills with `kind: 'technical'`. Keep this — skills in JP are a flat list for now.

**Acceptance Criteria:**
- Skills displayed as styled chips/cards
- Textarea for editing, comma/newline separated
- Save button persists via API
- Import from user profile converts technical+competency to flat list

---

### Task P2.T7: Replace JPSectionContent with Section Editors

**Feature:** Wire new editors into JobProfileEditor.tsx
**Effort:** M / 30–45 mins
**Dependencies:** P2.T1 through P2.T6
**Risk Level:** Medium — integration point.

#### Sub-task P2.T7.S1: Replace JPSectionContent with per-section editor components

**Files:** `frontend/src/features/job-profiles/editor/JobProfileEditor.tsx`

**Description:** Replace the `JPSectionContent` component with per-section editor components. For personal, use a custom JP personal form (or keep the read-only view for now since personal is a single record, not a list). For all other sections, use the new List+Form components.

**Implementation Hints:**
- Keep the section tabs and routing the same
- Replace `JPSectionContent` with a router-like switch:
  ```
  {tab === 'education' && <JPEducationList jobProfileId={id} />}
  {tab === 'experience' && <JPExperienceList jobProfileId={id} />}
  ... etc
  ```
- Keep the RenderPanel on the right side
- Remove the "Full section editors available in future release" message
- Keep the Import button integrated into each section's list component

**Dependencies:** P2.T1–T6
**Effort:** S / 20 mins
**Risk Flags:** Ensure backward compatibility — the import flow still works within each section editor. Keep `JPSectionContent.tsx` as fallback (do not delete, just stop using it).
**Acceptance Criteria:**
- Clicking an education tab shows JPEducationList with full CRUD
- Clicking experience tab shows JPExperienceList with full CRUD
- All 6 list sections (education, experience, projects, research, certifications, skills) use the new editors
- Import from User Profile button is available within each section editor
- Personal section shows the updated all-8-fields display from P1.T2.S4
- No "future release" placeholder text visible

---

### Task P2.T8: Add "Is Current" Toggle to Experience Form

**Feature:** Experience "Currently working here" toggle
**Effort:** XS / 15 mins
**Dependencies:** P2.T2 (JP Experience form exists)
**Risk Level:** Low.

**Description:** Add a checkbox "I currently work here" to both user-profile and job-profile experience forms. When checked, it clears the end date and disables the end date picker. This replaces the implicitly-derived `is_current` logic (which only works for null `end_month_year` on read, not write).

**Files:**
- `frontend/src/features/user-profile/sections/experience/ExperienceForm.tsx`
- `frontend/src/features/job-profiles/sections/experience/JPExperienceForm.tsx`

**Implementation Hints:**
- Add state: `isCurrent: boolean` (default: `!initial?.end_date`)
- When toggled on: set `end_date` to empty string, disable MonthYearPicker
- When toggled off: enable MonthYearPicker, user must pick end date
- On save: if isCurrent, send `end_date: null` to backend (for UP) or `end_month_year: null` (for JP)
- Add label: "I currently work here"

**Acceptance Criteria:**
- Checkbox toggles end date field disabled state
- Save with "is current" checked sends null end date
- Save with "is current" unchecked sends the selected date

---

## Phase 3: Verification & Hardening

### Overview
- **Goal:** End-to-end verification of all fixes. Create user profile → create job profile → import data → edit sections → render resume.
- **Entry criteria:** P1 and P2 complete, frontend and backend running.
- **Exit criteria:** Full smoke test passes, test audit log complete.

### Task P3.T1: End-to-End Smoke Test

**Description:** Manual verification flow:
1. Create a user profile with education, experience, projects, certifications, skills (using MonthYearPicker for dates)
2. Create a job profile
3. Import all sections from user profile
4. Edit imported data in each job profile section (verify inline editing works)
5. Save personal details (verify all 8 fields persist)
6. Click "Render Resume" → verify PDF is generated
7. Download PDF
8. Delete an item, re-import (verify undo works)

**Dependencies:** P2.T7
**Effort:** M / 30 mins
**Risk Flags:** None.
**Acceptance Criteria:**
- Full flow works without errors
- All 8 personal fields save and reload correctly
- Resume render succeeds and PDF downloads
- No 404 errors in network tab

### Task P3.T2: Test Audit Log

**Description:** Create a test audit log documenting all changes. See Appendix H for format.

**Files:** `Features-to-develop/ui-and-data-schema-fixes/test-audit-log.md`

**Acceptance Criteria:**
- Log covers all tasks (P1.T1 through P2.T8)
- Each entry has: task id, changed files, commands run, pass/fail, notes

---

## Decisions Locked from Analysis

- **MonthYearPicker approach:** Native `<select>` elements (not a third-party date picker library). This avoids adding `react-datepicker` or similar deps and matches the project's lightweight frontend approach.
- **Job profile editor pattern:** Copy the user-profile section pattern (List + Form + Hook per section) rather than building a generic SectionCrud abstraction. This is faster, avoids abstraction risk, and keeps each section independently maintainable.
- **Skills in job profile:** Keep as flat list (no technical/competency split) since the JP skills table doesn't distinguish `kind`. This is consistent with the current API layer.
- **Experience "Is Current":** Add explicit toggle in both UP and JP forms, rather than continuing to infer from null end date.
- **Resume URL fix:** Change frontend paths (not backend prefix) since the backend prefix `/latex-resume` is intentional and matches the feature folder name.

## New Dependencies

**Frontend:** None. All components are built with existing React + TypeScript + Tailwind stack.

**Backend:** None. No backend changes needed for these fixes.

## File Structure Target

```
frontend/
  src/
    components/
      index.ts                              # + MonthYearPicker export
      MonthYearPicker.tsx                   # NEW — reusable month/year picker
    generated/
      openapi.json                          # UPDATED — regenerated with phone/location/summary
      schema.ts                             # UPDATED — regenerated types
      contracts.ts                          # UPDATED — regenerated contracts
    features/
      user-profile/
        sections/
          education/
            EducationForm.tsx               # UPDATED — MonthYearPicker integration
          experience/
            ExperienceForm.tsx              # UPDATED — MonthYearPicker + Is Current toggle
          projects/
            ProjectForm.tsx                 # UPDATED — MonthYearPicker integration
          research/
            ResearchForm.tsx                # UPDATED — year picker improvement
      job-profiles/
        jobProfileApi.ts                    # UPDATED — fix personal fields + resume URLs + technologies
        editor/
          JobProfileEditor.tsx              # UPDATED — replace JPSectionContent with per-section editors
          JPSectionContent.tsx              # DEPRECATED (kept as fallback)
        sections/                           # NEW directory
          education/
            JPEducationList.tsx             # NEW
            JPEducationForm.tsx             # NEW
            useJPEducation.ts               # NEW
          experience/
            JPExperienceList.tsx            # NEW
            JPExperienceForm.tsx            # NEW
            useJPExperience.ts              # NEW
          projects/
            JPProjectList.tsx               # NEW
            JPProjectForm.tsx               # NEW
            useJPProjects.ts                # NEW
          research/
            JPResearchList.tsx              # NEW
            JPResearchForm.tsx              # NEW
            useJPResearch.ts                # NEW
          certifications/
            JPCertList.tsx                  # NEW
            JPCertForm.tsx                  # NEW
            useJPCertifications.ts          # NEW
          skills/
            JPSkillsEditor.tsx              # NEW
            useJPSkills.ts                  # NEW
Features-to-develop/
  ui-and-data-schema-fixes/
    development-plan.md                     # THIS FILE
    test-audit-log.md                       # NEW — verification results
```

---

## Appendix

### Appendix A - Glossary

| Term | Meaning |
| --- | --- |
| **MonthYearPicker** | Custom React component rendering month + year `<select>` dropdowns, emitting `MM/YYYY` formatted strings. |
| **JP** | Job Profile — a user-created profile variant for job applications. |
| **UP** | User Profile — the master/authoritative profile data. |
| **Section Editor** | Per-section List + Form + Hook pattern providing full CRUD for a profile category. |
| **Is Current** | Toggle indicating a currently-held position (sets end date to null). |
| **OpenAPI spec regeneration** | Re-fetching the `/openapi.json` from the running FastAPI backend to get updated type definitions. |
| **Field name mapping** | Translation between frontend display names (`start_date`, `institution`) and backend API names (`start_month_year`, `university_name`). |

### Appendix B - Full Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| R1 | `openapi-ts` tool fails on regenerated spec | Medium | High | Manually patch `openapi.json` with the 3 missing fields; use `(row as any)` casts in mapper functions as belt-and-suspenders |
| R2 | Section editor duplication leads to maintenance burden | Medium | Medium | Keep user-profile editors as source of truth; job-profile editors are intentionally independent to allow divergence in future phases |
| R3 | MonthYearPicker performance with 100+ year options | Low | Low | Virtualize year dropdown if needed; for MVP, 100 years is negligible DOM size |
| R4 | Import-then-edit-then-reimport data loss | Medium | High | Import is additive-only; duplicate source_ids are skipped. Document that user must delete before re-importing if they want fresh data |
| R5 | Technologies field not sent in JP project create/update | High | Medium | Fix in P2.T3 — update `createProject`/`updateProject` and `mapProject` in `jobProfileApi.ts` |
| R6 | Resume render URL fix might break Polling logic in `useJPLatexRender.ts` | Low | Medium | Check `useJPLatexRender.ts` for hardcoded URLs and fix if present |
| R7 | Generated TypeScript types don't match actual backend responses | Medium | Medium | Use `(response as any).field ?? null` fallback pattern (already established in `profileApi.ts`). Remove casts when types are accurate |

### Appendix C - Assumptions Log

| ID | Assumption | Impact if wrong |
| --- | --- | --- |
| A1 | Backend `/job-profiles/{id}/latex-resume` endpoint is fully functional when called with correct URL | Resume render still fails — need to debug backend |
| A2 | The `technologies` field exists in `job_profile_projects` table and is served by the backend API | Projects API calls fail — need to add column migration |
| A3 | User profile and job profile section forms can be independent (no shared state) | Need to add prop-drilling or context for cross-section refresh |
| A4 | `openapi.json` can be regenerated by hitting a running backend | If backend unavailable, manually patch the JSON file |
| A5 | The existing `jobProfileApi` CRUD methods (create, update, delete) work correctly for all sections | Need backend debugging — out of scope for this plan |
| A6 | Tailwind `inputClass` / `fieldClass` styles are consistent across the project | Minor visual inconsistency — acceptable for MVP |

### Appendix D - Instructions for Coding Agents

1. **Skill-first workflow.** Before any implementation, invoke `using-superpowers` to plan the skill sequence, then invoke applicable skills (`test-driven-development` before writing code, `verification-before-completion` before claiming done).
2. **Dispatch rule.** Phase 1 tasks can run in parallel (3 agents): P1.T1 (MonthYearPicker), P1.T2 (personal details fix), P1.T3 (resume URLs). Phase 2 is sequential per section, but all 6 sections can run in parallel (6 agents).
3. **Copy-paste-adjust pattern.** For section editors, copy the corresponding user-profile section as base, then:
   - Replace `profileApi` with `jobProfileApi`
   - Add `jobProfileId` prop
   - Adjust field names in API payloads
   - Adjust imports to `@features/job-profiles/types`
4. **Graphify-first scoping.** Before substantive edits, query `graphify-out/` for impact radius; after edits, run `python -m graphify update .`.
5. **Targeted testing.** Test only changed files. Run `npm run typecheck` (if available) to catch TypeScript errors.
6. **Frontend verification.** After each section editor is built, verify in browser: (1) list loads, (2) add new works, (3) edit works, (4) delete works, (5) import works.
7. **Secrets hygiene.** Never commit `.env` or API keys.

### Appendix E - Development Order Summary

| Order | Work item | Rationale |
| --- | --- | --- |
| 1 | P1.T3 — Fix resume URLs | One-line fixes, unblocks resume testing |
| 2 | P1.T1 — MonthYearPicker component | Reusable component needed by all forms |
| 3 | P1.T2 — Personal details fix | Unblocks JP personal editing |
| 4 | P1.T1.S2 — Integrate picker into 3 forms | Depends on picker component |
| 5 | P2.T1 — JP Education editor | First section, establishes pattern |
| 6 | P2.T2 — JP Experience editor | Follows pattern, adds is_current |
| 7 | P2.T3 — JP Projects editor | Fixes technologies field |
| 8 | P2.T4 — JP Research editor | Fixes journal/year fields |
| 9 | P2.T5 — JP Certifications editor | Simplest section |
| 10 | P2.T6 — JP Skills editor | Unique pattern (textarea, not list) |
| 11 | P2.T7 — Replace JPSectionContent in JobProfileEditor | Integration of all editors |
| 12 | P2.T8 — Is Current toggle | UX improvement across both profile types |
| 13 | P3.T1 — End-to-end smoke test | Full verification |
| 14 | P3.T2 — Test audit log | Documentation |

**Parallelism:** P1.T1, P1.T2, P1.T3 can all run in parallel. P2.T1 through P2.T6 can all run in parallel once P2 pattern is established. P2.T7 and P2.T8 depend on P2.T1–T6.

### Appendix F - Wave Dispatch Map

**Wave 1 (P1 — 3 agents in parallel):**
- agent-A: P1.T1 (MonthYearPicker + integration)
- agent-B: P1.T2 (personal details fix + regenerate OpenAPI spec)
- agent-C: P1.T3 (resume URL fix)

**Wave 2 (P2 — up to 6 agents in parallel):**
- agent-A: P2.T1 (JP Education editor)
- agent-B: P2.T2 (JP Experience editor)
- agent-C: P2.T3 (JP Projects editor)
- agent-D: P2.T4 (JP Research editor)
- agent-E: P2.T5 (JP Certifications editor)
- agent-F: P2.T6 (JP Skills editor)

**Wave 3 (Integration — 1 agent):**
- agent-A: P2.T7 (replace JPSectionContent) + P2.T8 (Is Current toggle) + P3.T1 (E2E smoke test) + P3.T2 (audit log)

### Appendix G - Coding Instructions and Implementation Quality Bar

1. **Use `using-superpowers` to plan skills before coding.** At task start, invoke `using-superpowers`, decide the skill sequence, then execute in order.
2. **Use Graphify MCP for codebase reading first.** Check `graphify-out/GRAPH_REPORT.md` for god nodes before file reads.
3. **Preserve file structure quality.** New files must match the layout in File Structure Target section. Existing patterns for naming, imports, Tailwind classes must be followed.
4. **Keep imports clean.** Use `@features/...` and `@components/...` path aliases.
5. **No dead code.** Remove placeholder text like "Full section editors available in future release" after editors are built.
6. **Minimal diffs.** When editing existing files, make the smallest change needed. Do not reformat unrelated code.

### Appendix H - Testing Instructions and Test Audit Log Requirements

1. **Mandatory scoped-test rule.** Test only what was developed or changed. Do not run full test suite by default.
2. **When broader tests are allowed.** Only when shared infrastructure changes (MonthYearPicker affects 3 forms → test all 3).
3. **Mandatory test creation for changed behavior.** Every behavior change requires a test or manual verification entry in the audit log.
4. **Mandatory test audit log per change set.** Include: task/change id, changed files, exact verification steps, pass/fail result, notes.

**Audit log template:**

| Field | Required content |
| --- | --- |
| Task / change id | `P1.T1` (example) |
| Changed files / behavior | concise list of changed paths and behavior |
| Verification performed | exact manual steps or test commands |
| Scope type | `new-code`, `changed-code`, or `shared-dependency` |
| Result | pass/fail with short note |
| Why not broader | one-line rationale |

**Critical test cases:**
1. MonthYearPicker: renders with initial value, emits correct MM/YYYY on change, handles null/empty value
2. Personal details: save and reload all 8 fields, verify no data loss
3. Resume: trigger render, verify 200 response, download PDF
4. Section editors: create, read, update, delete, import for each of 6 sections
5. Is Current: toggle sets end date to null, saves correctly

### Appendix I - Multi-Agent and User Review Gates

1. **Functionality gate:** behavior matches this plan, edge cases handled, no regressions.
2. **Code quality gate:** readability, maintainability, error handling meet production expectations.
3. **File structure gate:** paths, module boundaries, naming match section File Structure Target.
4. **Testing gate:** audit log proves relevant verification coverage.
5. **Review readiness gate:** the full smoke test (P3.T1) passes end-to-end.
