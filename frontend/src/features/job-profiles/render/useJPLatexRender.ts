import { useState, useCallback, useRef, useEffect } from 'react'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'
import type { ResumeMetadata, RenderStatus } from '@features/job-profiles/types'

const TERMINAL_STATES: RenderStatus[] = ['completed', 'failed']
const POLL_INTERVAL_MS = 3000
const MAX_RETRIES = 20  // ~60s

interface RenderState {
  metadata: ResumeMetadata | null
  isRendering: boolean
  isPolling: boolean
  error: string | null
  timedOut: boolean
}

export function useJPLatexRender(jobProfileId: string) {
  const [state, setState] = useState<RenderState>({
    metadata: null,
    isRendering: false,
    isPolling: false,
    error: null,
    timedOut: false,
  })
  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const retryCountRef = useRef(0)

  const stopPolling = useCallback(() => {
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current)
      pollTimeoutRef.current = null
    }
    setState(s => ({ ...s, isPolling: false }))
  }, [])

  const pollMetadata = useCallback(async () => {
    if (retryCountRef.current >= MAX_RETRIES) {
      stopPolling()
      setState(s => ({ ...s, timedOut: true, isRendering: false }))
      return
    }

    try {
      const meta = await jobProfileApi.getResumeMetadata(jobProfileId)
      setState(s => ({ ...s, metadata: meta }))

      if (TERMINAL_STATES.includes(meta.status)) {
        stopPolling()
        setState(s => ({ ...s, isRendering: false }))
      } else {
        retryCountRef.current += 1
        pollTimeoutRef.current = setTimeout(pollMetadata, POLL_INTERVAL_MS)
      }
    } catch (err) {
      stopPolling()
      setState(s => ({ ...s, isRendering: false, error: err instanceof HttpError ? err.message : 'Render poll failed' }))
    }
  }, [jobProfileId, stopPolling])

  const triggerRender = useCallback(async () => {
    setState(s => ({ ...s, isRendering: true, error: null, timedOut: false }))
    retryCountRef.current = 0
    try {
      const meta = await jobProfileApi.triggerRender(jobProfileId)
      setState(s => ({ ...s, metadata: meta, isPolling: true }))
      pollTimeoutRef.current = setTimeout(pollMetadata, POLL_INTERVAL_MS)
    } catch (err) {
      setState(s => ({ ...s, isRendering: false, error: err instanceof HttpError ? err.message : 'Failed to start render' }))
    }
  }, [jobProfileId, pollMetadata])

  const downloadPdf = useCallback(async () => {
    try {
      const blob = await jobProfileApi.downloadPdf(jobProfileId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `resume-${jobProfileId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Download failed' }))
    }
  }, [jobProfileId])

  const openPdfInTab = useCallback(async () => {
    try {
      const blob = await jobProfileApi.downloadPdf(jobProfileId)
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
      // Revoke after a short delay to allow the tab to load
      setTimeout(() => URL.revokeObjectURL(url), 30_000)
    } catch (err) {
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Failed to open PDF' }))
    }
  }, [jobProfileId])

  useEffect(() => {
    return () => { stopPolling() }
  }, [stopPolling])

  return { ...state, triggerRender, stopPolling, downloadPdf, openPdfInTab }
}
