import { useState, useCallback, useRef, useEffect } from 'react'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'
import type { ResumeMetadata } from '@features/job-profiles/types'

interface RenderState {
  metadata: ResumeMetadata | null
  isRendering: boolean
  error: string | null
  timedOut: boolean
}

export function useJPLatexRender(jobProfileId: string) {
  const [state, setState] = useState<RenderState>({
    metadata: null,
    isRendering: false,
    error: null,
    timedOut: false,
  })
  const isRenderingRef = useRef(false)

  const stopPolling = useCallback(() => {
    // Manual job-profile render is synchronous; kept for API compatibility with RenderPanel.
    return
  }, [])

  const loadMetadata = useCallback(async () => {
    try {
      const meta = await jobProfileApi.getResumeMetadata(jobProfileId)
      setState(s => ({ ...s, metadata: meta, error: null }))
    } catch (err) {
      if (err instanceof HttpError && err.status === 404) {
        setState(s => ({ ...s, metadata: null }))
        return
      }
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Failed to load render metadata' }))
    }
  }, [jobProfileId])

  const triggerRender = useCallback(async () => {
    if (isRenderingRef.current) {
      return
    }

    isRenderingRef.current = true
    setState(s => ({ ...s, isRendering: true, error: null, timedOut: false }))
    try {
      const meta = await jobProfileApi.triggerRender(jobProfileId)
      setState(s => ({ ...s, metadata: meta, isRendering: false }))
    } catch (err) {
      setState(s => ({ ...s, isRendering: false, error: err instanceof HttpError ? err.message : 'Failed to start render' }))
    } finally {
      isRenderingRef.current = false
    }
  }, [jobProfileId])

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
    void loadMetadata()
  }, [loadMetadata])

  return { ...state, triggerRender, stopPolling, downloadPdf, openPdfInTab }
}
