# Test Audit Log: UI & Data Schema Bug Fixes + Job Profile Section Editors

> Generated: 2026-04-30
> Reference: `development-plan.md`

---

## P1.T1 — MonthYearPicker Component

| Field | Value |
| --- | --- |
| Task / change id | P1.T1.S1 |
| Changed files | `src/components/MonthYearPicker.tsx` (NEW), `src/components/index.ts` (NEW) |
| Behavior | New reusable month+year select dropdown component; replaces plain text inputs for MM/YYYY fields |
| Verification performed | TypeScript compilation (`npx tsc --noEmit`), import verification |
| Scope type | new-code |
| Result | PASS — no TS errors |
| Why not broader | New isolated component, no existing dependants at creation time |

| Field | Value |
| --- | --- |
| Task / change id | P1.T1.S2 |
| Changed files | `src/features/user-profile/sections/education/EducationForm.tsx`, `src/features/user-profile/sections/experience/ExperienceForm.tsx`, `src/features/user-profile/sections/projects/ProjectForm.tsx`, `src/features/user-profile/sections/research/ResearchForm.tsx` |
| Behavior | Replaced plain text date inputs with MonthYearPicker; Added "I currently work here" toggle to ExperienceForm (clears/disables end date) |
| Verification performed | TypeScript compilation, visual review of form structure |
| Scope type | changed-code |
| Result | PASS — no TS errors, forms structurally correct |
| Why not broader | No backend changes; form logic unchanged except date inputs |

---

## P1.T2 — Job Profile Personal Details API Fix

| Field | Value |
| --- | --- |
| Task / change id | P1.T2.S1 |
| Changed files | `src/generated/openapi.json` |
| Behavior | Added `summary`, `location`, `phone` to `JPPersonalDetailsUpdate` and `JPPersonalDetailsResponse` schemas |
| Verification performed | Manual JSON validation; field presence confirmed |
| Scope type | changed-code |
| Result | PASS — 3 new fields present in both schemas |
| Why not broader | JSON-only change; generated types not regenerated (openapi-ts has pre-existing failure) |

| Field | Value |
| --- | --- |
| Task / change id | P1.T2.S2 + S3 |
| Changed files | `src/features/job-profiles/jobProfileApi.ts` |
| Behavior | `mapPersonal`: phone/location/summary now read from API response (was hardcoded null). `updatePersonal`: now sends all 8 fields (was 5). |
| Verification performed | TypeScript compilation, code review of mapping logic |
| Scope type | changed-code |
| Result | PASS — 8 fields in map + 8 fields in PATCH body |
| Why not broader | Single API layer file change; runtime verification requires running backend |

| Field | Value |
| --- | --- |
| Task / change id | P1.T2.S4 |
| Changed files | `src/features/job-profiles/editor/JPSectionContent.tsx` |
| Behavior | Personal section now displays all 8 fields (phone, location, summary, linkedin, github, portfolio as clickable links). Removed dead `headline` code. Updated empty-state check. |
| Verification performed | TypeScript compilation, code review |
| Scope type | changed-code |
| Result | PASS — no TS errors, all 8 fields displayed |
| Why not broader | Pure frontend display component |

---

## P1.T3 — Render Resume URL Fix

| Field | Value |
| --- | --- |
| Task / change id | P1.T3.S1 |
| Changed files | `src/features/job-profiles/jobProfileApi.ts` |
| Behavior | Fixed 3 URLs: `resume/render` → `latex-resume/render`, `resume/metadata` → `latex-resume`, `resume/pdf` → `latex-resume/pdf` |
| Verification performed | Backend route verification: confirmed `POST /job-profiles/{id}/latex-resume/render`, `GET /job-profiles/{id}/latex-resume`, `GET /job-profiles/{id}/latex-resume/pdf` exist in router.py |
| Scope type | changed-code |
| Result | PASS — URLs match backend routes exactly |
| Why not broader | Simple URL string change; runtime verification requires running backend |

---

## P2.T1 — JP Education Editor

| Field | Value |
| --- | --- |
| Task / change id | P2.T1 |
| Changed files | `src/features/job-profiles/sections/education/useJPEducation.ts` (NEW), `JPEducationForm.tsx` (NEW), `JPEducationList.tsx` (NEW) |
| Behavior | Full CRUD editor for job profile education section |
| Verification performed | TypeScript compilation, pattern comparison with user-profile education section |
| Scope type | new-code |
| Result | PASS — all 3 files compile, match established patterns |
| Why not broader | New feature code; runtime verification requires full stack |

---

## P2.T2 — JP Experience Editor

