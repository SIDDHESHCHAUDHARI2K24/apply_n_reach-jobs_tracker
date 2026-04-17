import { API_BASE_URL } from '@core/config/env'

export interface ApiError {
  message: string
  code?: number
  status: number
}

export class HttpError extends Error {
  readonly code?: number
  readonly status: number

  constructor(message: string, status: number, code?: number) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.code = code
  }
}

async function parseError(response: Response): Promise<HttpError> {
  let message = `HTTP ${response.status}`
  let code: number | undefined

  try {
    const body = await response.json()
    if (typeof body.detail === 'string') message = body.detail
    if (typeof body.code === 'number') code = body.code
  } catch {
    // non-JSON error body — use status text
  }

  return new HttpError(message, response.status, code)
}

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, signal } = options

  const init: RequestInit = {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    signal,
  }

  if (body !== undefined) {
    init.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, init)

  if (!response.ok) {
    throw await parseError(response)
  }

  // 204 No Content — use apiRequest<void>(...) or apiRequest<null>(...) for endpoints that return no body
  if (response.status === 204) {
    return undefined as unknown as T
  }

  return response.json() as Promise<T>
}

export async function apiRequestBlob(path: string, options: RequestOptions = {}): Promise<Blob> {
  const { method = 'GET', body, headers = {}, signal } = options

  const init: RequestInit = {
    method,
    credentials: 'include',
    headers: { ...headers },
    signal,
  }

  if (body !== undefined) {
    init.headers = { 'Content-Type': 'application/json', ...headers }
    init.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, init)

  if (!response.ok) {
    throw await parseError(response)
  }

  return response.blob()
}
