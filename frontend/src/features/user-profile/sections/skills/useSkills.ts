import { useState, useCallback, useEffect } from 'react'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'

export function useSkills() {
  const [skills, setSkills] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await profileApi.getSkills()
      setSkills(data.skills)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to load skills')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)
    profileApi.getSkills()
      .then(data => { if (!cancelled) setSkills(data.skills) })
      .catch(err => {
        if (!cancelled) setError(err instanceof HttpError ? err.message : 'Failed to load skills')
      })
      .finally(() => { if (!cancelled) setIsLoading(false) })
    return () => { cancelled = true }
  }, [])

  const replaceAll = useCallback(async (newSkills: string[]) => {
    setIsSaving(true)
    setError(null)
    try {
      const data = await profileApi.updateSkills(newSkills)
      setSkills(data.skills)
      return data
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save skills')
      throw err
    } finally {
      setIsSaving(false)
    }
  }, [])

  return { skills, isLoading, isSaving, error, refresh, replaceAll }
}
