import { useState, useCallback, useEffect, useRef } from 'react'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import { HttpError } from '@core/http/client'
import type { ExtractedDetails, ExtractionRun } from '@features/job-tracker/types'

interface IngestionState {
  isRefreshing: boolean
  isInFlight: boolean  // 409 — another extraction running
  latestDetails: ExtractedDetails | null
  runs: ExtractionRun[]
  error: string | null
  selectedOpeningId: string | null
  lastRunId: string | null
}

export function useIngestion() {
  const [state, setState] = useState<IngestionState>({
    isRefreshing: false,
    isInFlight: false,
    latestDetails: null,
    runs: [],
    error: null,
    selectedOpeningId: null,
    lastRunId: null,
  })
  const selectedOpeningIdRef = useRef<string | null>(null)

  useEffect(() => {
    selectedOpeningIdRef.current = state.selectedOpeningId
  }, [state.selectedOpeningId])

  const refresh = useCallback(async (openingIdArg?: string) => {
    const openingId = openingIdArg ?? selectedOpeningIdRef.current ?? ''
    setState(s => ({ ...s, isRefreshing: true, error: null, isInFlight: false }))
    try {
      const { run_id } = await jobTrackerApi.refreshExtraction(openingId)
      setState(s => ({ ...s, isRefreshing: false, lastRunId: run_id }))
      // Load latest extracted details and runs after starting
      const [details, runs] = await Promise.all([
        jobTrackerApi.getLatestExtracted(openingId),
        jobTrackerApi.getExtractionRuns(openingId),
      ])
      setState(s => ({ ...s, latestDetails: details, runs }))
    } catch (err) {
      if (err instanceof HttpError && err.status === 409) {
        setState(s => ({ ...s, isRefreshing: false, isInFlight: true }))
      } else {
        setState(s => ({ ...s, isRefreshing: false, error: err instanceof HttpError ? err.message : 'Extraction failed' }))
      }
    }
  }, [])

  const loadRuns = useCallback(async (openingIdArg?: string) => {
    const openingId = openingIdArg ?? selectedOpeningIdRef.current ?? ''
    try {
      const [details, runs] = await Promise.all([
        jobTrackerApi.getLatestExtracted(openingId),
        jobTrackerApi.getExtractionRuns(openingId),
      ])
      setState(s => ({ ...s, latestDetails: details, runs }))
    } catch (err) {
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Failed to load runs' }))
    }
  }, [])

  const setOpeningId = useCallback((openingId: string) => {
    setState(s => ({ ...s, selectedOpeningId: openingId }))
  }, [])

  return { ...state, refresh, loadRuns, setOpeningId }
}
