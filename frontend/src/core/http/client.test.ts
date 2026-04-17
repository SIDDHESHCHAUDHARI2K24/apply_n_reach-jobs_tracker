import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiRequest, HttpError } from './client'

const originalFetch = globalThis.fetch

beforeEach(() => {
  globalThis.fetch = vi.fn()
})

afterEach(() => {
  globalThis.fetch = originalFetch
})

function mockFetch(status: number, body: unknown, ok = status < 400) {
  const jsonBody = JSON.stringify(body)
  ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(jsonBody),
  } as unknown as Response)
}

describe('apiRequest', () => {
  it('returns parsed JSON on success', async () => {
    mockFetch(200, { hello: 'world' })
    const result = await apiRequest<{ hello: string }>('/test')
    expect(result).toEqual({ hello: 'world' })
  })

  it('throws HttpError with detail and code on 401', async () => {
    mockFetch(401, { detail: 'Unauthorized', code: 401 }, false)
    await expect(apiRequest('/secure')).rejects.toThrow(HttpError)
    try {
      mockFetch(401, { detail: 'Unauthorized', code: 401 }, false)
      await apiRequest('/secure')
    } catch (err) {
      expect(err).toBeInstanceOf(HttpError)
      expect((err as HttpError).status).toBe(401)
      expect((err as HttpError).message).toBe('Unauthorized')
    }
  })

  it('throws HttpError on 404', async () => {
    mockFetch(404, { detail: 'Not found' }, false)
    try {
      await apiRequest('/missing')
    } catch (err) {
      expect(err).toBeInstanceOf(HttpError)
      expect((err as HttpError).status).toBe(404)
    }
  })

  it('throws HttpError on 409 conflict', async () => {
    mockFetch(409, { detail: 'Already exists', code: 409 }, false)
    try {
      await apiRequest('/duplicate', { method: 'POST', body: {} })
    } catch (err) {
      expect(err).toBeInstanceOf(HttpError)
      expect((err as HttpError).status).toBe(409)
    }
  })

  it('throws HttpError on 422 validation error', async () => {
    mockFetch(422, { detail: 'Validation error', code: 422 }, false)
    try {
      await apiRequest('/validate', { method: 'POST', body: {} })
    } catch (err) {
      expect(err).toBeInstanceOf(HttpError)
      expect((err as HttpError).status).toBe(422)
    }
  })

  it('returns undefined on 204 No Content', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: () => Promise.reject(new Error('no body')),
    } as unknown as Response)
    const result = await apiRequest('/delete')
    expect(result).toBeUndefined()
  })

  it('sends credentials: include on all requests', async () => {
    mockFetch(200, {})
    await apiRequest('/test')
    const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    expect(call[1].credentials).toBe('include')
  })
})
