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
    ;(profileApiModule.profileApi.getSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      technical: ['TypeScript', 'React'],
      competency: ['Team Leadership'],
    })
    const { useSkills } = await import('./sections/skills/useSkills')
    const { result } = renderHook(() => useSkills())
    await act(async () => {})
    expect(result.current.skills.technical).toEqual(['TypeScript', 'React'])
    expect(result.current.skills.competency).toEqual(['Team Leadership'])
  })

  it('updateSkills updates skills', async () => {
    ;(profileApiModule.profileApi.getSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      technical: [],
      competency: [],
    })
    ;(profileApiModule.profileApi.updateSkills as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      technical: ['Go', 'Rust'],
      competency: ['Problem Solving'],
    })
    const { useSkills } = await import('./sections/skills/useSkills')
    const { result } = renderHook(() => useSkills())
    await act(async () => {})
    await act(async () => {
      await result.current.updateSkills({ technical: ['Go', 'Rust'], competency: ['Problem Solving'] })
    })
    expect(result.current.skills.technical).toEqual(['Go', 'Rust'])
    expect(result.current.skills.competency).toEqual(['Problem Solving'])
  })
})
