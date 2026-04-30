import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SettingsView } from './SettingsView'
import * as authContext from '@core/auth/context'
import * as httpClient from '@core/http/client'

const mockReplace = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: mockReplace }),
}))

vi.mock('@core/auth/context', async (importOriginal) => {
  const actual = await importOriginal<typeof authContext>()
  return { ...actual, useAuth: vi.fn() }
})

vi.mock('@core/http/client', async (importOriginal) => {
  const actual = await importOriginal<typeof httpClient>()
  return { ...actual, apiRequest: vi.fn() }
})

const mockUser = { id: 'u1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }
const mockClearUser = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  mockReplace.mockReset()
  ;(authContext.useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
    user: mockUser, isLoading: false, error: null, refetch: vi.fn(), clearUser: mockClearUser,
  })
  ;(httpClient.apiRequest as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)
})

function renderView() {
  return render(<SettingsView />)
}

describe('SettingsView', () => {
  it('renders user email', () => {
    renderView()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('renders user id', () => {
    renderView()
    expect(screen.getByText('u1')).toBeInTheDocument()
  })

  it('calls logout when sign out button clicked', async () => {
    renderView()
    fireEvent.click(screen.getByRole('button', { name: /sign out/i }))
    await waitFor(() => expect(httpClient.apiRequest).toHaveBeenCalledWith('/auth/logout', { method: 'POST' }))
    expect(mockClearUser).toHaveBeenCalled()
  })

  it('disables sign out button while logging out', async () => {
    // Make apiRequest hang so we can observe the disabled state
    let resolve!: () => void
    ;(httpClient.apiRequest as ReturnType<typeof vi.fn>).mockReturnValue(
      new Promise<void>(r => { resolve = r })
    )
    renderView()
    fireEvent.click(screen.getByRole('button', { name: /sign out/i }))
    await waitFor(() => expect(screen.getByRole('button')).toBeDisabled())
    resolve()
  })
})
