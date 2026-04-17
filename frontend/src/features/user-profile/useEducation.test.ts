import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as profileApiModule from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'

vi.mock('@features/user-profile/profileApi', () => ({
  profileApi: {
    getEducation: vi.fn(),
    createEducation: vi.fn(),
    updateEducation: vi.fn(),
    deleteEducation: vi.fn(),
  },
}))

const item = { id: '1', profile_id: 'p1', institution: 'MIT', degree: 'BS', field_of_study: null, start_date: null, end_date: null, gpa: null, bullet_points: [], created_at: '', updated_at: '' }

beforeEach(() => vi.clearAllMocks())

describe('useEducation', () => {
  it('loads items on mount', async () => {
    ;(profileApiModule.profileApi.getEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce([item])
    const { useEducation } = await import('./sections/education/useEducation')
    const { result } = renderHook(() => useEducation())
    expect(result.current.isLoading).toBe(true)
    await act(async () => {})
    expect(result.current.items).toEqual([item])
    expect(result.current.isLoading).toBe(false)
  })

  it('creates an item and adds to list', async () => {
    ;(profileApiModule.profileApi.getEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce([])
    ;(profileApiModule.profileApi.createEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce(item)
    const { useEducation } = await import('./sections/education/useEducation')
    const { result } = renderHook(() => useEducation())
    await act(async () => {})
    await act(async () => {
      await result.current.create({ institution: 'MIT', degree: 'BS', field_of_study: null, start_date: null, end_date: null, gpa: null, bullet_points: [] })
    })
    expect(result.current.items).toHaveLength(1)
  })

  it('removes an item from list', async () => {
    ;(profileApiModule.profileApi.getEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce([item])
    ;(profileApiModule.profileApi.deleteEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce(undefined)
    const { useEducation } = await import('./sections/education/useEducation')
    const { result } = renderHook(() => useEducation())
    await act(async () => {})
    await act(async () => {
      await result.current.remove('1')
    })
    expect(result.current.items).toHaveLength(0)
  })

  it('updates an item in the list', async () => {
    const updated = { ...item, degree: 'MS' }
    ;(profileApiModule.profileApi.getEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce([item])
    ;(profileApiModule.profileApi.updateEducation as ReturnType<typeof vi.fn>).mockResolvedValueOnce(updated)
    const { useEducation } = await import('./sections/education/useEducation')
    const { result } = renderHook(() => useEducation())
    await act(async () => {})
    await act(async () => {
      await result.current.update('1', { degree: 'MS' })
    })
    expect(result.current.items[0].degree).toBe('MS')
  })

  it('sets error on load failure', async () => {
    ;(profileApiModule.profileApi.getEducation as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new HttpError('Server error', 500))
    const { useEducation } = await import('./sections/education/useEducation')
    const { result } = renderHook(() => useEducation())
    await act(async () => {})
    expect(result.current.error).toBe('Server error')
  })
})
