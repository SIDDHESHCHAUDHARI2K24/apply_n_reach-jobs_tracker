import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '@core/http/client'
import { useAuth } from '@core/auth/context'

export function SettingsView() {
  const { user, clearUser } = useAuth()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const navigate = useNavigate()

  const logout = useCallback(async () => {
    setIsLoggingOut(true)
    try {
      await apiRequest('/auth/logout', { method: 'POST' })
    } finally {
      clearUser()
      navigate('/auth/login', { replace: true })
      setIsLoggingOut(false)
    }
  }, [navigate, clearUser])

  return (
    <div style={{ maxWidth: 480 }}>
      <h1>Settings</h1>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Account</h2>
        {user && (
          <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem' }}>
            <dt>Email</dt>
            <dd>{user.email}</dd>
            <dt>Member since</dt>
            <dd>{new Date(user.created_at).toLocaleDateString()}</dd>
            <dt>User ID</dt>
            <dd style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{user.id}</dd>
          </dl>
        )}
      </section>

      <section>
        <h2>Session</h2>
        <button onClick={logout} disabled={isLoggingOut} style={{ background: '#dc2626', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: 4, cursor: 'pointer' }}>
          {isLoggingOut ? 'Signing out...' : 'Sign out'}
        </button>
      </section>
    </div>
  )
}
