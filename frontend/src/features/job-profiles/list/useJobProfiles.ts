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

function normalizePage(result: Awaited<ReturnType<typeof jobProfileApi.list>>) {
  if (Array.isArray(result)) {
    return { items: result, total: result.length, offset: 0 }
  }
  return result
}

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
      const page = normalizePage(await jobProfileApi.list(params))
      const items = page.items
      offsetRef.current = offset + items.length
      setState(s => ({
        ...s,
        profiles: offset === 0 ? items : [...s.profiles, ...items],
        isLoading: false,
        hasMore: page.offset + page.items.length < page.total || items.length === PAGE_SIZE,
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
      .then(result => {
        if (!cancelled) {
          const page = normalizePage(result)
          const items = page.items
          offsetRef.current = items.length
          setState(s => ({
            ...s,
            profiles: items,
            isLoading: false,
            hasMore: page.offset + page.items.length < page.total || items.length === PAGE_SIZE,
          }))
        }
      })
      .catch(err => {
        if (!cancelled) setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
      })
    return () => { cancelled = true }
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

  const activate = useCallback(async (id: string) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const updated = await jobProfileApi.activate(id)
      setState(s => ({
        ...s,
        profiles: s.profiles.map(p => (p.id === id ? updated : p)),
        isSaving: false,
      }))
      return updated
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to activate' }))
      throw err
    }
  }, [])

  const archive = useCallback(async (id: string) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const updated = await jobProfileApi.archive(id)
      setState(s => ({
        ...s,
        profiles: s.profiles.map(p => (p.id === id ? updated : p)),
        isSaving: false,
      }))
      return updated
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to archive' }))
      throw err
    }
  }, [])

  return { ...state, setFilter, loadMore, create, remove, activate, archive }
}
