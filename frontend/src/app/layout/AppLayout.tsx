import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@core/auth/context'
import {
  LayoutDashboard,
  BriefcaseBusiness,
  UserCircle,
  Settings,
  Rocket,
  type LucideIcon,
} from 'lucide-react'

interface NavItem {
  to: string
  label: string
  Icon: LucideIcon
}

const NAV_ITEMS: NavItem[] = [
  { to: '/job-tracker', label: 'Job Tracker', Icon: LayoutDashboard },
  { to: '/job-profiles', label: 'Job Profiles', Icon: BriefcaseBusiness },
  { to: '/profile', label: 'Profile', Icon: UserCircle },
  { to: '/settings', label: 'Settings', Icon: Settings },
]

export function AppLayout() {
  const { user } = useAuth()
  const location = useLocation()

  function isActive(to: string): boolean {
    return location.pathname === to || location.pathname.startsWith(to + '/')
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <nav
        aria-label="Main navigation"
        style={{
          width: 'var(--sidebar-width)',
          minWidth: 'var(--sidebar-width)',
          background: 'var(--sidebar-bg)',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: '1.5rem 1.25rem 1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <Rocket size={20} color="#38bdf8" strokeWidth={2.5} />
          <span
            style={{
              fontFamily: 'var(--font-heading)',
              fontWeight: 700,
              fontSize: '1rem',
              color: '#38bdf8',
              letterSpacing: '-0.01em',
            }}
          >
            apply_n_reach
          </span>
        </div>

        {/* Nav links */}
        <ul
          role="list"
          style={{ listStyle: 'none', padding: '0.5rem 0.75rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '2px' }}
        >
          {NAV_ITEMS.map(({ to, label, Icon }) => {
            const active = isActive(to)
            return (
              <li key={to}>
                <Link
                  to={to}
                  aria-current={active ? 'page' : undefined}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.625rem',
                    padding: '0.5rem 0.75rem',
                    borderRadius: '0.375rem',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    fontWeight: active ? 600 : 400,
                    color: active ? 'var(--sidebar-active-text)' : 'var(--sidebar-text)',
                    background: active ? 'var(--sidebar-active-bg)' : 'transparent',
                    borderLeft: active ? '3px solid var(--sidebar-active-border)' : '3px solid transparent',
                    transition: 'background 0.15s, color 0.15s',
                  }}
                >
                  <span style={{ flexShrink: 0 }}><Icon size={18} /></span>
                  {label}
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* User section */}
        {user && (
          <div
            style={{
              padding: '1rem 1.25rem',
              borderTop: '1px solid rgba(148, 163, 184, 0.1)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <UserCircle size={18} color="#94a3b8" />
            <span
              style={{
                fontSize: '0.8125rem',
                color: 'var(--sidebar-text)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                flex: 1,
              }}
              title={user.email}
            >
              {user.email}
            </span>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main
        style={{
          flex: 1,
          background: 'var(--content-bg)',
          padding: '2rem',
          overflow: 'auto',
        }}
      >
        <Outlet />
      </main>
    </div>
  )
}