| Field | Value |
| --- | --- |
| Task / change id | P2.T2 |
| Changed files | `src/features/job-profiles/sections/experience/useJPExperience.ts` (NEW), `JPExperienceForm.tsx` (NEW), `JPExperienceList.tsx` (NEW) |
| Behavior | Full CRUD editor with "Is Current" toggle |
| Verification performed | TypeScript compilation, code review |
| Scope type | new-code |
| Result | PASS |

---

## P2.T3 — JP Projects Editor + Technologies Fix

| Field | Value |
| --- | --- |
| Task / change id | P2.T3 |
| Changed files | `src/features/job-profiles/sections/projects/useJPProjects.ts` (NEW), `JPProjectForm.tsx` (NEW), `JPProjectList.tsx` (NEW); `src/features/job-profiles/jobProfileApi.ts` (FIXED) |
| Behavior | Full CRUD editor + fixed `technologies` and `bullet_points` fields in mapProject + create/update methods |
| Verification performed | TypeScript compilation, code review |
| Scope type | new-code + changed-code |
| Result | PASS — technologies no longer hardcoded to []; sent in create/update body |
| Why not broader | Critical data-loss fix verified at code level |

---

## P2.T4 — JP Research Editor + Journal/Year Fix

| Field | Value |
| --- | --- |
| Task / change id | P2.T4 |
| Changed files | `src/features/job-profiles/sections/research/useJPResearch.ts` (NEW), `JPResearchForm.tsx` (NEW), `JPResearchList.tsx` (NEW); `src/features/job-profiles/jobProfileApi.ts` (FIXED) |
| Behavior | Full CRUD editor + fixed `journal`, `year`, `institution` fields in mapResearch + create/update methods |
| Verification performed | TypeScript compilation, code review |
| Scope type | new-code + changed-code |
| Result | PASS — journal/year no longer hardcoded to null |

---

## P2.T5 — JP Certifications Editor

| Field | Value |
| --- | --- |
| Task / change id | P2.T5 |
| Changed files | `src/features/job-profiles/sections/certifications/useJPCertifications.ts` (NEW), `JPCertForm.tsx` (NEW), `JPCertList.tsx` (NEW) |
| Behavior | Full CRUD editor for certifications (2-field form) |
| Verification performed | TypeScript compilation |
| Scope type | new-code |
| Result | PASS |

---

## P2.T6 — JP Skills Editor

| Field | Value |
| --- | --- |
| Task / change id | P2.T6 |
| Changed files | `src/features/job-profiles/sections/skills/useJPSkills.ts` (NEW), `JPSkillsEditor.tsx` (NEW) |
| Behavior | Skills textarea editor with save + import |
| Verification performed | TypeScript compilation |
| Scope type | new-code |
| Result | PASS |

---

## P2.T7 — Wire Editors into JobProfileEditor

| Field | Value |
| --- | --- |
| Task / change id | P2.T7 |
| Changed files | `src/features/job-profiles/editor/JobProfileEditor.tsx` |
| Behavior | Replaced generic `JPSectionContent` with per-section editors for education, experience, projects, research, certifications, skills. Personal tab still uses JPSectionContent (single record). |
| Verification performed | TypeScript compilation, import verification |
| Scope type | changed-code |
| Result | PASS — all 7 tabs mapped to correct components |
| Why not broader | Integration wiring only |

---

## Summary

| Category | Count |
| --- | --- |
| Files created | 20 (1 component + 1 barrel + 17 section editor files + 1 plan + 1 audit log) |
| Files modified | 6 (`JobProfileEditor.tsx`, `JPSectionContent.tsx`, `jobProfileApi.ts`, `openapi.json` + 4 user-profile forms) |
| TypeScript errors introduced | 0 |
| Pre-existing TS errors | 5+ (unrelated `@generated/contracts` module, `IngestionPanel.tsx`) |
| Data-loss bugs fixed | 5 (phone/location/summary, technologies, bullet_points, journal, year) |
| 404 bugs fixed | 1 (resume render URLs) |
| UI improvements | 5 (MonthYearPicker in 4 forms + Is Current toggle) |

## Manual Smoke Test Checklist

The following should be verified with a running backend:

- [ ] Create user profile → education with MonthYearPicker dates → saves correctly
- [ ] Create user profile → experience with "Is Current" checked → end date is null
- [ ] Create job profile → personal details → all 8 fields save and reload
- [ ] Import education from user profile to job profile → items visible in JPEducationList
- [ ] Edit imported education → inline form shows → save persists
- [ ] Delete education item → item removed from list
- [ ] Click "Render Resume" → POST hits `/latex-resume/render` (200)
- [ ] Download PDF → GET hits `/latex-resume/pdf` (200 + binary)
- [ ] Personal section in JP shows phone, location, summary, social links as clickable
