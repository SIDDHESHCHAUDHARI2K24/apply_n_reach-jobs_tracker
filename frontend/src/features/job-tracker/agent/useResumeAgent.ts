'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { HttpError } from '@core/http/client'
import { jobTrackerApi } from '../jobTrackerApi'
import type { EmailAgentStatusResponse } from '../types'

const POLL_MS = 2000
const TERMINAL_AGENT = new Set(['succeeded', 'failed'])

export type ResumeAgentStartOptions = {
  /** Called once when tailoring finishes (`succeeded` or `failed`). */
  onComplete?: (outcome: 'succeeded' | 'failed') => void
}

/** Poll `/job-openings/:id/agent/status` after POST `/agent/run`. */
export function useResumeAgent(openingId: string) {
  const [agentStatus, setAgentStatus] = useState<
    EmailAgentStatusResponse['agent_status'] | string
  >('idle')
  const [currentNode, setCurrentNode] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isStarting, setIsStarting] = useState(false)
  const [isRunning, setIsRunning] = useState(false)

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const onCompleteRef = useRef<ResumeAgentStartOptions['onComplete'] | null>(null)
  const openingIdRef = useRef(openingId)
  openingIdRef.current = openingId

  const clearPolling = useCallback(() => {
    if (intervalRef.current != null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  useEffect(() => () => clearPolling(), [clearPolling])

  const applyStatus = useCallback(
    (st: EmailAgentStatusResponse) => {
      setAgentStatus(st.agent_status)
      setCurrentNode(st.current_node)
      setErrorMessage(st.error_message)
      setIsRunning(st.agent_status === 'running')

      if (TERMINAL_AGENT.has(st.agent_status)) {
        clearPolling()
        const cb = onCompleteRef.current
        onCompleteRef.current = null
        if (cb) {
          cb(st.agent_status as 'succeeded' | 'failed')
        }
      }
    },
    [clearPolling],
  )

  const pollOnce = useCallback(async () => {
    const oid = openingIdRef.current
    try {
      const st = await jobTrackerApi.getResumeAgentStatus(oid)
      applyStatus(st)
    } catch (e) {
      clearPolling()
      setIsRunning(false)
      const msg =
        e instanceof HttpError ? e.message : e instanceof Error ? e.message : 'Status request failed'
      setErrorMessage(msg)
      setAgentStatus('failed')
      const cb = onCompleteRef.current
      onCompleteRef.current = null
      if (cb) cb('failed')
    }
  }, [applyStatus, clearPolling])

  const beginPollingIfRunning = useCallback(() => {
    if (intervalRef.current != null) return
    intervalRef.current = setInterval(() => void pollOnce(), POLL_MS)
  }, [pollOnce])

  /** Initial sync + polling if backend already marks this opening as running. */
  useEffect(() => {
    clearPolling()
    let cancelled = false
    ;(async () => {
      try {
        const st = await jobTrackerApi.getResumeAgentStatus(openingId)
        if (cancelled) return
        applyStatus(st)
        if (st.agent_status === 'running') beginPollingIfRunning()
      } catch {
        // ignore bootstrap errors (e.g. network)
      }
    })()
    return () => {
      cancelled = true
      clearPolling()
    }
  }, [openingId, applyStatus, beginPollingIfRunning, clearPolling])

  const refreshStatus = useCallback(async () => {
    try {
      const st = await jobTrackerApi.getResumeAgentStatus(openingIdRef.current)
      applyStatus(st)
      if (st.agent_status === 'running') beginPollingIfRunning()
    } catch {
      //
    }
  }, [applyStatus, beginPollingIfRunning])

  const start = useCallback(
    async (opts?: ResumeAgentStartOptions) => {
      clearPolling()
      onCompleteRef.current = opts?.onComplete ?? null
      setIsStarting(true)
      setErrorMessage(null)
      try {
        await jobTrackerApi.startResumeAgent(openingIdRef.current)
        const st = await jobTrackerApi.getResumeAgentStatus(openingIdRef.current)
        applyStatus(st)
        if (st.agent_status === 'running') beginPollingIfRunning()
      } catch (e) {
        const msg =
          e instanceof HttpError
            ? e.message
            : e instanceof Error
              ? e.message
              : 'Failed to start tailoring'
        setErrorMessage(msg)
        setIsRunning(false)
        onCompleteRef.current = null
      } finally {
        setIsStarting(false)
      }
    },
    [applyStatus, beginPollingIfRunning, clearPolling],
  )

  return {
    agentStatus,
    currentNode,
    errorMessage,
    isStarting,
    isRunning,
    start,
    refreshStatus,
  }
}
