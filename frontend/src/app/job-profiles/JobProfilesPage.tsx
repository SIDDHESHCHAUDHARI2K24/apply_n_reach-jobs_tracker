import React from 'react'
import { Routes, Route } from 'react-router-dom'

const JobProfilesListPage = React.lazy(() =>
  import('@features/job-profiles/list/JobProfilesListPage').then(m => ({ default: m.JobProfilesListPage }))
)
const JobProfileEditor = React.lazy(() =>
  import('@features/job-profiles/editor/JobProfileEditor').then(m => ({ default: m.JobProfileEditor }))
)

export default function JobProfilesPage() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route index element={<JobProfilesListPage />} />
        <Route path=":jobProfileId/edit" element={<JobProfileEditor />} />
      </Routes>
    </React.Suspense>
  )
}
