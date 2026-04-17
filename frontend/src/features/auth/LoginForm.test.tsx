import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { LoginForm } from './LoginForm'
import * as authForms from './useAuthForms'

vi.mock('./useAuthForms', async (importOriginal) => {
  const actual = await importOriginal<typeof authForms>()
  return { ...actual, useLoginForm: vi.fn() }
})

const mockLogin = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  ;(authForms.useLoginForm as ReturnType<typeof vi.fn>).mockReturnValue({
    login: mockLogin,
    isLoading: false,
    error: null,
    success: null,
  })
})

function renderForm() {
  return render(
    <MemoryRouter><LoginForm /></MemoryRouter>
  )
}

describe('LoginForm', () => {
  it('shows validation error when email is empty', () => {
    renderForm()
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(screen.getByRole('alert')).toHaveTextContent('Email is required')
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('shows validation error for invalid email', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'notanemail' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(screen.getByRole('alert')).toHaveTextContent('valid email')
  })

  it('shows validation error when password is too short', () => {
    renderForm()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'short' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(screen.getByRole('alert')).toHaveTextContent('8 characters')
  })

  it('calls login with trimmed email and password when valid', async () => {
    mockLogin.mockResolvedValueOnce(undefined)
    renderForm()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: '  a@b.com  ' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'mypassword' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => expect(mockLogin).toHaveBeenCalledWith({ email: 'a@b.com', password: 'mypassword' }))
  })

  it('displays API error from hook', () => {
    ;(authForms.useLoginForm as ReturnType<typeof vi.fn>).mockReturnValue({
      login: mockLogin, isLoading: false, error: 'Invalid credentials', success: null,
    })
    renderForm()
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials')
  })

  it('disables button while loading', () => {
    ;(authForms.useLoginForm as ReturnType<typeof vi.fn>).mockReturnValue({
      login: mockLogin, isLoading: true, error: null, success: null,
    })
    renderForm()
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
