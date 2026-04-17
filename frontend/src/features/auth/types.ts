export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface ResetRequest {
  email: string
  new_password: string
}

export interface AuthResponse {
  id: string
  email: string
  created_at: string
}

export interface MessageResponse {
  message: string
}
