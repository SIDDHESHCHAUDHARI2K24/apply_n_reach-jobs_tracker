import { useState, useCallback, useEffect, useRef } from 'react'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import { HttpError } from '@core/http/client'
import type { JobOpening, CreateOpeningRequest, OpeningFilters, OpeningStatus } from '@features/job-tracker/types'

const PAGE_SIZE = 20

interface State {
  openings: JobOpening[]
  isLoading: boolean
  isSaving: boolean
  error: string | null
  hasMore: boolean
}

export function useJobOpenings() {
  const [state, setState] = useState<State>({
    openings: [],
    isLoading: true,
    isSaving: false,
    error: null,
    hasMore: false,
  })
  // Use refs for cursor and filters so loadMore/fetchPage always see current values
  const [filters, setFiltersState] = useState<OpeningFilters>({})
  const lastIdRef = useRef<string | null>(null)
  const filtersRef = useRef<OpeningFilters>({})

  // Keep filtersRef in sync
  useEffect(() => {
    filtersRef.current = filters
  }, [filters])

  const fetchPage = useCallback(async (f: OpeningFilters, afterId: string | null, replace: boolean) => {
    setState(s => ({ ...s, isLoading: true, error: null }))
    try {
      const params: Parameters<typeof jobTrackerApi.list>[0] = { limit: PAGE_SIZE }
      if (f.status) params.status = f.status
      if (f.company) params.company = f.company
      if (f.role) params.role = f.role
      if (afterId) params.after_id = afterId
      const items = await jobTrackerApi.list(params)
      const newLastId = items.length > 0 ? items[items.length - 1].id : afterId
      lastIdRef.current = newLastId
      setState(s => ({
        ...s,
        openings: replace ? items : [...s.openings, ...items],
        isLoading: false,
        hasMore: items.length === PAGE_SIZE,
      }))
    } catch (err) {
      setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
    }
  }, [])

  // Load on mount and when filters change
  useEffect(() => {
    let cancelled = false
    lastIdRef.current = null
    setState(s => ({ ...s, isLoading: true, error: null, openings: [] }))
    const params: Parameters<typeof jobTrackerApi.list>[0] = { limit: PAGE_SIZE }
    if (filters.status) params.status = filters.status
    if (filters.company) params.company = filters.company
    if (filters.role) params.role = filters.role
    jobTrackerApi.list(params)
      .then(items => {
        if (!cancelled) {
          lastIdRef.current = items.length > 0 ? items[items.length - 1].id : null
          setState(s => ({
            ...s,
            openings: items,
            isLoading: false,
            hasMore: items.length === PAGE_SIZE,
          }))
        }
      })
      .catch(err => {
        if (!cancelled) setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
      })
    return () => { cancelled = true }
  }, [filters])  // 'filters' is a separate useState, not part of combined state object

  const setFilters = useCallback((f: OpeningFilters) => {
    setFiltersState(f)
  }, [])

  // loadMore reads from ref — no stale closure, no side effects in updater
  const loadMore = useCallback(() => {
    fetchPage(filtersRef.current, lastIdRef.current, false)
  }, [fetchPage])

  const create = useCallback(async (data: CreateOpeningRequest) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const opening = await jobTrackerApi.create(data)
      setState(s => ({ ...s, openings: [opening, ...s.openings], isSaving: false }))
      return opening
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to create' }))
      throw err
    }
  }, [])

  const update = useCallback(async (id: string, data: Partial<CreateOpeningRequest>) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const opening = await jobTrackerApi.update(id, data)
      setState(s => ({ ...s, openings: s.openings.map(o => o.id === id ? opening : o), isSaving: false }))
      return opening
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to update' }))
      throw err
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      await jobTrackerApi.remove(id)
      setState(s => ({ ...s, openings: s.openings.filter(o => o.id !== id), isSaving: false }))
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to delete' }))
      throw err
    }
  }, [])

  const transitionStatus = useCallback(async (id: string, status: OpeningStatus) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const opening = await jobTrackerApi.transitionStatus(id, status)
      setState(s => ({ ...s, openings: s.openings.map(o => o.id === id ? opening : o), isSaving: false }))
      return opening
    } catch (err) {
      setState(s => ({ ...s, isSaving: false, error: err instanceof HttpError ? err.message : 'Failed to update status' }))
      throw err
    }
  }, [])

  return { ...state, filters, setFilters, loadMore, create, update, remove, transitionStatus }
}
