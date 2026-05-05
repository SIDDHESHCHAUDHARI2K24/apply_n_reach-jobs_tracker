import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import {
  OPENING_RESUME_REFRESH_EVENT,
  type OpeningResumeRefreshDetail,
} from '@features/opening-resume/openingResumeEvents'
import type { ORPersonal } from '@features/opening-resume/types'

export function useORPersonal(openingId: string) {
  const [data, setData] = useState<ORPersonal | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPersonal = useCallback(() => {
    setIsLoading(true)
    setError(null)
    openingResumeApi
      .getPersonal(openingId)
      .then(d => {
        setData(d)
        setIsLoading(false)
      })
      .catch(err => {
        if (err instanceof HttpError && err.status === 404) setData(null)
        else setError(err instanceof HttpError ? err.message : 'Failed to load')
        setIsLoading(false)
      })
  }, [openingId])

  useEffect(() => {
    loadPersonal()
  }, [loadPersonal])

  useEffect(() => {
    function onOpeningResumeRefresh(ev: Event) {
      const ce = ev as CustomEvent<OpeningResumeRefreshDetail>
      if (ce.detail?.openingId !== openingId) return
      loadPersonal()
    }
    window.addEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
    return () => window.removeEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
  }, [openingId, loadPersonal])

  const save = useCallback(async (patch: Partial<Omit<ORPersonal, 'id' | 'resume_id' | 'updated_at'>>) => {
    setIsSaving(true); setError(null)
    try {
      const updated = await openingResumeApi.updatePersonal(openingId, patch)
      setData(updated); setIsSaving(false)
      return updated
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save')
      setIsSaving(false); throw err
    }
  }, [openingId])

  return { data, isLoading, isSaving, error, save }
}
