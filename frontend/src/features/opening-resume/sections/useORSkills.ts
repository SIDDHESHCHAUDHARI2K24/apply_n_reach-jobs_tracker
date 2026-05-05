import { useState, useCallback, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import {
  OPENING_RESUME_REFRESH_EVENT,
  type OpeningResumeRefreshDetail,
} from '@features/opening-resume/openingResumeEvents'
import { HttpError } from '@core/http/client'
import type { ORSkillItem } from '@features/opening-resume/types'

export function useORSkills(openingId: string) {
  const [skills, setSkills] = useState<ORSkillItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSkills = useCallback(() => {
    setIsLoading(true)
    setError(null)
    openingResumeApi
      .getSkills(openingId)
      .then(items => {
        setSkills(items)
        setIsLoading(false)
      })
      .catch(err => {
        setError(err instanceof HttpError ? err.message : 'Failed to load')
        setIsLoading(false)
      })
  }, [openingId])

  useEffect(() => {
    loadSkills()
  }, [loadSkills])

  useEffect(() => {
    function onOpeningResumeRefresh(ev: Event) {
      const ce = ev as CustomEvent<OpeningResumeRefreshDetail>
      if (ce.detail?.openingId !== openingId) return
      loadSkills()
    }
    window.addEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
    return () => window.removeEventListener(OPENING_RESUME_REFRESH_EVENT, onOpeningResumeRefresh as EventListener)
  }, [openingId, loadSkills])

  const create = useCallback(async (payload: Omit<ORSkillItem, 'id' | 'resume_id'>) => {
    setIsSaving(true)
    setError(null)
    try {
      const created = await openingResumeApi.createSkill(openingId, payload)
      setSkills(prev => [...prev, created])
      return created
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to save')
      throw err
    } finally {
      setIsSaving(false)
    }
  }, [openingId])

  const remove = useCallback(async (id: string) => {
    setIsSaving(true)
    setError(null)
    try {
      await openingResumeApi.deleteSkill(openingId, id)
      setSkills(prev => prev.filter(item => item.id !== id))
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Failed to delete')
      throw err
    } finally {
      setIsSaving(false)
    }
  }, [openingId])

  return { skills, isLoading, isSaving, error, create, remove }
}
