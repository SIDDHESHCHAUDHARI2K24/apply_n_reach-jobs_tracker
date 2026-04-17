import { useState, useCallback, useEffect, useRef } from 'react'
import { openingResumeApi } from './openingResumeApi'
import { HttpError } from '@core/http/client'
import type { OpeningResume } from './types'

interface State {
  resume: OpeningResume | null
  isLoading: boolean
  isCreating: boolean
  error: string | null
  notFound: boolean
  conflict: boolean
}

export function useOpeningResume(openingId: string) {
  const [state, setState] = useState<State>({
    resume: null,
    isLoading: true,
    isCreating: false,
    error: null,
    notFound: false,
    conflict: false,
  })
  const cancelledRef = useRef(false)

  const loadResume = useCallback(async () => {
    setState(s => ({ ...s, isLoading: true, error: null, notFound: false }))
    try {
      const resume = await openingResumeApi.get(openingId)
      if (!cancelledRef.current) setState(s => ({ ...s, resume, isLoading: false }))
    } catch (err) {
      if (!cancelledRef.current) {
        if (err instanceof HttpError && err.status === 404) {
          setState(s => ({ ...s, isLoading: false, notFound: true }))
        } else {
          setState(s => ({ ...s, isLoading: false, error: err instanceof Error ? err.message : 'Failed to load resume' }))
        }
      }
    }
  }, [openingId])

  useEffect(() => {
    cancelledRef.current = false
    loadResume()
    return () => { cancelledRef.current = true }
  }, [loadResume])

  const createResume = useCallback(async (sourceJobProfileId?: string) => {
    setState(s => ({ ...s, isCreating: true, error: null, conflict: false }))
    try {
      const resume = await openingResumeApi.create(openingId, sourceJobProfileId)
      if (!cancelledRef.current) setState(s => ({ ...s, resume, isCreating: false, notFound: false }))
      return resume
    } catch (err) {
      if (err instanceof HttpError && err.status === 409) {
        if (!cancelledRef.current) setState(s => ({ ...s, isCreating: false, conflict: true }))
        await loadResume()
      } else {
        if (!cancelledRef.current) setState(s => ({ ...s, isCreating: false, error: err instanceof Error ? err.message : 'Failed to create resume' }))
        throw err
      }
    }
  }, [openingId, loadResume])

  return { ...state, createResume, loadResume }
}
