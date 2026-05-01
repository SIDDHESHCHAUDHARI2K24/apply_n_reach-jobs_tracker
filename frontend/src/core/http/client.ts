import { API_BASE_URL } from '@core/config/env'

export interface ApiError {
  message: string
  code?: number | string
  status: number
}

export class HttpError extends Error {
  readonly code?: number | string
  readonly status: number

  constructor(message: string, status: number, code?: number | string) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.code = code
  }
}

async function parseError(response: Response): Promise<HttpError> {
  let message = `HTTP ${response.status}`
  let code: number | string | undefined

  try {
    const body = await response.json() as { detail?: unknown; code?: unknown; message?: unknown }

    if (typeof body.code === 'number' || typeof body.code === 'string') {
      code = body.code
    }

    if (typeof body.detail === 'string') {
      message = body.detail
    } else if (Array.isArray(body.detail) && body.detail.length > 0) {
      // FastAPI validation errors usually provide a list of issues.
      const first = body.detail[0] as Record<string, unknown>
      if (typeof first?.msg === 'string') {
        const loc = Array.isArray(first?.loc)
          ? first.loc.map(segment => String(segment)).join('.')
          : undefined
        message = loc ? `${loc}: ${first.msg}` : first.msg
      } else {
        message = 'Validation failed'
      }
    } else if (body.detail && typeof body.detail === 'object') {
      const detailObj = body.detail as Record<string, unknown>
      if (typeof detailObj.message === 'string') {
        message = detailObj.message
      } else {
        message = JSON.stringify(body.detail)
      }
      if (typeof detailObj.error_code === 'string') {
        code = detailObj.error_code
      }
    } else if (typeof body.message === 'string') {
      message = body.message
    }
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
