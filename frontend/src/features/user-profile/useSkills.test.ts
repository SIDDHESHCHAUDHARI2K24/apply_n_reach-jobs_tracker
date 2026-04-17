import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as profileApiModule from '@features/user-profile/profileApi'

vi.mock('@features/user-profile/profileApi', () => ({
  profileApi: {
    getSkills: vi.fn(),
    updateSkills: vi.fn(),
  },
}))

beforeEach(() => vi.clearAllMocks())

describe('useSkills', () => {
  it('loads skills on mount', async () => {
    ;(profileApiModule.profileApi.getSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ skills: ['TypeScript', 'React'] })
    const { useSkills } = await import('./sections/skills/useSkills')
    const { result } = renderHook(() => useSkills())
    await act(async () => {})
    expect(result.current.skills).toEqual(['TypeScript', 'React'])
  })

  it('replaceAll updates skills', async () => {
    ;(profileApiModule.profileApi.getSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ skills: [] })
    ;(profileApiModule.profileApi.updateSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ skills: ['Go', 'Rust'] })
    const { useSkills } = await import('./sections/skills/useSkills')
    const { result } = renderHook(() => useSkills())
    await act(async () => {})
    await act(async () => {
      await result.current.replaceAll(['Go', 'Rust'])
    })
    expect(result.current.skills).toEqual(['Go', 'Rust'])
  })
})
