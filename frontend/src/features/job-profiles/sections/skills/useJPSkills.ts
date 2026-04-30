import { useState, useEffect, useCallback } from 'react'
import type { JPSkills } from '@features/job-profiles/types'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

export function useJPSkills(jobProfileId: string) {
  const [skills, setSkills] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await jobProfileApi.getSkills(jobProfileId)
      setSkills(data.skills)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to load skills')
    } finally {
      setIsLoading(false)
    }
  }, [jobProfileId])

  useEffect(() => { load() }, [load])

  const update = async (skillNames: string[]) => {
    const data = await jobProfileApi.updateSkills(jobProfileId, skillNames)
    setSkills(data.skills)
    return data
  }

  const importAll = async () => {
    const result = await jobProfileApi.importSkills(jobProfileId)
    await load()
    return result
  }

  return { skills, isLoading, error, load, update, importAll }
}
