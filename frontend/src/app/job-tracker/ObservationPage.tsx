'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { AlertTriangle, ArrowLeft, ExternalLink, FileText, Loader2, Mail, Sparkles } from 'lucide-react'
import { useResumeAgent } from '@features/job-tracker/agent/useResumeAgent'
import {
  OPENING_RESUME_REFRESH_EVENT,
  type OpeningResumeRefreshDetail,
} from '@features/opening-resume/openingResumeEvents'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import type { ExtractedDetails, ExtractionRun, JobOpening, OpeningStatus } from '@features/job-tracker/types'

const STATUS_OPTIONS: OpeningStatus[] = [
  'discovered',
  'applied',
  'phone_screen',
  'interview',
  'offer',
  'rejected',
  'withdrawn',
]

const STATUS_COLORS: Record<OpeningStatus, string> = {
  discovered: 'bg-slate-100 text-slate-700',
  applied: 'bg-sky-100 text-sky-700',
  phone_screen: 'bg-violet-100 text-violet-700',
  interview: 'bg-amber-100 text-amber-700',
  offer: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-700',
  withdrawn: 'bg-slate-100 text-slate-500',
}

const inputCls =
  'px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none'

const MANUAL_DETAILS_PREFIX = '[MANUAL_JOB_DETAILS]'
const MANUAL_DETAILS_SUFFIX = '[/MANUAL_JOB_DETAILS]'

interface ManualDetails {
  location: string
  description: string
  requirements: string
}

interface ManualNotesPayload {
  baseNotes: string
  manual: ManualDetails
}

function parseManualNotesPayload(notes: string | null): ManualNotesPayload {
  const manual: ManualDetails = {
    location: '',
    description: '',
    requirements: '',
  }
  if (!notes) {
    return { baseNotes: '', manual }
  }
  const startIdx = notes.indexOf(MANUAL_DETAILS_PREFIX)
  const endIdx = notes.indexOf(MANUAL_DETAILS_SUFFIX)
  if (startIdx === -1 || endIdx === -1 || endIdx <= startIdx) {
    return { baseNotes: notes, manual }
  }
  const baseNotes = `${notes.slice(0, startIdx)}${notes.slice(endIdx + MANUAL_DETAILS_SUFFIX.length)}`.trim()
  const payload = notes.slice(startIdx + MANUAL_DETAILS_PREFIX.length, endIdx)
  try {
    const parsed = JSON.parse(payload) as Partial<ManualDetails>
    return {
      baseNotes,
      manual: {
        location: parsed.location ?? '',
        description: parsed.description ?? '',
        requirements: parsed.requirements ?? '',
      },
    }
  } catch {
    return { baseNotes, manual }
  }
}

function buildNotesPayload(baseNotes: string, manual: ManualDetails): string | null {
  const cleanBase = baseNotes.trim()
  const hasManualDetails = Object.values(manual).some(value => value.trim() !== '')
  if (!hasManualDetails) {
    return cleanBase || null
  }
  const serialized = `${MANUAL_DETAILS_PREFIX}${JSON.stringify(manual)}${MANUAL_DETAILS_SUFFIX}`
  return cleanBase ? `${cleanBase}\n\n${serialized}` : serialized
}

interface Props {
  openingId: string
}

