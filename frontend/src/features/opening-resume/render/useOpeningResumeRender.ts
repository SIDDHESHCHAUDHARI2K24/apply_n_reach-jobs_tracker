import { useState, useCallback, useRef, useEffect } from 'react'
import { openingResumeApi } from '@features/opening-resume/openingResumeApi'
import { HttpError } from '@core/http/client'
import type { OpeningResumeRenderMetadata } from '@features/opening-resume/types'

interface RenderState {
  metadata: OpeningResumeRenderMetadata | null
  isRendering: boolean
  error: string | null
}

export function useOpeningResumeRender(openingId: string) {
  const [state, setState] = useState<RenderState>({
    metadata: null,
    isRendering: false,
    error: null,
  })
  const isRenderingRef = useRef(false)

  const loadMetadata = useCallback(async () => {
    try {
      const meta = await openingResumeApi.getRenderMetadata(openingId)
      setState(s => ({ ...s, metadata: meta, error: null }))
    } catch (err) {
      if (err instanceof HttpError && err.status === 404) {
        setState(s => ({ ...s, metadata: null }))
        return
      }
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Failed to load render metadata' }))
    }
  }, [openingId])

  const triggerRender = useCallback(async (): Promise<OpeningResumeRenderMetadata | null> => {
    if (isRenderingRef.current) return null
    isRenderingRef.current = true
    setState(s => ({ ...s, isRendering: true, error: null }))
    try {
      const meta = await openingResumeApi.triggerRender(openingId)
      setState(s => ({ ...s, metadata: meta, isRendering: false }))
      return meta
    } catch (err) {
      setState(s => ({ ...s, isRendering: false, error: err instanceof HttpError ? err.message : 'Failed to start render' }))
      return null
    } finally {
      isRenderingRef.current = false
    }
  }, [openingId])

  const downloadPdf = useCallback(async () => {
    try {
      const blob = await openingResumeApi.downloadPdf(openingId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `opening-resume-${openingId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setState(s => ({ ...s, error: err instanceof HttpError ? err.message : 'Download failed' }))
    }
  }, [openingId])

  useEffect(() => {
    void loadMetadata()
  }, [loadMetadata])

  return {
    metadata: state.metadata,
    isRendering: state.isRendering,
    error: state.error,
    triggerRender,
    downloadPdf,
    loadMetadata,
  }
}
