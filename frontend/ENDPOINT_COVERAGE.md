# Endpoint Coverage Map

Maps which frontend tasks consume which backend endpoints, and which error states are tested.

## Auth (/auth)
| Endpoint | Feature | Hook/API | Error States Tested |
|----------|---------|----------|-------------------|
| POST /auth/login | P2.T1 | authApi.login | 401 (invalid creds), 422 (validation) |
| POST /auth/register | P2.T1 | authApi.register | 409 (email taken), 422 (validation) |
| POST /auth/logout | P2.T1, P5.T2 | authApi.logout | - |
| POST /auth/reset | P2.T1 | authApi.reset | 404 (user not found) |
| GET /auth/me | P1 | AuthContext bootstrap | 401 (unauthenticated) |

## User Profile (/profile)
| Endpoint | Feature | Hook/API | Error States Tested |
|----------|---------|----------|-------------------|
| POST /profile | P2.T2 | profileApi.bootstrapProfile | 409 (already exists — handled as ok) |
| GET /profile/summary | P2.T2 | profileApi.getProfileSummary | - |
| GET/PATCH /profile/personal | P2.T2 | usePersonal | 404 (not found) |
| GET/POST/PATCH/DELETE /profile/education | P2.T2 | useEducation | 500 (server error) |
| GET/POST/PATCH/DELETE /profile/experience | P2.T2 | useExperience | - |
| GET/POST/PATCH/DELETE /profile/projects | P2.T2 | useProjects | - |
| GET/POST/PATCH/DELETE /profile/research | P2.T2 | useResearch | - |
| GET/POST/PATCH/DELETE /profile/certifications | P2.T2 | useCertifications | - |
| GET/PATCH /profile/skills | P2.T2 | useSkills | - |

## Job Profiles (/job-profiles)
| Endpoint | Feature | Hook/API | Error States Tested |
|----------|---------|----------|-------------------|
| GET /job-profiles | P3 | useJobProfiles | 401 |
| POST /job-profiles | P3 | useJobProfiles.create | - |
| DELETE /job-profiles/{id} | P3 | useJobProfiles.remove | - |
| POST /job-profiles/{id}/*/import | P3 | jobProfileApi.import* | - (wiring tested) |
| POST /job-profiles/{id}/resume/render | P3 | useJPLatexRender | 500 (render trigger failure) |
| GET /job-profiles/{id}/resume/metadata | P3 | useJPLatexRender | poll error |
| GET /job-profiles/{id}/resume/pdf | P3 | jobProfileApi.downloadPdf | binary blob verified |

## Job Tracker (/job-openings)
| Endpoint | Feature | Hook/API | Error States Tested |
|----------|---------|----------|-------------------|
| GET /job-openings | P4 | useJobOpenings | - |
| POST /job-openings | P4 | useJobOpenings.create | - |
| PATCH /job-openings/{id} | P4 | useJobOpenings.update | - |
| DELETE /job-openings/{id} | P4 | useJobOpenings.remove | - |
| POST /job-openings/{id}/status | P4 | useJobOpenings.transitionStatus | - |
| GET /job-openings/{id}/status-history | P4 | StatusHistoryDrawer | - |
| POST /extraction/refresh | P4 | useIngestion | 409 (in-flight) |
| GET /extracted-details/latest | P4 | useIngestion | - |
| GET /extraction-runs | P4 | useIngestion | - |

## Opening Resume (/job-openings/{id}/resume)
| Endpoint | Feature | Hook/API | Error States Tested |
|----------|---------|----------|-------------------|
| POST /job-openings/{id}/resume | P5.T1 | useOpeningResume.createResume | 409 (already exists → reload) |
| GET /job-openings/{id}/resume | P5.T1 | useOpeningResume | 404 (not found → show create CTA) |
| GET/PUT /job-openings/{id}/resume/personal | P5.T1 | useORPersonal | - |
| GET/POST/PATCH/DELETE /job-openings/{id}/resume/education | P5.T1 | useOREducation | - |
| GET/POST/PATCH/DELETE /job-openings/{id}/resume/experience | P5.T1 | useORExperience | - |
| GET/POST/PATCH/DELETE /job-openings/{id}/resume/projects | P5.T1 | useORProjects | - |
| GET/POST/PATCH/DELETE /job-openings/{id}/resume/research | P5.T1 | useORResearch | - |
| GET/POST/PATCH/DELETE /job-openings/{id}/resume/certifications | P5.T1 | useORCertifications | - |
| GET/PUT /job-openings/{id}/resume/skills | P5.T1 | useORSkills | - |
