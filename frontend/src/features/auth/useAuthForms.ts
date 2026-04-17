import { useState, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
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
  const navigate = useNavigate()
  const location = useLocation()
  const { refetch } = useAuth()

  const login = useCallback(async (data: LoginRequest) => {
    setState({ isLoading: true, error: null, success: null })
    try {
      await authApi.login(data)
      await refetch()
      const returnTo = (location.state as { returnTo?: string } | null)?.returnTo ?? '/job-profiles'
      navigate(returnTo, { replace: true })
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Login failed'
      setState({ isLoading: false, error: message, success: null })
      return
    }
    setState(initial)
  }, [navigate, location.state, refetch])

  return { ...state, login }
}

export function useRegisterForm() {
  const [state, setState] = useState<FormState>(initial)
  const navigate = useNavigate()
  const { refetch } = useAuth()

  const register = useCallback(async (data: RegisterRequest) => {
    setState({ isLoading: true, error: null, success: null })
    try {
      await authApi.register(data)
      await refetch()
      navigate('/job-profiles', { replace: true })
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Registration failed'
      setState({ isLoading: false, error: message, success: null })
      return
    }
    setState(initial)
  }, [navigate, refetch])

  return { ...state, register }
}

export function useLogoutAction() {
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { clearUser } = useAuth()

  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      await authApi.logout()
    } finally {
      clearUser()
      navigate('/auth/login', { replace: true })
      setIsLoading(false)
    }
  }, [navigate, clearUser])

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
