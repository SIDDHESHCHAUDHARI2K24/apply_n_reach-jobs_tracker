'use client'

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Loader2, Mail, Play, RefreshCw } from 'lucide-react'
import { HttpError } from '@core/http/client'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import type {
  EmailAgentEvent,
  EmailAgentOutputResponse,
  EmailAgentRunListItem,
  EmailAgentStatusResponse,
  JobOpening,
} from '@features/job-tracker/types'

interface Props {
  openingId: string
}

function isTerminalStatus(status: string | undefined): boolean {
  return status === 'succeeded' || status === 'failed' || status === 'cancelled' || status === 'timeout'
}

export default function EmailAgentPage({ openingId }: Props) {
  const [opening, setOpening] = useState<JobOpening | null>(null)
  const [status, setStatus] = useState<EmailAgentStatusResponse | null>(null)
  const [runs, setRuns] = useState<EmailAgentRunListItem[]>([])
  const [output, setOutput] = useState<EmailAgentOutputResponse | null>(null)
  const [streamEvents, setStreamEvents] = useState<EmailAgentEvent[]>([])
  const [recipientType, setRecipientType] = useState('recruiter')
  const [rawJd, setRawJd] = useState('')
  const [rawResume, setRawResume] = useState('')
  const [resumeEdits, setResumeEdits] = useState('[\n  {\n    "field": "subject_lines[0]",\n    "value": "Refined subject line"\n  }\n]')
  const [isLoading, setIsLoading] = useState(true)
  const [isStarting, setIsStarting] = useState(false)
  const [isResuming, setIsResuming] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [streamState, setStreamState] = useState<'idle' | 'connected' | 'error'>('idle')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const eventSourceRef = useRef<EventSource | null>(null)

  const closeStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }, [])

  const loadOutput = useCallback(async () => {
    try {
      const latestOutput = await jobTrackerApi.getEmailAgentOutput(openingId)
      setOutput(latestOutput)
    } catch (err: unknown) {
      if (err instanceof HttpError && err.status === 404) {
        setOutput(null)
        return
      }
      throw err
    }
  }, [openingId])

  const refreshAgentState = useCallback(async () => {
    const [statusResult, runsResult] = await Promise.all([
      jobTrackerApi.getEmailAgentStatus(openingId),
      jobTrackerApi.getEmailAgentRuns(openingId),
    ])
    setStatus(statusResult)
    setRuns(runsResult)
    if (statusResult.agent_status === 'succeeded') {
      await loadOutput()
    } else {
      setOutput(null)
    }
  }, [loadOutput, openingId])

  const connectStream = useCallback(() => {
    closeStream()
    const es = new EventSource(jobTrackerApi.getEmailAgentStreamUrl(openingId), { withCredentials: true })
    eventSourceRef.current = es
    setStreamState('connected')

    es.onmessage = event => {
      try {
        const parsed = JSON.parse(event.data) as EmailAgentEvent
        setStreamEvents(prev => [...prev, parsed])
      } catch {
        setStreamEvents(prev => [...prev, { message: event.data }])
      }
    }

    es.onerror = () => {
      setStreamState('error')
      closeStream()
    }
  }, [closeStream, openingId])

  useEffect(() => {
    let cancelled = false

    async function loadPage() {
      setIsLoading(true)
      setError(null)
      try {
        const openingData = await jobTrackerApi.get(openingId)
        if (cancelled) return
        setOpening(openingData)
        await refreshAgentState()
      } catch (err: unknown) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load Email Agent page')
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadPage()

    return () => {
      cancelled = true
      closeStream()
    }
  }, [closeStream, openingId, refreshAgentState])

  useEffect(() => {
    if (status?.agent_status === 'running') {
      connectStream()
      return () => closeStream()
    }
    closeStream()
    setStreamState('idle')
    return undefined
  }, [closeStream, connectStream, status?.agent_status])

  useEffect(() => {
    if (!status || isTerminalStatus(status.agent_status) || status.agent_status === 'idle') {
      return undefined
    }
    const intervalId = window.setInterval(() => {
      refreshAgentState().catch(() => {})
    }, 4000)
    return () => window.clearInterval(intervalId)
  }, [refreshAgentState, status])

  const timelineEvents = useMemo(
    () => [...(status?.events ?? []), ...streamEvents].slice(-30),
    [status?.events, streamEvents],
  )

  async function handleStart(event: FormEvent) {
    event.preventDefault()
    setIsStarting(true)
    setError(null)
    setMessage(null)
    setStreamEvents([])
    try {
      const result = await jobTrackerApi.startEmailAgentRun(openingId, {
        recipient_type: recipientType,
        raw_jd: rawJd.trim() || undefined,
        raw_resume: rawResume.trim() || undefined,
      })
      setMessage(result.message)
      await refreshAgentState()
      connectStream()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start email agent')
    } finally {
      setIsStarting(false)
    }
  }

  async function handleResume(event: FormEvent) {
    event.preventDefault()
    setIsResuming(true)
    setError(null)
    setMessage(null)
    try {
      const parsed = JSON.parse(resumeEdits)
      if (!Array.isArray(parsed)) {
        throw new Error('Resume edits must be a JSON array')
      }
      const result = await jobTrackerApi.resumeEmailAgent(openingId, { user_edits: parsed })
      setMessage(result.message)
      await refreshAgentState()
      connectStream()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to resume email agent')
    } finally {
      setIsResuming(false)
    }
  }

  async function handleRefresh() {
    setIsRefreshing(true)
    try {
      await refreshAgentState()
      setMessage('Status refreshed')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to refresh status')
    } finally {
      setIsRefreshing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Link href={`/job-openings/${openingId}`} className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
          <ArrowLeft size={16} /> Back to Observation
        </Link>
        <div className="text-slate-500 text-sm">Loading email agent...</div>
      </div>
    )
  }

  if (error && !opening) {
    return (
      <div className="space-y-6">
        <Link href={`/job-openings/${openingId}`} className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
          <ArrowLeft size={16} /> Back to Observation
        </Link>
        <div role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <Link href={`/job-openings/${openingId}`} className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors">
        <ArrowLeft size={16} /> Back to Observation
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-sora text-2xl font-bold text-slate-900">Email Agent</h1>
          <p className="text-slate-500 mt-0.5">{opening?.company} · {opening?.role}</p>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 text-sm font-medium rounded-lg transition-colors"
        >
          {isRefreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Refresh
        </button>
      </div>

      {(message || error) && (
        <div className={`text-sm rounded-lg px-4 py-3 border ${error ? 'text-red-700 border-red-200 bg-red-50' : 'text-emerald-700 border-emerald-200 bg-emerald-50'}`}>
          {error ?? message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4 space-y-4">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Run new outreach</p>
            <p className="text-sm text-slate-600 mt-1">Start the agent with optional JD/resume overrides.</p>
          </div>
          <form className="space-y-3" onSubmit={handleStart}>
            <label className="block text-xs text-slate-500">
              Recipient type
              <select
                value={recipientType}
                onChange={e => setRecipientType(e.target.value)}
                className="mt-1 w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                <option value="recruiter">Recruiter</option>
                <option value="hiring_manager">Hiring Manager</option>
                <option value="referral">Referral</option>
              </select>
            </label>
            <label className="block text-xs text-slate-500">
              Raw JD override (optional)
              <textarea
                value={rawJd}
                onChange={e => setRawJd(e.target.value)}
                className="mt-1 min-h-24 w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </label>
            <label className="block text-xs text-slate-500">
              Raw resume override (optional)
              <textarea
                value={rawResume}
                onChange={e => setRawResume(e.target.value)}
                className="mt-1 min-h-24 w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </label>
            <button
              type="submit"
              disabled={isStarting}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {isStarting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {isStarting ? 'Starting...' : 'Start Email Agent'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4 space-y-3">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Current status</p>
          <div className="text-sm text-slate-700 space-y-1">
            <p><span className="text-slate-500">Run:</span> {status?.run_id ?? '—'}</p>
            <p><span className="text-slate-500">Agent status:</span> {status?.agent_status ?? 'idle'}</p>
            <p><span className="text-slate-500">Current node:</span> {status?.current_node ?? '—'}</p>
            <p><span className="text-slate-500">Stream:</span> {streamState}</p>
            <p><span className="text-slate-500">Started:</span> {status?.started_at ? new Date(status.started_at).toLocaleString() : '—'}</p>
            <p><span className="text-slate-500">Completed:</span> {status?.completed_at ? new Date(status.completed_at).toLocaleString() : '—'}</p>
          </div>
          {status?.error_message && (
            <p className="text-xs text-red-600">{status.error_message}</p>
          )}
          {status?.agent_status === 'paused' && (
            <form onSubmit={handleResume} className="space-y-2 pt-2 border-t border-slate-100">
              <p className="text-xs text-slate-500">Run is paused. Submit JSON user edits to resume.</p>
              <textarea
                value={resumeEdits}
                onChange={e => setResumeEdits(e.target.value)}
                className="min-h-28 w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
              <button
                type="submit"
                disabled={isResuming}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
              >
                {isResuming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                {isResuming ? 'Resuming...' : 'Resume Run'}
              </button>
            </form>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Live event timeline</p>
        {timelineEvents.length === 0 ? (
          <p className="text-sm text-slate-500">No events yet.</p>
        ) : (
          <ul className="space-y-2">
            {timelineEvents.map((evt, index) => (
              <li key={`${index}-${String(evt.node ?? 'event')}`} className="text-sm border border-slate-100 rounded-lg px-3 py-2">
                <div className="font-medium text-slate-700">{String(evt.node ?? 'agent')} · {String(evt.status ?? 'update')}</div>
                <div className="text-slate-600 text-xs mt-1 whitespace-pre-wrap">{String(evt.message ?? JSON.stringify(evt))}</div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Run history</p>
        {runs.length === 0 ? (
          <p className="text-sm text-slate-500">No runs found for this opening.</p>
        ) : (
          <ul className="space-y-2">
            {runs.map(run => (
              <li key={run.id} className="text-sm border border-slate-100 rounded-lg px-3 py-2">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <span className="font-medium text-slate-700">Run #{run.id}</span>
                  <span className="text-slate-500">status: {run.status}</span>
                  <span className="text-slate-500">node: {run.current_node ?? '—'}</span>
                  <span className="text-slate-400">created: {new Date(run.created_at).toLocaleString()}</span>
                </div>
                {run.error_message && (
                  <p className="text-xs text-red-600 mt-1">{run.error_message}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-5 py-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Latest succeeded output</p>
        {!output ? (
          <p className="text-sm text-slate-500">No completed output available yet.</p>
        ) : (
          <div className="space-y-3 text-sm">
            <p><span className="text-slate-500">Outreach status:</span> {output.outreach_status ?? '—'}</p>
            <details className="border border-slate-100 rounded-lg px-3 py-2">
              <summary className="cursor-pointer font-medium text-slate-700">Generated emails ({output.generated_emails.length})</summary>
              <pre className="text-xs text-slate-600 mt-2 whitespace-pre-wrap">{JSON.stringify(output.generated_emails, null, 2)}</pre>
            </details>
            <details className="border border-slate-100 rounded-lg px-3 py-2">
              <summary className="cursor-pointer font-medium text-slate-700">Subject lines ({output.subject_lines.length})</summary>
              <pre className="text-xs text-slate-600 mt-2 whitespace-pre-wrap">{JSON.stringify(output.subject_lines, null, 2)}</pre>
            </details>
            <details className="border border-slate-100 rounded-lg px-3 py-2">
              <summary className="cursor-pointer font-medium text-slate-700">Follow-up drafts ({output.followup_drafts.length})</summary>
              <pre className="text-xs text-slate-600 mt-2 whitespace-pre-wrap">{JSON.stringify(output.followup_drafts, null, 2)}</pre>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}
