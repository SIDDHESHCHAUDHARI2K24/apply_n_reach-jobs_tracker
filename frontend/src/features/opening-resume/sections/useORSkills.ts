import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'

export function useORSkills(openingId: string) {
  const [skills, setSkills] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    openingResumeApi.getSkills(openingId)
      .then(d => { if (!cancelled) { setSkills(d.skills); setIsLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err instanceof HttpError ? err.message : 'Failed to load'); setIsLoading(false) } })
    return () => { cancelled = true }
  }, [openingId])

  const replaceAll = useCallback(async (newSkills: string[]) => {
    setIsSaving(true); setError(null)
    try {
      const d = await openingResumeApi.updateSkills(openingId, newSkills)
      setSkills(d.skills); setIsSaving(false)
      return d
    } catch (err) { setError(err instanceof HttpError ? err.message : 'Failed to save'); setIsSaving(false); throw err }
  }, [openingId])

  return { skills, isLoading, isSaving, error, replaceAll }
}
