import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ProfileShell } from './shell/ProfileShell'
import * as profileApiModule from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/user-profile/profileApi', () => ({
  profileApi: {
    bootstrapProfile: vi.fn(),
    getProfileSummary: vi.fn(),
  },
}))

beforeEach(() => vi.clearAllMocks())

function renderShell(initialEntries = ['/profile/personal']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <ProfileShell />
    </MemoryRouter>
  )
}

describe('ProfileShell', () => {
  it('bootstraps profile on mount', async () => {
    ;(profileApiModule.profileApi.bootstrapProfile as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ id: '1', user_id: 'u1', created_at: '' })
    renderShell()
    await waitFor(() => expect(screen.getByText('Personal')).toBeInTheDocument())
    expect(profileApiModule.profileApi.bootstrapProfile).toHaveBeenCalled()
  })

  it('handles 409 (already exists) gracefully', async () => {
    ;(profileApiModule.profileApi.bootstrapProfile as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new HttpError('Profile already exists', 409))
    renderShell()
    await waitFor(() => expect(screen.getByText('Personal')).toBeInTheDocument())
  })

  it('shows error on bootstrap failure', async () => {
    ;(profileApiModule.profileApi.bootstrapProfile as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new HttpError('Server error', 500))
    renderShell()
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
  })
})
