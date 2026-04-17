import { useState, useCallback, useEffect, useRef } from 'react'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'
import type { JobProfile, JobProfileStatus, CreateJobProfileRequest } from '@features/job-profiles/types'

interface State {
  profiles: JobProfile[]
  isLoading: boolean
  isSaving: boolean
  error: string | null
  statusFilter: JobProfileStatus | 'all'
  hasMore: boolean
}

const PAGE_SIZE = 20

export function useJobProfiles() {
  const [state, setState] = useState<State>({
    profiles: [],
    isLoading: true,
    isSaving: false,
    error: null,
    statusFilter: 'all',
    hasMore: false,
  })
  const offsetRef = useRef(0)

  const load = useCallback(async (filter: JobProfileStatus | 'all', offset: number) => {
    setState(s => ({ ...s, isLoading: true, error: null }))
    try {
      const params: { limit: number; offset: number; status?: string } = { limit: PAGE_SIZE, offset }
      if (filter !== 'all') params.status = filter
      const items = await jobProfileApi.list(params)
      offsetRef.current = offset + items.length
      setState(s => ({
        ...s,
        profiles: offset === 0 ? items : [...s.profiles, ...items],
        isLoading: false,
        hasMore: items.length === PAGE_SIZE,
      }))
    } catch (err) {
      setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const params: { limit: number; offset: number; status?: string } = { limit: PAGE_SIZE, offset: 0 }
    if (state.statusFilter !== 'all') params.status = state.statusFilter
    setState(s => ({ ...s, isLoading: true, error: null }))
    jobProfileApi.list(params)
      .then(items => {
        if (!cancelled) {
          offsetRef.current = items.length
          setState(s => ({ ...s, profiles: items, isLoading: false, hasMore: items.length === PAGE_SIZE }))
        }
      })
      .catch(err => {
        if (!cancelled) setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
      })
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.statusFilter])

  const setFilter = useCallback((filter: JobProfileStatus | 'all') => {
    offsetRef.current = 0
    setState(s => ({ ...s, statusFilter: filter, profiles: [] }))
  }, [])

  const loadMore = useCallback(() => {
    load(state.statusFilter, offsetRef.current)
  }, [load, state.statusFilter])

  const create = useCallback(async (data: CreateJobProfileRequest) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const jp = await jobProfileApi.create(data)
      setState(s => ({ ...s, profiles: [jp, ...s.profiles], isSaving: false }))
      return jp
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to create' }))
      throw err
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      await jobProfileApi.remove(id)
      setState(s => ({ ...s, profiles: s.profiles.filter(p => p.id !== id), isSaving: false }))
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to delete' }))
      throw err
    }
  }, [])

  return { ...state, setFilter, loadMore, create, remove }
}
