import { useState, useCallback, useEffect } from 'react'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'

export interface SkillsData {
  technical: string[]
  competency: string[]
}

export function useSkills() {
  const [skills, setSkills] = useState<SkillsData>({ technical: [], competency: [] })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await profileApi.getSkills()
      setSkills({ technical: data.technical, competency: data.competency })
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
      .then(data => {
        if (!cancelled) setSkills({ technical: data.technical, competency: data.competency })
      })
      .catch(err => {
        if (!cancelled) setError(err instanceof HttpError ? err.message : 'Failed to load skills')
      })
      .finally(() => { if (!cancelled) setIsLoading(false) })
    return () => { cancelled = true }
  }, [])

  const updateSkills = useCallback(async ({ technical, competency }: SkillsData) => {
    setIsSaving(true)
    setError(null)
    try {
      const data = await profileApi.updateSkills({ technical, competency })
      setSkills({ technical: data.technical, competency: data.competency })
      return data
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save skills')
      throw err
    } finally {
      setIsSaving(false)
    }
  }, [])

  return { skills, isLoading, isSaving, error, refresh, updateSkills }
}
