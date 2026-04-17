import { useState, useCallback, useEffect } from 'react'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'
import type { Experience } from '@features/user-profile/types'

interface State {
  items: Experience[]
  isLoading: boolean
  isSaving: boolean
  error: string | null
}

export function useExperience() {
  const [state, setState] = useState<State>({ items: [], isLoading: true, isSaving: false, error: null })

  const refresh = useCallback(async () => {
    setState(s => ({ ...s, isLoading: true, error: null }))
    try {
      const items = await profileApi.getExperience()
      setState(s => ({ ...s, items, isLoading: false }))
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Failed to load'
      setState(s => ({ ...s, isLoading: false, error: message }))
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    setState(s => ({ ...s, isLoading: true, error: null }))
    profileApi.getExperience()
      .then(items => { if (!cancelled) setState(s => ({ ...s, items, isLoading: false })) })
      .catch(err => {
        if (!cancelled) setState(s => ({ ...s, isLoading: false, error: err instanceof HttpError ? err.message : 'Failed to load' }))
      })
    return () => { cancelled = true }
  }, [])

  const create = useCallback(async (data: Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const item = await profileApi.createExperience(data)
      setState(s => ({ ...s, items: [...s.items, item], isSaving: false }))
      return item
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Failed to save'
      setState(s => ({ ...s, isSaving: false, error: message }))
      throw err
    }
  }, [])

  const update = useCallback(async (id: string, data: Partial<Omit<Experience, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      const item = await profileApi.updateExperience(id, data)
      setState(s => ({ ...s, items: s.items.map(i => i.id === id ? item : i), isSaving: false }))
      return item
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Failed to save'
      setState(s => ({ ...s, isSaving: false, error: message }))
      throw err
    }
  }, [])

  const remove = useCallback(async (id: string) => {
    setState(s => ({ ...s, isSaving: true, error: null }))
    try {
      await profileApi.deleteExperience(id)
      setState(s => ({ ...s, items: s.items.filter(i => i.id !== id), isSaving: false }))
    } catch (err) {
      const message = err instanceof HttpError ? err.message : 'Failed to delete'
      setState(s => ({ ...s, isSaving: false, error: message }))
      throw err
    }
  }, [])

  return { ...state, refresh, create, update, remove }
}
