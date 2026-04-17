import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '@core/auth/context'

export function AppLayout() {
  const { user } = useAuth()

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Left sidebar */}
      <nav style={{ width: 220, borderRight: '1px solid #e5e7eb', padding: '1rem' }}>
        <div style={{ fontWeight: 700, marginBottom: '1.5rem' }}>apply_n_reach</div>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          <li style={{ marginBottom: '0.5rem' }}>
            <Link to="/job-profiles">Job Profiles</Link>
          </li>
          <li style={{ marginBottom: '0.5rem' }}>
            <Link to="/job-tracker">Job Tracker</Link>
          </li>
        </ul>
      </nav>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Top bar */}
        <header style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', padding: '0.75rem 1.5rem', borderBottom: '1px solid #e5e7eb' }}>
          {user && (
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <Link to="/profile">User Profile</Link>
              <Link to="/settings">Settings</Link>
              <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>{user.email}</span>
            </div>
          )}
        </header>

        {/* Page content */}
        <main style={{ flex: 1, padding: '1.5rem' }}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
