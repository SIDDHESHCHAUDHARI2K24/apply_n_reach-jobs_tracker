import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as jpApiModule from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/job-profiles/jobProfileApi', () => ({
  jobProfileApi: {
    list: vi.fn(),
    create: vi.fn(),
    activate: vi.fn(),
    archive: vi.fn(),
    remove: vi.fn(),
  },
}))

const mockApi = jpApiModule.jobProfileApi as unknown as {
  list: ReturnType<typeof vi.fn>
  create: ReturnType<typeof vi.fn>
  activate: ReturnType<typeof vi.fn>
  archive: ReturnType<typeof vi.fn>
  remove: ReturnType<typeof vi.fn>
}

const profile = { id: '1', user_id: 'u1', title: 'Test Profile', status: 'draft' as const, created_at: '', updated_at: '' }

beforeEach(() => vi.clearAllMocks())

describe('useJobProfiles', () => {
  it('loads profiles on mount', async () => {
    mockApi.list.mockResolvedValueOnce([profile])
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    expect(result.current.profiles).toEqual([profile])
    expect(result.current.isLoading).toBe(false)
  })

  it('filters by status', async () => {
    mockApi.list.mockResolvedValue([])
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    act(() => result.current.setFilter('active'))
    await act(async () => {})
    expect(mockApi.list).toHaveBeenCalledWith(expect.objectContaining({ status: 'active' }))
  })

  it('creates a profile and prepends to list', async () => {
    mockApi.list.mockResolvedValueOnce([])
    mockApi.create.mockResolvedValueOnce(profile)
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    await act(async () => {
      await result.current.create({ title: 'Test Profile' })
    })
    expect(result.current.profiles).toHaveLength(1)
  })

  it('removes a profile from list', async () => {
    mockApi.list.mockResolvedValueOnce([profile])
    mockApi.remove.mockResolvedValueOnce(undefined)
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    await act(async () => { await result.current.remove('1') })
    expect(result.current.profiles).toHaveLength(0)
  })

  it('activates a profile', async () => {
    mockApi.list.mockResolvedValueOnce([profile])
    mockApi.activate.mockResolvedValueOnce({ ...profile, status: 'active' })
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    await act(async () => { await result.current.activate('1') })
    expect(result.current.profiles[0]?.status).toBe('active')
  })

  it('archives a profile', async () => {
    mockApi.list.mockResolvedValueOnce([{ ...profile, status: 'active' }])
    mockApi.archive.mockResolvedValueOnce({ ...profile, status: 'archived' })
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    await act(async () => { await result.current.archive('1') })
    expect(result.current.profiles[0]?.status).toBe('archived')
  })

  it('sets error on load failure', async () => {
    mockApi.list.mockRejectedValueOnce(new HttpError('Unauthorized', 401))
    const { useJobProfiles } = await import('./list/useJobProfiles')
    const { result } = renderHook(() => useJobProfiles())
    await act(async () => {})
    expect(result.current.error).toBe('Unauthorized')
  })
})
