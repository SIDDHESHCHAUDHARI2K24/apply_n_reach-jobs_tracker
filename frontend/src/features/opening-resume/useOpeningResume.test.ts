import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as orApiModule from '@features/opening-resume/openingResumeApi'
import * as jpApiModule from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/opening-resume/openingResumeApi', () => ({
  openingResumeApi: {
    get: vi.fn(),
    create: vi.fn(),
  },
}))

vi.mock('@features/job-profiles/jobProfileApi', () => ({
  jobProfileApi: {
    list: vi.fn(),
  },
}))

const mockApi = orApiModule.openingResumeApi as unknown as {
  get: ReturnType<typeof vi.fn>
  create: ReturnType<typeof vi.fn>
}

const mockJpApi = jpApiModule.jobProfileApi as unknown as {
  list: ReturnType<typeof vi.fn>
}

const resume = { id: 'r1', job_opening_id: 'o1', source_job_profile_id: 'jp1', created_at: '', updated_at: '' }

beforeEach(() => {
  vi.clearAllMocks()
  mockJpApi.list.mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 })
})

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

  describe('job profile template selector', () => {
    const profilesPage = {
      items: [
        { id: 'jp1', user_id: 'u1', title: 'Software Engineer', status: 'active' as const, created_at: '', updated_at: '' },
        { id: 'jp2', user_id: 'u1', title: 'Data Scientist', status: 'active' as const, created_at: '', updated_at: '' },
      ],
      total: 2,
      limit: 50,
      offset: 0,
    }

    it('loads job profiles when resume does not exist', async () => {
      mockApi.get.mockRejectedValueOnce(new HttpError('Not found', 404))
      mockJpApi.list.mockResolvedValueOnce(profilesPage)
      const { useOpeningResume } = await import('./useOpeningResume')
      const { result } = renderHook(() => useOpeningResume('o1'))
      await act(async () => {})
      expect(result.current.notFound).toBe(true)
      expect(result.current.jobProfiles).toEqual(profilesPage.items)
      expect(mockJpApi.list).toHaveBeenCalledWith({ limit: 50 })
    })

    it('does not fetch profiles when resume exists', async () => {
      mockApi.get.mockResolvedValueOnce(resume)
      const { useOpeningResume } = await import('./useOpeningResume')
      const { result } = renderHook(() => useOpeningResume('o1'))
      await act(async () => {})
      expect(result.current.resume).toEqual(resume)
      expect(mockJpApi.list).not.toHaveBeenCalled()
    })

    it('provides empty profiles list when fetch fails', async () => {
      mockApi.get.mockRejectedValueOnce(new HttpError('Not found', 404))
      mockJpApi.list.mockRejectedValueOnce(new Error('Network error'))
      const { useOpeningResume } = await import('./useOpeningResume')
      const { result } = renderHook(() => useOpeningResume('o1'))
      await act(async () => {})
      expect(result.current.jobProfiles).toEqual([])
      expect(result.current.notFound).toBe(true)
    })

    it('passes sourceJobProfileId to create API call', async () => {
      mockApi.get.mockRejectedValueOnce(new HttpError('Not found', 404))
      mockApi.create.mockResolvedValueOnce(resume)
      const { useOpeningResume } = await import('./useOpeningResume')
      const { result } = renderHook(() => useOpeningResume('o1'))
      await act(async () => {})
      await act(async () => { await result.current.createResume('jp1') })
      expect(mockApi.create).toHaveBeenCalledWith('o1', 'jp1')
    })
  })
})
