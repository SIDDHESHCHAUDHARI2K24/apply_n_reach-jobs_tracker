'use client'

import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Camera, FileText, FileDown, Loader2, Mail, Printer, Sparkles } from 'lucide-react'
import { useResumeAgent } from '@features/job-tracker/agent/useResumeAgent'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import { useOpeningResume } from '@features/opening-resume/useOpeningResume'
import { useOpeningResumeRender } from '@features/opening-resume/render/useOpeningResumeRender'
import { OPENING_RESUME_REFRESH_EVENT, type OpeningResumeRefreshDetail } from '@features/opening-resume/openingResumeEvents'

const TABS = [
  { label: 'Personal', path: 'personal' },
  { label: 'Education', path: 'education' },
  { label: 'Experience', path: 'experience' },
  { label: 'Projects', path: 'projects' },
  { label: 'Research', path: 'research' },
  { label: 'Certifications', path: 'certifications' },
  { label: 'Skills', path: 'skills' },
]

export function OpeningResumeShell({ openingId, children }: { openingId: string; children: ReactNode }) {
  const pathname = usePathname()
  const {
    resume,
    isLoading,
    isCreating,
    error,
    notFound,
    conflict,
    createResume,
    jobProfiles,
    isLoadingProfiles,
    loadResume,
  } = useOpeningResume(openingId)
  const {
    metadata,
    isRendering,
    error: renderError,
    triggerRender,
    downloadPdf,
    loadMetadata,
  } = useOpeningResumeRender(openingId)
  const {
    agentStatus,
    currentNode,
    errorMessage: tailorError,
    isStarting: isTailorStarting,
    isRunning: isTailorRunning,
    start: startTailor,
  } = useResumeAgent(openingId)
  const [hasJobSnapshot, setHasJobSnapshot] = useState<boolean | null>(null)
  const [selectedProfileId, setSelectedProfileId] = useState('')

  useEffect(() => {
    jobTrackerApi
      .getLatestExtracted(openingId)
      .then(() => setHasJobSnapshot(true))
      .catch(() => setHasJobSnapshot(false))
  }, [openingId])

  async function handleRender() {
    const renderMeta = await triggerRender()
    if (!renderMeta) return
    await loadResume({ silent: true })
    window.dispatchEvent(
      new CustomEvent<OpeningResumeRefreshDetail>(
        OPENING_RESUME_REFRESH_EVENT,
        { detail: { openingId } },
      ),
    )
  }

  if (isLoading) return (
    <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
      Loading resume...
    </div>
  )

  if (error) return (
    <div role="alert" className="m-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center justify-between">
      <span>Error: {error}</span>
      <button
        onClick={() => window.location.reload()}
        className="ml-4 text-red-600 underline hover:no-underline"
      >
        Retry
      </button>
    </div>
  )

  if (notFound && !resume) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-10 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-sky-50 mb-4">
            <FileText size={28} className="text-sky-500" />
          </div>
          <h2 className="font-sora text-xl font-semibold text-slate-800 mb-2">Resume not created yet</h2>
          <p className="text-sm text-slate-500 mb-6 leading-relaxed">
            This resume is an independent snapshot — changes here won&apos;t affect your main profile or job profiles.
          </p>
          {isLoadingProfiles ? (
            <p className="text-sm text-slate-400 mb-4">Loading job profiles...</p>
          ) : jobProfiles.length === 0 ? (
            <p className="text-sm text-slate-400 mb-4">No job profiles yet. Create one first to use as a template.</p>
          ) : (
            <select
              value={selectedProfileId}
              onChange={e => setSelectedProfileId(e.target.value)}
              className="w-full mb-4 px-3 py-2.5 text-sm border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-300 focus:border-sky-400 transition-colors"
            >
              <option value="">Select a job profile as template...</option>
              {jobProfiles.map(jp => (
                <option key={jp.id} value={jp.id}>{jp.title}</option>
              ))}
            </select>
          )}
          <button
            onClick={() => selectedProfileId && createResume(selectedProfileId)}
            disabled={isCreating || !selectedProfileId}
            className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50 w-full"
          >
            {isCreating ? 'Creating...' : 'Create Resume Snapshot'}
          </button>
          {conflict && (
            <p className="mt-3 text-amber-600 text-xs">A resume already exists. Loading it...</p>
          )}
        </div>
      </div>
    )
  }

  const basePath = `/job-openings/${openingId}/resume`

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <nav className="flex items-center gap-1.5 text-sm text-slate-500">
          <Link href="/job-tracker" className="hover:text-sky-600 transition-colors">Job Openings</Link>
          <ChevronRight size={14} className="text-slate-400" />
          <span className="text-slate-700 font-medium">Opening Resume</span>
        </nav>
        <div className="flex items-center gap-2 flex-wrap justify-end">
          {(isTailorRunning || agentStatus === 'running') && currentNode ? (
            <span className="hidden lg:inline-flex text-xs text-violet-700 bg-violet-50 border border-violet-200 px-2 py-0.5 rounded-md max-w-[8rem] truncate" title={currentNode}>
              {currentNode}
            </span>
          ) : null}
          {agentStatus === 'failed' && tailorError ? (
            <span className="hidden sm:inline-flex text-xs text-red-600 max-w-[10rem] truncate" title={tailorError}>{tailorError}</span>
          ) : null}
          <Link
            href={`/job-openings/${openingId}/email-agent`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-lg transition-colors"
          >
            <Mail size={14} />
            Email Agent
          </Link>
          <button
            type="button"
            title={
              hasJobSnapshot !== true
                ? 'Save job details on the opening page first (automatic extraction or manual form).'
                : 'Tailor resume sections and render PDF via AI.'
            }
            disabled={
              hasJobSnapshot !== true
              || isTailorStarting
              || isTailorRunning
              || agentStatus === 'running'
            }
            onClick={() => {
              startTailor({
                onComplete: async outcome => {
                  if (outcome !== 'succeeded') return
                  await loadMetadata()
                  await loadResume({ silent: true })
                  window.dispatchEvent(
                    new CustomEvent<OpeningResumeRefreshDetail>(
                      OPENING_RESUME_REFRESH_EVENT,
                      { detail: { openingId } },
                    ),
                  )
                },
              })
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 border border-violet-300 hover:bg-violet-100 disabled:opacity-50 text-violet-800 text-xs font-medium rounded-lg transition-colors"
          >
            {isTailorStarting || isTailorRunning || agentStatus === 'running' ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Tailoring…
              </>
            ) : (
              <>
                <Sparkles size={14} />
                Tailor Resume
              </>
            )}
          </button>
          {metadata ? (
            <>
              <button
                onClick={downloadPdf}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-sky-500 hover:bg-sky-600 text-white text-xs font-medium rounded-lg transition-colors"
              >
                <FileDown size={14} />
                Download PDF
              </button>
              <button
                onClick={handleRender}
                disabled={isRendering}
                className="flex items-center gap-1.5 px-2 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg transition-colors disabled:opacity-50"
                title="Re-render with latest changes"
              >
                {isRendering ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Printer size={14} />
                )}
              </button>
            </>
          ) : (
            <button
              onClick={handleRender}
              disabled={isRendering}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-600 text-xs font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              {isRendering ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Printer size={14} />
              )}
              {isRendering ? 'Rendering...' : 'Render PDF'}
            </button>
          )}
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-medium">
            <Camera size={10} />
            Snapshot
          </span>
        </div>
      </div>
      {(renderError || metadata?.updated_at) ? (
        <div className="px-1 mb-4">
          {renderError ? (
            <p role="alert" className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-md px-2.5 py-2">
              Render failed: {renderError}
            </p>
          ) : null}
          {metadata?.updated_at ? (
            <p className="text-xs text-slate-500 mt-2">
              Last rendered {new Date(metadata.updated_at).toLocaleString()}
            </p>
          ) : null}
        </div>
      ) : null}

      {/* Tab navigation */}
      <nav className="flex gap-1 border-b border-slate-200 mb-6 overflow-x-auto">
        {TABS.map(tab => {
          const tabPath = `${basePath}/${tab.path}`
          const isActive = pathname.startsWith(tabPath)
          return (
            <Link
              key={tab.path}
              href={tabPath}
              className={[
                'px-3 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors',
                isActive
                  ? 'border-sky-500 text-sky-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
              ].join(' ')}
            >
              {tab.label}
            </Link>
          )
        })}
      </nav>

      {children}
    </div>
  )
}
