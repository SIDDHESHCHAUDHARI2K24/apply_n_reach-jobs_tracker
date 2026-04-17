import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from '@core/auth/guards'
import { OpeningResumeShell } from '@features/opening-resume/shell/OpeningResumeShell'

const PersonalPage = React.lazy(() => import('./sections/PersonalPage'))
const EducationPage = React.lazy(() => import('./sections/EducationPage'))
const ExperiencePage = React.lazy(() => import('./sections/ExperiencePage'))
const ProjectsPage = React.lazy(() => import('./sections/ProjectsPage'))
const ResearchPage = React.lazy(() => import('./sections/ResearchPage'))
const CertificationsPage = React.lazy(() => import('./sections/CertificationsPage'))
const SkillsPage = React.lazy(() => import('./sections/SkillsPage'))

export default function OpeningResumePage() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <ProtectedRoute>
        <Routes>
          <Route element={<OpeningResumeShell />}>
            <Route index element={<Navigate to="personal" replace />} />
            <Route path="personal" element={<PersonalPage />} />
            <Route path="education" element={<EducationPage />} />
            <Route path="experience" element={<ExperiencePage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="certifications" element={<CertificationsPage />} />
            <Route path="skills" element={<SkillsPage />} />
          </Route>
        </Routes>
      </ProtectedRoute>
    </React.Suspense>
  )
}
