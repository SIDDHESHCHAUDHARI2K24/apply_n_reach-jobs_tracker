import { useState, useEffect, useCallback } from 'react'
import type { JPResearch } from '@features/job-profiles/types'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

export function useJPResearch(jobProfileId: string) {
  const [items, setItems] = useState<JPResearch[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await jobProfileApi.getResearch(jobProfileId)
      setItems(data)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to load research')
    } finally {
      setIsLoading(false)
    }
  }, [jobProfileId])

  useEffect(() => { load() }, [load])

  const create = async (data: Omit<JPResearch, 'id' | 'job_profile_id'>) => {
    const created = await jobProfileApi.createResearch(jobProfileId, data)
    setItems(prev => [...prev, created])
    return created
  }

  const update = async (itemId: string, data: Partial<Omit<JPResearch, 'id' | 'job_profile_id'>>) => {
    const updated = await jobProfileApi.updateResearch(jobProfileId, itemId, data)
    setItems(prev => prev.map(item => item.id === itemId ? updated : item))
    return updated
  }

  const remove = async (itemId: string) => {
    await jobProfileApi.deleteResearch(jobProfileId, itemId)
    setItems(prev => prev.filter(item => item.id !== itemId))
  }

  const importAll = async () => {
    const result = await jobProfileApi.importResearch(jobProfileId)
    await load()
    return result
  }

  return { items, isLoading, error, load, create, update, remove, importAll }
}
