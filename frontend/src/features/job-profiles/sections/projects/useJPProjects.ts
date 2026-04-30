import { useState, useCallback } from 'react'
import type { JPProject } from '@features/job-profiles/types'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

export function useJPProjects(jobProfileId: string) {
  const [items, setItems] = useState<JPProject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await jobProfileApi.getProjects(jobProfileId)
      setItems(data)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to load projects')
    } finally {
      setIsLoading(false)
    }
  }, [jobProfileId])

  const create = async (data: Omit<JPProject, 'id' | 'job_profile_id'>) => {
    const created = await jobProfileApi.createProject(jobProfileId, data)
    setItems(prev => [...prev, created])
    return created
  }

  const update = async (itemId: string, data: Partial<Omit<JPProject, 'id' | 'job_profile_id'>>) => {
    const updated = await jobProfileApi.updateProject(jobProfileId, itemId, data)
    setItems(prev => prev.map(item => item.id === itemId ? updated : item))
    return updated
  }

  const remove = async (itemId: string) => {
    await jobProfileApi.deleteProject(jobProfileId, itemId)
    setItems(prev => prev.filter(item => item.id !== itemId))
  }

  const importAll = async () => {
    const result = await jobProfileApi.importProjects(jobProfileId)
    await load()
    return result
  }

  return { items, isLoading, error, load, create, update, remove, importAll }
}
