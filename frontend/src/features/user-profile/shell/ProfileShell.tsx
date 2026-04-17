import { useEffect, useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'

const TABS = [
  { label: 'Personal', path: '/profile/personal' },
  { label: 'Education', path: '/profile/education' },
  { label: 'Experience', path: '/profile/experience' },
  { label: 'Projects', path: '/profile/projects' },
  { label: 'Research', path: '/profile/research' },
  { label: 'Certifications', path: '/profile/certifications' },
  { label: 'Skills', path: '/profile/skills' },
]

export function ProfileShell() {
  const [isBootstrapping, setIsBootstrapping] = useState(true)
  const [bootstrapError, setBootstrapError] = useState<string | null>(null)
  const location = useLocation()

  useEffect(() => {
    let cancelled = false
    async function bootstrap() {
      try {
        await profileApi.bootstrapProfile()
      } catch (err) {
        if (err instanceof HttpError && err.status === 409) {
          // Already exists — fine
        } else if (!cancelled) {
          setBootstrapError(err instanceof Error ? err.message : 'Failed to initialize profile')
        }
      } finally {
        if (!cancelled) setIsBootstrapping(false)
      }
    }
    bootstrap()
    return () => { cancelled = true }
  }, [])

  if (isBootstrapping) return <div>Loading profile...</div>
  if (bootstrapError) return (
    <div role="alert">
      Error: {bootstrapError}{' '}
      <button onClick={() => window.location.reload()}>Retry</button>
    </div>
  )

  return (
    <div>
      <h1>User Profile</h1>
      <nav style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid #e5e7eb', marginBottom: '1.5rem' }}>
        {TABS.map(tab => (
          <Link
            key={tab.path}
            to={tab.path}
            style={{
              padding: '0.5rem 0',
              fontWeight: location.pathname.startsWith(tab.path) ? 700 : 400,
              borderBottom: location.pathname.startsWith(tab.path) ? '2px solid #4f46e5' : '2px solid transparent',
              textDecoration: 'none',
            }}
          >
            {tab.label}
          </Link>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
