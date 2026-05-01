import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PersonalForm } from './PersonalForm'
import * as profileApiModule from '@features/user-profile/profileApi'

const mockRefresh = vi.fn()
const mockSave = vi.fn()

vi.mock('./usePersonal', () => ({
  usePersonal: () => ({
    data: mockUsePersonalData(),
    isLoading: false,
    isSaving: false,
    error: null,
    save: mockSave,
    refresh: mockRefresh,
  }),
}))

vi.mock('@features/user-profile/profileApi', () => ({
  profileApi: {
    getPersonal: vi.fn(),
    updatePersonal: vi.fn(),
    importFromLinkedIn: vi.fn(),
  },
}))

let _personalData: ReturnType<typeof defaultPersonal> = defaultPersonal()

function defaultPersonal() {
  return {
    id: '1',
    profile_id: 'p1',
    full_name: 'Test User',
    email: 'test@example.com',
    phone: null,
    location: null,
    linkedin_url: null,
    github_url: null,
    portfolio_url: null,
    summary: null,
    created_at: '',
    updated_at: '',
  }
}

function mockUsePersonalData() {
  return _personalData
}

function setPersonalData(overrides: Partial<ReturnType<typeof defaultPersonal>>) {
  _personalData = { ...defaultPersonal(), ...overrides }
}

beforeEach(() => {
  vi.clearAllMocks()
  _personalData = defaultPersonal()
})

describe('PersonalForm — LinkedIn Import', () => {
  it('renders Import from LinkedIn button', () => {
    render(<PersonalForm />)
    expect(screen.getByRole('button', { name: /import from linkedin/i })).toBeInTheDocument()
  })

  it('disables import button while importing', async () => {
    setPersonalData({ linkedin_url: 'https://linkedin.com/in/testuser' })
    let resolveImport: (value: unknown) => void
    const importPromise = new Promise(resolve => { resolveImport = resolve })
    ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
      .mockImplementation(() => importPromise)

    render(<PersonalForm />)
    const btn = screen.getByRole('button', { name: /import from linkedin/i })

    // Click without awaiting so we can check intermediate state
    const clickPromise = userEvent.click(btn)

    // After React processes the synchronous state updates from the click handler
    await waitFor(() => {
      expect(btn).toBeDisabled()
      expect(screen.getByText('Importing...')).toBeInTheDocument()
    })

    // Cleanup: resolve to allow the test to complete cleanly
    resolveImport!({ message: 'ok', sections_imported: {} })
    await clickPromise
  })

  describe('saved URL path (linkedin_url present)', () => {
    beforeEach(() => {
      setPersonalData({ linkedin_url: 'https://linkedin.com/in/testuser' })
    })

    it('calls importFromLinkedIn with saved URL', async () => {
      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({ message: 'ok', sections_imported: { personal: 1 } })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      expect(profileApiModule.profileApi.importFromLinkedIn).toHaveBeenCalledWith(
        'https://linkedin.com/in/testuser'
      )
    })

    it('refreshes profile data after successful import', async () => {
      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({ message: 'ok', sections_imported: { personal: 1, education: 2 } })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(mockRefresh).toHaveBeenCalled()
      })
    })

    it('shows import summary after success', async () => {
      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({ message: 'ok', sections_imported: { personal: 1, education: 2 } })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.getByText(/Imported sections/i)).toBeInTheDocument()
      })
    })
  })

  describe('fallback URL prompt path (no linkedin_url)', () => {
    it('prompts user for URL when linkedin_url is missing', async () => {
      const promptSpy = vi.fn().mockReturnValue('https://linkedin.com/in/entered')
      const originalPrompt = window.prompt
      window.prompt = promptSpy

      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({ message: 'ok', sections_imported: {} })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      expect(promptSpy).toHaveBeenCalledWith('Enter your LinkedIn profile URL')
      expect(profileApiModule.profileApi.importFromLinkedIn).toHaveBeenCalledWith(
        'https://linkedin.com/in/entered'
      )

      window.prompt = originalPrompt
    })

    it('does nothing when user cancels the prompt', async () => {
      const promptSpy = vi.fn().mockReturnValue(null)
      const originalPrompt = window.prompt
      window.prompt = promptSpy

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      expect(promptSpy).toHaveBeenCalled()
      expect(profileApiModule.profileApi.importFromLinkedIn).not.toHaveBeenCalled()

      window.prompt = originalPrompt
    })
  })

  describe('invalid URL', () => {
    it('shows error for non-LinkedIn URL', async () => {
      setPersonalData({ linkedin_url: 'https://google.com/profile' })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid LinkedIn URL.')).toBeInTheDocument()
      })
      expect(profileApiModule.profileApi.importFromLinkedIn).not.toHaveBeenCalled()
    })

    it('shows error for invalid URL format', async () => {
      const promptSpy = vi.fn().mockReturnValue('not-a-url')
      const originalPrompt = window.prompt
      window.prompt = promptSpy

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid LinkedIn URL.')).toBeInTheDocument()
      })
      expect(profileApiModule.profileApi.importFromLinkedIn).not.toHaveBeenCalled()

      window.prompt = originalPrompt
    })
  })

  describe('API error handling', () => {
    it('shows error message with status code on API failure', async () => {
      setPersonalData({ linkedin_url: 'https://linkedin.com/in/testuser' })
      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockRejectedValueOnce({ status: 503, message: 'Token missing' })

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.getByText(/Import failed \(503\): Token missing/)).toBeInTheDocument()
      })
    })

    it('displays error without status prefix when error has no status', async () => {
      setPersonalData({ linkedin_url: 'https://linkedin.com/in/testuser' })
      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockRejectedValueOnce(new Error('Network failure'))

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.getByText('Import failed: Network failure')).toBeInTheDocument()
      })
    })

    it('clears error on subsequent successful import', async () => {
      setPersonalData({ linkedin_url: 'https://linkedin.com/in/testuser' })

      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockRejectedValueOnce(new Error('First fail'))

      render(<PersonalForm />)

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))
      await waitFor(() => {
        expect(screen.getByText('Import failed: First fail')).toBeInTheDocument()
      })

      ;(profileApiModule.profileApi.importFromLinkedIn as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({ message: 'ok', sections_imported: { personal: 1 } })

      await userEvent.click(screen.getByRole('button', { name: /import from linkedin/i }))

      await waitFor(() => {
        expect(screen.queryByText('Import failed: First fail')).not.toBeInTheDocument()
      })
    })
  })
})
