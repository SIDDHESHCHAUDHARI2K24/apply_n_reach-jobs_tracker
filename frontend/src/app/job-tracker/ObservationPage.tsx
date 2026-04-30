'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, ExternalLink, FileText } from 'lucide-react'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import type { JobOpening, OpeningStatus, ExtractedDetails } from '@features/job-tracker/types'

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

interface Props {
  openingId: string
}

export default function ObservationPage({ openingId }: Props) {
  const [opening, setOpening] = useState<JobOpening | null>(null)
  const [details, setDetails] = useState<ExtractedDetails | null>(null)
  const [hasResume, setHasResume] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)

    jobTrackerApi
      .get(openingId)
      .then((data) => {
        if (cancelled) return
        setOpening(data)

        // Fetch extracted details (best-effort)
        jobTrackerApi
          .getLatestExtracted(openingId)
          .then((d) => { if (!cancelled) setDetails(d) })
          .catch(() => {})

        // Check if resume exists (best-effort)
        jobTrackerApi
          .getOpeningResume(openingId)
          .then(() => { if (!cancelled) setHasResume(true) })
          .catch(() => {})
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load opening')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

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
            <p className="text-sm text-slate-700 whitespace-pre-wrap">{opening.notes}</p>
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
          </div>
        </div>
      )}
    </div>
  )
}
