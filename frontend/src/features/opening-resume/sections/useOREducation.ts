import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import {
  OPENING_RESUME_REFRESH_EVENT,
  type OpeningResumeRefreshDetail,
} from '@features/opening-resume/openingResumeEvents'
import { HttpError } from '@core/http/client'
import type { OREducation } from '@features/opening-resume/types'

export function useOREducation(openingId: string) {
  const [items, setItems] = useState<OREducation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadEducation = useCallback(() => {
    setIsLoading(true)
    setError(null)
    openingResumeApi
      .getEducation(openingId)
      .then(data => {
        setItems(data)
        setIsLoading(false)
      })
      .catch(err => {
        setError(err instanceof HttpError ? err.message : 'Failed to load')
        setIsLoading(false)
      })
  }, [openingId])

  useEffect(() => {
    loadEducation()
  }, [loadEducation])

  useEffect(() => {
    function onOpeningResumeRefresh(ev: Event) {
      const ce = ev as CustomEvent<OpeningResumeRefreshDetail>
      if (ce.detail?.openingId !== openingId) return
      loadEducation()
    }
    window.addEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
    return () => window.removeEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
  }, [openingId, loadEducation])

  const create = useCallback(async (data: Omit<OREducation, 'id' | 'resume_id'>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.createEducation(openingId, data)
      setItems(s => [...s, item]); setIsSaving(false)
      return item
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save')
      setIsSaving(false); throw err
    }
  }, [openingId])

  const update = useCallback(async (id: string, data: Partial<Omit<OREducation, 'id' | 'resume_id'>>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.updateEducation(openingId, id, data)
      setItems(s => s.map(i => i.id === id ? item : i)); setIsSaving(false)
      return item
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save')
      setIsSaving(false); throw err
    }
  }, [openingId])

  const remove = useCallback(async (id: string) => {
    setIsSaving(true); setError(null)
    try {
      await openingResumeApi.deleteEducation(openingId, id)
      setItems(s => s.filter(i => i.id !== id)); setIsSaving(false)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to delete')
      setIsSaving(false); throw err
    }
  }, [openingId])

  return { items, isLoading, isSaving, error, create, update, remove }
}
