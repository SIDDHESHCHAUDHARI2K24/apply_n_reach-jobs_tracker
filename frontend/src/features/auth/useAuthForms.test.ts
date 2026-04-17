import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'
import * as authContext from '@core/auth/context'
import * as authApiModule from './authApi'

vi.mock('@core/auth/context', async (importOriginal) => {
  const actual = await importOriginal<typeof authContext>()
  return {
    ...actual,
    useAuth: vi.fn(),
  }
})

vi.mock('./authApi', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    reset: vi.fn(),
    me: vi.fn(),
  },
}))

const mockRefetch = vi.fn()
const mockClearUser = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  ;(authContext.useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
    user: null,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
    clearUser: mockClearUser,
  })
})

function wrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(MemoryRouter, { initialEntries: ['/auth/login'] }, children)
}

describe('useLoginForm', () => {
  it('calls authApi.login with credentials', async () => {
    const { useLoginForm } = await import('./useAuthForms')
    ;(authApiModule.authApi.login as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ id: '1', email: 'a@b.com', created_at: '' })
    mockRefetch.mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useLoginForm(), { wrapper })

    await act(async () => {
      await result.current.login({ email: 'a@b.com', password: 'secret123' })
    })

    expect(authApiModule.authApi.login).toHaveBeenCalledWith({ email: 'a@b.com', password: 'secret123' })
    expect(mockRefetch).toHaveBeenCalled()
  })

  it('sets error state on 401', async () => {
    const { useLoginForm } = await import('./useAuthForms')
    const { HttpError } = await import('@core/http/client')
    ;(authApiModule.authApi.login as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new HttpError('Invalid credentials', 401, 401),
    )

    const { result } = renderHook(() => useLoginForm(), { wrapper })

    await act(async () => {
      await result.current.login({ email: 'a@b.com', password: 'wrongpass' })
    })

    expect(result.current.error).toBe('Invalid credentials')
    expect(result.current.isLoading).toBe(false)
  })

  it('surfaces 422 validation error', async () => {
    const { useLoginForm } = await import('./useAuthForms')
    const { HttpError } = await import('@core/http/client')
    ;(authApiModule.authApi.login as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new HttpError('Validation error', 422, 422),
    )

    const { result } = renderHook(() => useLoginForm(), { wrapper })

    await act(async () => {
      await result.current.login({ email: 'a@b.com', password: 'pass1234' })
    })

    expect(result.current.error).toBe('Validation error')
    expect(result.current.isLoading).toBe(false)
  })
})

describe('useRegisterForm', () => {
  it('calls authApi.register on submit', async () => {
    const { useRegisterForm } = await import('./useAuthForms')
    ;(authApiModule.authApi.register as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ id: '1', email: 'new@b.com', created_at: '' })
    mockRefetch.mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useRegisterForm(), { wrapper })

    await act(async () => {
      await result.current.register({ email: 'new@b.com', password: 'newpass12' })
    })

    expect(authApiModule.authApi.register).toHaveBeenCalledWith({ email: 'new@b.com', password: 'newpass12' })
  })

  it('surfaces 409 email-taken error', async () => {
    const { useRegisterForm } = await import('./useAuthForms')
    const { HttpError } = await import('@core/http/client')
    ;(authApiModule.authApi.register as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new HttpError('Email already registered', 409, 409),
    )

    const { result } = renderHook(() => useRegisterForm(), { wrapper })

    await act(async () => {
      await result.current.register({ email: 'dup@b.com', password: 'pass1234' })
    })

    expect(result.current.error).toBe('Email already registered')
  })
})

describe('useLogoutAction', () => {
  it('calls authApi.logout and clears user', async () => {
    const { useLogoutAction } = await import('./useAuthForms')
    ;(authApiModule.authApi.logout as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ message: 'Logged out' })

    const { result } = renderHook(() => useLogoutAction(), { wrapper })

    await act(async () => {
      await result.current.logout()
    })

    expect(authApiModule.authApi.logout).toHaveBeenCalled()
    expect(mockClearUser).toHaveBeenCalled()
  })
})

describe('useResetForm', () => {
  it('sets success state on successful reset', async () => {
    const { useResetForm } = await import('./useAuthForms')
    ;(authApiModule.authApi.reset as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ message: 'Password reset' })

    const { result } = renderHook(() => useResetForm(), { wrapper })

    await act(async () => {
      await result.current.reset({ email: 'a@b.com', new_password: 'newpass12' })
    })

    expect(result.current.success).toBeTruthy()
    expect(result.current.error).toBeNull()
  })

  it('sets error state on 404', async () => {
    const { useResetForm } = await import('./useAuthForms')
    const { HttpError } = await import('@core/http/client')
    ;(authApiModule.authApi.reset as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new HttpError('User not found', 404),
    )

    const { result } = renderHook(() => useResetForm(), { wrapper })

    await act(async () => {
      await result.current.reset({ email: 'notfound@b.com', new_password: 'pass1234' })
    })

    expect(result.current.error).toBe('User not found')
  })
})
