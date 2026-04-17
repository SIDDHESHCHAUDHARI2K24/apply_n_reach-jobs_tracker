import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as orApiModule from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/opening-resume/openingResumeApi', () => ({
  openingResumeApi: {
    get: vi.fn(),
    create: vi.fn(),
  },
}))

const mockApi = orApiModule.openingResumeApi as unknown as {
  get: ReturnType<typeof vi.fn>
  create: ReturnType<typeof vi.fn>
}

const resume = { id: 'r1', job_opening_id: 'o1', source_job_profile_id: 'jp1', created_at: '', updated_at: '' }

beforeEach(() => vi.clearAllMocks())

describe('useOpeningResume', () => {
  it('loads existing resume on mount', async () => {
    mockApi.get.mockResolvedValueOnce(resume)
    const { useOpeningResume } = await import('./useOpeningResume')
    const { result } = renderHook(() => useOpeningResume('o1'))
    await act(async () => {})
    expect(result.current.resume).toEqual(resume)
    expect(result.current.notFound).toBe(false)
  })

  it('sets notFound when resume does not exist', async () => {
    mockApi.get.mockRejectedValueOnce(new HttpError('Not found', 404))
    const { useOpeningResume } = await import('./useOpeningResume')
    const { result } = renderHook(() => useOpeningResume('o1'))
    await act(async () => {})
    expect(result.current.notFound).toBe(true)
    expect(result.current.resume).toBeNull()
  })

  it('creates resume and clears notFound', async () => {
    mockApi.get.mockRejectedValueOnce(new HttpError('Not found', 404))
    mockApi.create.mockResolvedValueOnce(resume)
    const { useOpeningResume } = await import('./useOpeningResume')
    const { result } = renderHook(() => useOpeningResume('o1'))
    await act(async () => {})
    expect(result.current.notFound).toBe(true)
    await act(async () => { await result.current.createResume('jp1') })
    expect(result.current.resume).toEqual(resume)
    expect(result.current.notFound).toBe(false)
  })

  it('handles 409 conflict on create — reloads existing resume', async () => {
    mockApi.get
      .mockRejectedValueOnce(new HttpError('Not found', 404))
      .mockResolvedValueOnce(resume)
    mockApi.create.mockRejectedValueOnce(new HttpError('Resume already exists', 409))
    const { useOpeningResume } = await import('./useOpeningResume')
    const { result } = renderHook(() => useOpeningResume('o1'))
    await act(async () => {})
    await act(async () => { await result.current.createResume() })
    // After 409, it calls loadResume() which fetches the existing resume
    expect(result.current.resume).toEqual(resume)
    expect(result.current.conflict).toBe(true)
  })
})
