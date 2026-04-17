import { useParams, Link, Outlet, useLocation } from 'react-router-dom'
import { useOpeningResume } from '@features/opening-resume/useOpeningResume'

const TABS = [
  { label: 'Personal', path: 'personal' },
  { label: 'Education', path: 'education' },
  { label: 'Experience', path: 'experience' },
  { label: 'Projects', path: 'projects' },
  { label: 'Research', path: 'research' },
  { label: 'Certifications', path: 'certifications' },
  { label: 'Skills', path: 'skills' },
]

export function OpeningResumeShell() {
  const { openingId } = useParams<{ openingId: string }>()
  const location = useLocation()
  const { resume, isLoading, isCreating, error, notFound, conflict, createResume } = useOpeningResume(openingId ?? '')

  if (!openingId) return <div>Invalid opening ID</div>
  if (isLoading) return <div>Loading resume...</div>
  if (error) return <div role="alert">Error: {error} <button onClick={() => window.location.reload()}>Retry</button></div>

  if (notFound && !resume) {
    return (
      <div style={{ maxWidth: 480, margin: '2rem auto', padding: '1rem', border: '1px solid #e5e7eb', borderRadius: 8 }}>
        <h2>Resume not created yet</h2>
        <p>
          This resume is an independent snapshot — changes here won&apos;t affect your main profile or job profiles.
        </p>
        <button onClick={() => createResume()} disabled={isCreating}>
          {isCreating ? 'Creating...' : 'Create Resume Snapshot'}
        </button>
        {conflict && <p style={{ color: '#d97706' }}>A resume already exists. Loading it...</p>}
      </div>
    )
  }

  const basePath = `/job-openings/${openingId}/resume`

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h2>Opening Resume</h2>
        <div style={{ fontSize: '0.875rem', color: '#6b7280', background: '#f3f4f6', padding: '0.25rem 0.75rem', borderRadius: 4 }}>
          Snapshot — independent from source profile
        </div>
      </div>

      <nav style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid #e5e7eb', marginBottom: '1.5rem' }}>
        {TABS.map(tab => {
          const tabPath = `${basePath}/${tab.path}`
          const isActive = location.pathname.startsWith(tabPath)
          return (
            <Link
              key={tab.path}
              to={tabPath}
              style={{
                padding: '0.5rem 0',
                fontWeight: isActive ? 700 : 400,
                borderBottom: isActive ? '2px solid #4f46e5' : '2px solid transparent',
                textDecoration: 'none',
              }}
            >
              {tab.label}
            </Link>
          )
        })}
      </nav>

      <Outlet />
    </div>
  )
}
