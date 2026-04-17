import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Clock, Loader2, XCircle, Zap } from 'lucide-react'
import { useIngestion } from './useIngestion'

export function IngestionPanel() {
  const { isRefreshing, isInFlight, latestDetails, runs, error, refresh, loadRuns } = useIngestion()
  const [open, setOpen] = useState(false)

  useEffect(() => {
    loadRuns()
  }, [loadRuns])

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
      {/* Header */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-5 py-4 text-left"
        onClick={() => setOpen(o => !o)}
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-sky-500" />
          <span className="font-semibold text-slate-800" style={{ fontFamily: 'Sora, sans-serif' }}>Job Ingestion</span>
        </div>
        {open ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {open && (
        <div className="px-5 pb-5 space-y-4 border-t border-slate-100">
          {/* COMPLIANCE NOTICE — required */}
          <div className="flex gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 mt-4">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0 text-amber-500" />
            <span>
              <strong>Important:</strong> This feature does not scrape LinkedIn or any platform that prohibits automated data collection. Only use URLs from platforms that permit it. By using this feature, you confirm compliance with applicable Terms of Service.
            </span>
          </div>

          {error && (
            <div role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {isInFlight && (
            <div className="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              An extraction is already in progress. Please wait before starting another.
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-2">
            <button
              onClick={refresh}
              disabled={isRefreshing || isInFlight}
              className="px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {isRefreshing ? 'Starting extraction...' : 'Refresh / Extract New'}
            </button>
            <button
              onClick={loadRuns}
              disabled={isRefreshing}
              className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
            >
              Manual Refresh
            </button>
          </div>

          {latestDetails && (
            <div className="text-sm text-slate-600">
              <span className="font-medium text-slate-800">Latest extracted:</span>{' '}
              {latestDetails.company ?? '—'} — {latestDetails.role ?? '—'}
            </div>
          )}

          {runs.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Recent runs</p>
              <ul className="space-y-1">
                {runs.slice(0, 5).map(run => (
                  <li key={run.id} className="flex flex-col gap-0.5 text-sm">
                    <div className="flex items-center gap-2">
                      {run.status === 'failed' && <XCircle className="w-4 h-4 text-red-500 shrink-0" />}
                      {run.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />}
                      {run.status === 'processing' && <Loader2 className="w-4 h-4 text-amber-500 animate-spin shrink-0" />}
                      {run.status === 'pending' && <Clock className="w-4 h-4 text-slate-400 shrink-0" />}
                      <span className="font-mono text-slate-600 truncate">
                        {run.url.slice(0, 60)}{run.url.length > 60 ? '…' : ''}
                      </span>
                    </div>
                    {run.error_message && (
                      <div className="text-red-500 text-xs ml-6">{run.error_message}</div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
