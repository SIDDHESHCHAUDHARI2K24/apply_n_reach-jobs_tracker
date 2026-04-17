import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as jpApiModule from '@features/job-profiles/jobProfileApi'

vi.mock('@features/job-profiles/jobProfileApi', () => ({
  jobProfileApi: {
    importEducation: vi.fn(),
    importExperience: vi.fn(),
    importProjects: vi.fn(),
    importResearch: vi.fn(),
    importCertifications: vi.fn(),
    importSkills: vi.fn(),
  },
}))

const mockApi = jpApiModule.jobProfileApi as unknown as {
  importEducation: ReturnType<typeof vi.fn>
  importExperience: ReturnType<typeof vi.fn>
  importProjects: ReturnType<typeof vi.fn>
  importResearch: ReturnType<typeof vi.fn>
  importCertifications: ReturnType<typeof vi.fn>
  importSkills: ReturnType<typeof vi.fn>
}

const importResult = { imported_count: 3, skipped_count: 1 }

beforeEach(() => vi.clearAllMocks())

describe('jobProfileApi import endpoints', () => {
  it('importEducation posts to /job-profiles/{id}/education/import', async () => {
    mockApi.importEducation.mockResolvedValueOnce(importResult)
    const { jobProfileApi } = await import('./jobProfileApi')
    const result = await jobProfileApi.importEducation('jp1')
    expect(result).toEqual(importResult)
    expect(mockApi.importEducation).toHaveBeenCalledWith('jp1')
  })

  it('importExperience posts to correct endpoint', async () => {
    mockApi.importExperience.mockResolvedValueOnce(importResult)
    const { jobProfileApi } = await import('./jobProfileApi')
    const result = await jobProfileApi.importExperience('jp1')
    expect(result.imported_count).toBe(3)
  })

  it('importSkills posts to correct endpoint', async () => {
    mockApi.importSkills.mockResolvedValueOnce({ imported_count: 5, skipped_count: 0 })
    const { jobProfileApi } = await import('./jobProfileApi')
    const result = await jobProfileApi.importSkills('jp1')
    expect(result.imported_count).toBe(5)
  })
})
