import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'
import type { ORCertification } from '@features/opening-resume/types'

export function useORCertifications(openingId: string) {
  const [items, setItems] = useState<ORCertification[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    openingResumeApi.getCertifications(openingId)
      .then(data => { if (!cancelled) { setItems(data); setIsLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err instanceof HttpError ? err.message : 'Failed to load'); setIsLoading(false) } })
    return () => { cancelled = true }
  }, [openingId])

  const create = useCallback(async (data: Omit<ORCertification, 'id' | 'resume_id'>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.createCertification(openingId, data)
      setItems(s => [...s, item]); setIsSaving(false)
      return item
    } catch (err) { setError(err instanceof HttpError ? err.message : 'Failed to save'); setIsSaving(false); throw err }
  }, [openingId])

  const update = useCallback(async (id: string, data: Partial<Omit<ORCertification, 'id' | 'resume_id'>>) => {
    setIsSaving(true); setError(null)
    try {
      const item = await openingResumeApi.updateCertification(openingId, id, data)
      setItems(s => s.map(i => i.id === id ? item : i)); setIsSaving(false)
      return item
    } catch (err) { setError(err instanceof HttpError ? err.message : 'Failed to save'); setIsSaving(false); throw err }
  }, [openingId])

  const remove = useCallback(async (id: string) => {
    setIsSaving(true); setError(null)
    try {
      await openingResumeApi.deleteCertification(openingId, id)
      setItems(s => s.filter(i => i.id !== id)); setIsSaving(false)
    } catch (err) { setError(err instanceof HttpError ? err.message : 'Failed to delete'); setIsSaving(false); throw err }
  }, [openingId])

  return { items, isLoading, isSaving, error, create, update, remove }
}
