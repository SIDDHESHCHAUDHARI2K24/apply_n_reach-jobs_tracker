import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { jobTrackerApi } from '@features/job-tracker/jobTrackerApi'
import type { StatusHistoryEntry } from '@features/job-tracker/types'

interface Props {
  openingId: string
  onClose: () => void
}

export function StatusHistoryDrawer({ openingId, onClose }: Props) {
  const [history, setHistory] = useState<StatusHistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    jobTrackerApi.getStatusHistory(openingId)
      .then(h => { if (!cancelled) { setHistory(h); setIsLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err instanceof Error ? err.message : 'Failed to load'); setIsLoading(false) } })
    return () => { cancelled = true }
  }, [openingId])

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 z-40" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 w-80 bg-white shadow-2xl border-l border-slate-200 z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800" style={{ fontFamily: 'Sora, sans-serif' }}>Status History</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {error && <div role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-4">{error}</div>}
          {isLoading && <div className="text-sm text-slate-500">Loading…</div>}

          <ul className="space-y-0">
            {history.map((entry, idx) => (
              <li key={entry.id} className="relative flex gap-3 pb-4">
                {/* Timeline line */}
                {idx < history.length - 1 && (
                  <div className="absolute left-[7px] top-4 bottom-0 w-px bg-slate-200" />
                )}
                {/* Dot */}
                <div className="mt-1 w-3.5 h-3.5 rounded-full bg-sky-100 border-2 border-sky-400 shrink-0" />
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <span className={`badge badge-${entry.status}`}>{entry.status}</span>
                  <div className="text-xs text-slate-400 mt-1">{new Date(entry.changed_at).toLocaleString()}</div>
                  {entry.notes && <div className="text-sm text-slate-600 mt-1">{entry.notes}</div>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  )
}
