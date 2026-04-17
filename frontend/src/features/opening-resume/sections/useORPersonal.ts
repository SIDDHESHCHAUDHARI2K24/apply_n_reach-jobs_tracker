import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'
import type { ORPersonal } from '@features/opening-resume/types'

export function useORPersonal(openingId: string) {
  const [data, setData] = useState<ORPersonal | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    openingResumeApi.getPersonal(openingId)
      .then(d => { if (!cancelled) { setData(d); setIsLoading(false) } })
      .catch(err => {
        if (!cancelled) {
          if (err instanceof HttpError && err.status === 404) setData(null)
          else setError(err instanceof HttpError ? err.message : 'Failed to load')
          setIsLoading(false)
        }
      })
    return () => { cancelled = true }
  }, [openingId])

  const save = useCallback(async (patch: Partial<Omit<ORPersonal, 'id' | 'resume_id' | 'updated_at'>>) => {
    setIsSaving(true); setError(null)
    try {
      const updated = await openingResumeApi.updatePersonal(openingId, patch)
      setData(updated); setIsSaving(false)
      return updated
    } catch (err) { setError(err instanceof HttpError ? err.message : 'Failed to save'); setIsSaving(false); throw err }
  }, [openingId])

  return { data, isLoading, isSaving, error, save }
}
