'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { HttpError } from '@core/http/client'
import { useAuth } from '@core/auth/context'
import { authApi } from './authApi'
import type { LoginRequest, RegisterRequest, ResetRequest } from './types'

interface FormState {
  isLoading: boolean
  error: string | null
  success: string | null
}

const initial: FormState = { isLoading: false, error: null, success: null }

export function useLoginForm() {
  const [state, setState] = useState<FormState>(initial)
  const router = useRouter()
  const { refetch } = useAuth()

  const login = useCallback(async (data: LoginRequest) => {
    setState({ isLoading: true, error: null, success: null })
    try {
      await authApi.login(data)
      await refetch()
      const returnTo = typeof window !== 'undefined'
        ? new URLSearchParams(window.location.search).get('returnTo') ?? '/job-profiles'
        : '/job-profiles'
      router.replace(returnTo)
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Login failed'
      setState({ isLoading: false, error: message, success: null })
      return
    }
    setState(initial)
  }, [router, refetch])

  return { ...state, login }
}

export function useRegisterForm() {
  const [state, setState] = useState<FormState>(initial)
  const router = useRouter()
  const { refetch } = useAuth()

  const register = useCallback(async (data: RegisterRequest) => {
    setState({ isLoading: true, error: null, success: null })
    try {
      await authApi.register(data)
      await refetch()
      router.replace('/job-profiles')
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Registration failed'
      setState({ isLoading: false, error: message, success: null })
      return
    }
    setState(initial)
  }, [router, refetch])

  return { ...state, register }
}

export function useLogoutAction() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { clearUser } = useAuth()

  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      await authApi.logout()
    } finally {
      clearUser()
      router.replace('/auth/login')
      setIsLoading(false)
    }
  }, [router, clearUser])

  return { isLoading, logout }
}

export function useResetForm() {
  const [state, setState] = useState<FormState>(initial)

  const reset = useCallback(async (data: ResetRequest) => {
    setState({ isLoading: true, error: null, success: null })
    try {
      await authApi.reset(data)
      setState({ isLoading: false, error: null, success: 'Password reset successfully. You can now log in.' })
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Reset failed'
      setState({ isLoading: false, error: message, success: null })
    }
  }, [])

  return { ...state, reset }
}
