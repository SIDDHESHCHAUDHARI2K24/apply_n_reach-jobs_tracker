import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import {
  OPENING_RESUME_REFRESH_EVENT,
  type OpeningResumeRefreshDetail,
} from '@features/opening-resume/openingResumeEvents'
import { HttpError } from '@core/http/client'
import type { ORResearch } from '@features/opening-resume/types'

export function useORResearch(openingId: string) {
  const [items, setItems] = useState<ORResearch[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadResearch = useCallback(() => {
    setIsLoading(true)
    setError(null)
    openingResumeApi
      .getResearch(openingId)
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
    loadResearch()
  }, [loadResearch])

  useEffect(() => {
    function onOpeningResumeRefresh(ev: Event) {
      const ce = ev as CustomEvent<OpeningResumeRefreshDetail>
      if (ce.detail?.openingId !== openingId) return
      loadResearch()
    }
    window.addEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
    return () => window.removeEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
  }, [openingId, loadResearch])

  const create = useCallback(async (data: Omit<ORResearch, 'id' | 'resume_id'>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.createResearch(openingId, data)
      setItems(s => [...s, item]); setIsSaving(false)
      return item
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save')
      setIsSaving(false); throw err
    }
  }, [openingId])

  const update = useCallback(async (id: string, data: Partial<Omit<ORResearch, 'id' | 'resume_id'>>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.updateResearch(openingId, id, data)
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
      await openingResumeApi.deleteResearch(openingId, id)
      setItems(s => s.filter(i => i.id !== id)); setIsSaving(false)
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to delete')
      setIsSaving(false); throw err
    }
  }, [openingId])

  return { items, isLoading, isSaving, error, create, update, remove }
}
