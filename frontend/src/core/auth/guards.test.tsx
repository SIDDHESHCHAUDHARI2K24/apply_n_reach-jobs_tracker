import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './guards'
import * as authContext from './context'

vi.mock('./context', async (importOriginal) => {
  const actual = await importOriginal<typeof authContext>()
  return { ...actual, useAuth: vi.fn() }
})

function renderProtected(authState: Partial<ReturnType<typeof authContext.useAuth>>) {
  ;(authContext.useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
    user: null,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    clearUser: vi.fn(),
    ...authState,
  })

  return render(
    <MemoryRouter initialEntries={['/protected']}>
      <Routes>
        <Route
          path="/protected"
          element={<ProtectedRoute><div>Protected Content</div></ProtectedRoute>}
        />
        <Route path="/auth/login" element={<div>Login Page</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('shows loading when auth is loading', () => {
    renderProtected({ isLoading: true })
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('redirects to /auth/login when unauthenticated', () => {
    renderProtected({ user: null, isLoading: false })
    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    renderProtected({
      user: { id: '1', email: 'a@b.com', created_at: '2026-01-01T00:00:00Z' },
      isLoading: false,
    })
    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })
})
