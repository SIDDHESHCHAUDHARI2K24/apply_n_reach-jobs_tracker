import { useState, useCallback, useEffect } from 'react'
import { profileApi } from '@features/user-profile/profileApi'
import { HttpError } from '@core/http/client'
import type { PersonalDetails } from '@features/user-profile/types'

export function usePersonal() {
  const [data, setData] = useState<PersonalDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const d = await profileApi.getPersonal()
      setData(d)
    } catch (err) {
      if (err instanceof HttpError && err.status === 404) {
        setData(null)
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load')
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)
    profileApi.getPersonal()
      .then(d => { if (!cancelled) setData(d) })
      .catch(err => {
        if (!cancelled) {
          if (err instanceof HttpError && err.status === 404) {
            setData(null)
          } else {
            setError(err instanceof Error ? err.message : 'Failed to load')
          }
        }
      })
      .finally(() => { if (!cancelled) setIsLoading(false) })
    return () => { cancelled = true }
  }, [])

  const save = useCallback(async (patch: Partial<Omit<PersonalDetails, 'id' | 'profile_id' | 'created_at' | 'updated_at'>>) => {
    setIsSaving(true)
    setError(null)
    try {
      const updated = await profileApi.updatePersonal(patch)
      setData(updated)
      return updated
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save')
      throw err
    } finally {
      setIsSaving(false)
    }
  }, [])

  return { data, isLoading, isSaving, error, refresh, save }
}
