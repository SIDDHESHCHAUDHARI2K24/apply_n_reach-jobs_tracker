'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Camera, FileText } from 'lucide-react'
import { useOpeningResume } from '@features/opening-resume/useOpeningResume'

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
  const { resume, isLoading, isCreating, error, notFound, conflict, createResume } = useOpeningResume(openingId)

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
          <button
            onClick={() => createResume()}
            disabled={isCreating}
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
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-medium">
          <Camera size={10} />
          Snapshot
        </span>
      </div>

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
