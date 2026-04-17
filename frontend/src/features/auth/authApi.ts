import { apiRequest } from '@core/http/client'
import type { LoginRequest, RegisterRequest, ResetRequest, AuthResponse, MessageResponse } from './types'

export const authApi = {
  login: (data: LoginRequest) =>
    apiRequest<AuthResponse>('/auth/login', { method: 'POST', body: data }),

  register: (data: RegisterRequest) =>
    apiRequest<AuthResponse>('/auth/register', { method: 'POST', body: data }),

  logout: () =>
    apiRequest<MessageResponse>('/auth/logout', { method: 'POST' }),

  reset: (data: ResetRequest) =>
    apiRequest<MessageResponse>('/auth/reset', { method: 'POST', body: data }),

  me: () =>
    apiRequest<AuthResponse>('/auth/me'),
}