export default function ObservationPage({ openingId }: Props) {
  const {
    agentStatus,
    currentNode,
    errorMessage: tailorError,
    isStarting: isTailorStarting,
    isRunning: isTailorRunning,
    start: startTailor,
  } = useResumeAgent(openingId)

  const [opening, setOpening] = useState<JobOpening | null>(null)
  const [details, setDetails] = useState<ExtractedDetails | null>(null)
  const [runs, setRuns] = useState<ExtractionRun[]>([])
  const [hasResume, setHasResume] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)
  const [isManualSaving, setIsManualSaving] = useState(false)
  const [showManualForm, setShowManualForm] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [retryMessage, setRetryMessage] = useState<string | null>(null)
  const [manualMessage, setManualMessage] = useState<string | null>(null)
  const [manualForm, setManualForm] = useState({
    company: '',
    role: '',
    url: '',
    notes: '',
    location: '',
    description: '',
    requirements: '',
  })

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)
    setRetryMessage(null)
    setManualMessage(null)

    async function loadOpeningContext() {
      try {
        const data = await jobTrackerApi.get(openingId)
        if (cancelled) return

        const [detailsResult, runsResult, resumeResult] = await Promise.allSettled([
          jobTrackerApi.getLatestExtracted(openingId),
          jobTrackerApi.getExtractionRuns(openingId),
          jobTrackerApi.getOpeningResume(openingId),
        ])
        if (cancelled) return

        const latestDetails = detailsResult.status === 'fulfilled' ? detailsResult.value : null
        const extractionRuns = runsResult.status === 'fulfilled' ? runsResult.value : []
        const hasExistingResume = resumeResult.status === 'fulfilled'
        const parsed = parseManualNotesPayload(data.notes)

        setOpening(data)
        setDetails(latestDetails)
        setRuns(extractionRuns)
        setHasResume(hasExistingResume)
        setManualForm({
          company: data.company,
          role: data.role,
          url: data.url ?? '',
          notes: parsed.baseNotes,
          location: parsed.manual.location || latestDetails?.location || '',
          description: parsed.manual.description || latestDetails?.raw_text || '',
          requirements: parsed.manual.requirements || (latestDetails?.required_skills ?? []).join('\n'),
        })
      } catch (err: unknown) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load opening')
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadOpeningContext()

    return () => { cancelled = true }
  }, [openingId])

  async function handleStatusChange(e: React.ChangeEvent<HTMLSelectElement>) {
    if (!opening) return
    const newStatus = e.target.value as OpeningStatus
    setStatusError(null)
    setIsSaving(true)
    try {
      const updated = await jobTrackerApi.transitionStatus(opening.id, newStatus)
      setOpening(updated)
    } catch (err: unknown) {
      setStatusError(err instanceof Error ? err.message : 'Failed to update status')
    } finally {
      setIsSaving(false)
    }
  }

  async function handleRetryExtraction() {
    setIsRetrying(true)
    setRetryMessage(null)
    try {
      await jobTrackerApi.refreshExtraction(openingId)
      const refreshedRuns = await jobTrackerApi.getExtractionRuns(openingId)
      setRuns(refreshedRuns)
      setRetryMessage('Extraction queued. Refresh after a few seconds to check the latest details.')
    } catch (err: unknown) {
      setRetryMessage(err instanceof Error ? err.message : 'Failed to queue extraction')
    } finally {
      setIsRetrying(false)
    }
  }

  async function handleManualSave(event: React.FormEvent) {
    event.preventDefault()
    if (!opening) return
    setIsManualSaving(true)
    setManualMessage(null)
    try {
      const notes = buildNotesPayload(manualForm.notes, {
        location: manualForm.location,
        description: manualForm.description,
        requirements: manualForm.requirements,
      })
      const updated = await jobTrackerApi.update(opening.id, {
        company: manualForm.company.trim(),
        role: manualForm.role.trim(),
        url: manualForm.url.trim() || undefined,
        notes: notes ?? undefined,
      })

      try {
        const urlTrim = manualForm.url.trim()
        const requirementsLines = manualForm.requirements.split(/\r?\n/).map(s => s.trim()).filter(Boolean)
        const refreshedDetails = await jobTrackerApi.saveManualExtractedDetails(opening.id, {
          job_title: manualForm.role.trim() || undefined,
          company_name: manualForm.company.trim() || undefined,
          location: manualForm.location.trim() || undefined,
          description_summary: manualForm.description.trim() || undefined,
          required_skills: requirementsLines.length ? requirementsLines : undefined,
          source_url: (urlTrim || updated.url) ?? undefined,
        })
        setDetails(refreshedDetails)

        try {
          const refreshedRuns = await jobTrackerApi.getExtractionRuns(opening.id)
          setRuns(refreshedRuns)
        } catch {
          // non-fatal
        }

        setOpening(updated)
        setManualMessage('Manual job details saved.')
      } catch (snapErr: unknown) {
        setManualMessage(
          snapErr instanceof Error ? snapErr.message : 'Opening saved, but extraction snapshot failed',
        )
        setOpening(updated)
      }
    } catch (err: unknown) {
      setManualMessage(err instanceof Error ? err.message : 'Failed to save manual details')
    } finally {
      setIsManualSaving(false)
    }
  }

  const latestRun = runs[0] ?? null
  const extractionFailed = latestRun?.status === 'failed' && !details
  const extractionInFlight = latestRun?.status === 'pending' || latestRun?.status === 'processing'
  const extractionSummary = details
    ? 'Extracted details available.'
    : extractionInFlight
      ? 'Extraction is currently running.'
      : extractionFailed
        ? 'Latest extraction failed. Add details manually or retry extraction.'
        : 'No extracted details yet.'

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Link href="/job-tracker" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
          <ArrowLeft size={16} /> Back to Job Tracker
        </Link>
        <div className="text-slate-500 text-sm">Loading...</div>
      </div>
    )
  }

  if (error || !opening) {
    return (
      <div className="space-y-6">
        <Link href="/job-tracker" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
          <ArrowLeft size={16} /> Back to Job Tracker
        </Link>
        <div role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error ?? 'Opening not found'}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Back */}
      <Link
        href="/job-tracker"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors"
      >
        <ArrowLeft size={16} /> Back to Job Tracker
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-sora text-2xl font-bold text-slate-900">{opening.company}</h1>
          <p className="text-slate-500 mt-0.5">{opening.role}</p>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <div className="flex items-center gap-2">
            {(isTailorRunning || agentStatus === 'running') && currentNode ? (
              <span className="hidden sm:inline-flex text-xs text-violet-700 bg-violet-50 border border-violet-200 px-2 py-1 rounded-md max-w-[10rem] truncate" title={currentNode ?? ''}>
                {currentNode}
              </span>
            ) : null}
            {(agentStatus === 'failed' && tailorError != null && tailorError !== '') ? (
              <span className="hidden md:inline-flex text-xs text-red-600 max-w-[14rem] truncate" title={tailorError}>{tailorError}</span>
            ) : null}
            <button
              type="button"
              title={
                details
                  ? 'Run AI resume tailoring for this opening.'
                  : 'Save extraction results or manual job details first.'
              }
              disabled={!details || isTailorStarting || isTailorRunning || agentStatus === 'running'}
              onClick={() => {
                startTailor({
                  onComplete: async () => {
                    try {
                      const [o2, hr] = await Promise.all([
                        jobTrackerApi.get(openingId),
                        jobTrackerApi.getOpeningResume(openingId).then(() => true).catch(() => false),
                      ])
                      setOpening(o2)
                      setHasResume(hr)
                      window.dispatchEvent(
                        new CustomEvent<OpeningResumeRefreshDetail>(
                          OPENING_RESUME_REFRESH_EVENT,
                          { detail: { openingId } },
                        ),
                      )
                    } catch {
                      //
                    }
                  },
                })
              }}
              className="inline-flex items-center gap-1.5 px-4 py-2 border border-violet-300 bg-violet-50 hover:bg-violet-100 disabled:opacity-50 text-violet-800 text-sm font-medium rounded-lg transition-colors"
            >
              {isTailorStarting || isTailorRunning || agentStatus === 'running' ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Tailoring…
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Tailor Resume
                </>
              )}
            </button>
          </div>
          <Link
            href={`/job-openings/${opening.id}/email-agent`}
            className="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
          >
            <Mail size={16} />
            Email Agent
          </Link>
          {hasResume && (
            <Link
              href={`/job-openings/${opening.id}/resume`}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <FileText size={16} />
              View Resume
            </Link>
          )}
        </div>
      </div>

      {/* Extraction status */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm px-6 py-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Extraction Status</p>
        <p className="text-sm text-slate-700">{extractionSummary}</p>
        {latestRun?.error_message && (
          <p className="text-xs text-red-600 mt-1">{latestRun.error_message}</p>
        )}
      </div>

      {extractionFailed && (
        <div className="flex flex-col gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 mt-0.5 text-amber-500 shrink-0" />
            <p className="text-sm text-amber-900">
              We could not extract details from the source URL. Add details manually below or retry extraction.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowManualForm(true)}
              className="px-3 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm rounded-lg"
            >
              Add details manually
            </button>
            <button
              type="button"
              onClick={handleRetryExtraction}
              disabled={isRetrying}
              className="px-3 py-2 border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 text-sm rounded-lg"
            >
              {isRetrying ? 'Queuing...' : 'Retry extraction'}
            </button>
          </div>
          {retryMessage && <p className="text-xs text-slate-600">{retryMessage}</p>}
        </div>
      )}

      {/* Details card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-100">
        {/* Status row */}
        <div className="px-6 py-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Status</p>
            <span
              className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_COLORS[opening.status]}`}
            >
              {opening.status.replace('_', ' ')}
            </span>
          </div>
          <div className="flex flex-col items-end gap-1">
            <label htmlFor="status-select" className="text-xs text-slate-400">
              Change status
            </label>
            <select
              id="status-select"
              value={opening.status}
              onChange={handleStatusChange}
              disabled={isSaving}
              className={inputCls + ' disabled:opacity-50'}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
            {statusError && (
              <p className="text-xs text-red-600">{statusError}</p>
            )}
          </div>
        </div>

        {/* URL */}
        <div className="px-6 py-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Job URL</p>
          {opening.url ? (
            <a
              href={opening.url}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-1 text-sky-600 hover:text-sky-700 text-sm font-medium break-all"
            >
              <ExternalLink size={14} className="shrink-0" />
              {opening.url}
            </a>
          ) : (
            <span className="text-slate-400 text-sm">No URL provided</span>
          )}
        </div>

        {/* Dates */}
        <div className="px-6 py-4 grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Added</p>
            <p className="text-sm text-slate-700">
              {opening.created_at
                ? new Date(opening.created_at).toLocaleString()
                : '—'}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Last Updated</p>
            <p className="text-sm text-slate-700">
              {opening.updated_at
                ? new Date(opening.updated_at).toLocaleString()
                : '—'}
            </p>
          </div>
        </div>

        {/* Notes */}
        {opening.notes && (
          <div className="px-6 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Notes</p>
            <p className="text-sm text-slate-700 whitespace-pre-wrap">
              {parseManualNotesPayload(opening.notes).baseNotes || '—'}
            </p>
          </div>
        )}
      </div>

      {/* Extracted details */}
      {details && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-700">Extracted Job Details</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Extracted on {new Date(details.created_at).toLocaleString()}
            </p>
          </div>
          <div className="px-6 py-4 space-y-3">
            {details.company && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-0.5">Company (extracted)</p>
                <p className="text-sm text-slate-700">{details.company}</p>
              </div>
            )}
            {details.role && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-0.5">Role (extracted)</p>
                <p className="text-sm text-slate-700">{details.role}</p>
              </div>
            )}
            {details.raw_text && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-0.5">Description Summary</p>
                <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{details.raw_text}</p>
              </div>
            )}
            {details.required_skills.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-0.5">Requirements</p>
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{details.required_skills.join('\n')}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {(showManualForm || extractionFailed) && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="px-6 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-700">Manual Job Details</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Use this form when extraction is incomplete or failed. These fields are saved to the opening record.
            </p>
          </div>
          <form onSubmit={handleManualSave} className="px-6 py-4 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                className={inputCls}
                value={manualForm.company}
                onChange={event => setManualForm(s => ({ ...s, company: event.target.value }))}
                placeholder="Company"
                required
              />
              <input
                className={inputCls}
                value={manualForm.role}
                onChange={event => setManualForm(s => ({ ...s, role: event.target.value }))}
                placeholder="Role title"
                required
              />
              <input
                className={inputCls}
                value={manualForm.location}
                onChange={event => setManualForm(s => ({ ...s, location: event.target.value }))}
                placeholder="Location"
              />
            </div>
            <input
              className={inputCls}
              value={manualForm.url}
              onChange={event => setManualForm(s => ({ ...s, url: event.target.value }))}
              placeholder="Job URL"
            />
            <textarea
              className={inputCls + ' min-h-24 w-full'}
              value={manualForm.description}
              onChange={event => setManualForm(s => ({ ...s, description: event.target.value }))}
              placeholder="Description"
            />
            <textarea
              className={inputCls + ' min-h-24 w-full'}
              value={manualForm.requirements}
              onChange={event => setManualForm(s => ({ ...s, requirements: event.target.value }))}
              placeholder="Requirements (one per line)"
            />
            <textarea
              className={inputCls + ' min-h-20 w-full'}
              value={manualForm.notes}
              onChange={event => setManualForm(s => ({ ...s, notes: event.target.value }))}
              placeholder="Additional notes"
            />
            <div className="flex items-center gap-2">
              <button
                type="submit"
                disabled={isManualSaving}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
              >
                {isManualSaving ? <Loader2 size={14} className="animate-spin" /> : null}
                Save manual details
              </button>
              {!extractionFailed && (
                <button
                  type="button"
                  onClick={() => setShowManualForm(false)}
                  className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
                >
                  Hide
                </button>
              )}
            </div>
            {manualMessage && (
              <p className={`text-xs ${manualMessage.includes('saved') ? 'text-green-600' : 'text-red-600'}`}>
                {manualMessage}
              </p>
            )}
          </form>
        </div>
      )}
    </div>
  )
}
