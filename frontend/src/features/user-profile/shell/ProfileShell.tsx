import { useEffect, useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'
import { User, GraduationCap, Briefcase, FolderKanban, FlaskConical, Award, Zap } from 'lucide-react'

const TABS = [
  { label: 'Personal', path: '/profile/personal', icon: User },
  { label: 'Education', path: '/profile/education', icon: GraduationCap },
  { label: 'Experience', path: '/profile/experience', icon: Briefcase },
  { label: 'Projects', path: '/profile/projects', icon: FolderKanban },
  { label: 'Research', path: '/profile/research', icon: FlaskConical },
  { label: 'Certifications', path: '/profile/certifications', icon: Award },
  { label: 'Skills', path: '/profile/skills', icon: Zap },
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

  if (isBootstrapping) return (
    <div className="flex items-center justify-center py-16 text-slate-500 text-sm">
      Loading profile...
    </div>
  )

  if (bootstrapError) return (
    <div role="alert" className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      <span>Error: {bootstrapError}</span>
      <button
        onClick={() => window.location.reload()}
        className="ml-2 underline hover:no-underline"
      >
        Retry
      </button>
    </div>
  )

  return (
    <div className="flex gap-6">
      <nav className="w-48 shrink-0">
        <ul className="space-y-1">
          {TABS.map(tab => {
            const isActive = location.pathname.startsWith(tab.path)
            const Icon = tab.icon
            return (
              <li key={tab.path}>
                <Link
                  to={tab.path}
                  className={[
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors border-l-2',
                    isActive
                      ? 'bg-sky-50 text-sky-600 border-sky-500'
                      : 'text-slate-600 hover:bg-slate-50 border-transparent',
                  ].join(' ')}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {tab.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
      <div className="flex-1 min-w-0">
        <Outlet />
      </div>
    </div>
  )
}
