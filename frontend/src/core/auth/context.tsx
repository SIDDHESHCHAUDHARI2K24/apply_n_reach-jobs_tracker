import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { apiRequest, HttpError } from '@core/http/client'

export interface AuthUser {
  id: string
  email: string
  created_at: string
}

interface AuthState {
  user: AuthUser | null
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
  clearUser: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMe = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await apiRequest<AuthUser>('/auth/me')
      setUser(data)
    } catch (err) {
      if (err instanceof HttpError && err.status === 401) {
        setUser(null)
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load user')
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearUser = useCallback(() => {
    setUser(null)
  }, [])

  useEffect(() => {
    fetchMe()
  }, [fetchMe])

  return (
    <AuthContext.Provider value={{ user, isLoading, error, refetch: fetchMe, clearUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
