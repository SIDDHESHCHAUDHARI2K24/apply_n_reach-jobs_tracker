import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as jtApiModule from '@features/job-tracker/jobTrackerApi'
vi.mock('@features/job-tracker/jobTrackerApi', () => ({
  jobTrackerApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    transitionStatus: vi.fn(),
    getStatusHistory: vi.fn(),
  },
}))

const mockApi = jtApiModule.jobTrackerApi as unknown as {
  list: ReturnType<typeof vi.fn>
  create: ReturnType<typeof vi.fn>
  update: ReturnType<typeof vi.fn>
  remove: ReturnType<typeof vi.fn>
  transitionStatus: ReturnType<typeof vi.fn>
  getStatusHistory: ReturnType<typeof vi.fn>
}

const opening = { id: '1', user_id: 'u1', company: 'ACME', role: 'Engineer', url: null, status: 'discovered' as const, notes: null, created_at: '', updated_at: '' }

beforeEach(() => vi.clearAllMocks())

describe('useJobOpenings', () => {
  it('loads openings on mount', async () => {
    mockApi.list.mockResolvedValueOnce([opening])
    const { useJobOpenings } = await import('./openings/useJobOpenings')
    const { result } = renderHook(() => useJobOpenings())
    await act(async () => {})
    expect(result.current.openings).toEqual([opening])
    expect(result.current.isLoading).toBe(false)
  })

  it('creates an opening and prepends to list', async () => {
    mockApi.list.mockResolvedValueOnce([])
    mockApi.create.mockResolvedValueOnce(opening)
    const { useJobOpenings } = await import('./openings/useJobOpenings')
    const { result } = renderHook(() => useJobOpenings())
    await act(async () => {})
    await act(async () => {
      await result.current.create({ company: 'ACME', role: 'Engineer' })
    })
    expect(result.current.openings).toHaveLength(1)
  })

  it('transitions status and updates opening in list', async () => {
    const updated = { ...opening, status: 'applied' as const }
    mockApi.list.mockResolvedValueOnce([opening])
    mockApi.transitionStatus.mockResolvedValueOnce(updated)
    const { useJobOpenings } = await import('./openings/useJobOpenings')
    const { result } = renderHook(() => useJobOpenings())
    await act(async () => {})
    await act(async () => {
      await result.current.transitionStatus('1', 'applied')
    })
    expect(result.current.openings[0].status).toBe('applied')
  })

  it('removes an opening from list', async () => {
    mockApi.list.mockResolvedValueOnce([opening])
    mockApi.remove.mockResolvedValueOnce(undefined)
    const { useJobOpenings } = await import('./openings/useJobOpenings')
    const { result } = renderHook(() => useJobOpenings())
    await act(async () => {})
    await act(async () => { await result.current.remove('1') })
    expect(result.current.openings).toHaveLength(0)
  })

  it('applies status filter when loading', async () => {
    mockApi.list.mockResolvedValue([])
    const { useJobOpenings } = await import('./openings/useJobOpenings')
    const { result } = renderHook(() => useJobOpenings())
    await act(async () => {})
    act(() => result.current.setFilters({ status: 'applied' }))
    await act(async () => {})
    expect(mockApi.list).toHaveBeenCalledWith(expect.objectContaining({ status: 'applied' }))
  })
})
