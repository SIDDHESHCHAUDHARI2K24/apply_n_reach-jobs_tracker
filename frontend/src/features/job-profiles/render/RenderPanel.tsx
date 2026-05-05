import { FileText, Play, Download, AlertCircle } from 'lucide-react'
import { useJPLatexRender } from './useJPLatexRender'

interface Props { jobProfileId: string }

function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

export function RenderPanel({ jobProfileId }: Props) {
  const { metadata, isRendering, error, timedOut, triggerRender, downloadPdf } = useJPLatexRender(jobProfileId)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <FileText size={16} className="text-slate-400 shrink-0" />
        <h3 className="text-sm font-semibold text-slate-700" style={{ fontFamily: 'var(--font-heading)' }}>Resume Preview</h3>
      </div>

      {/* Error alert */}
      {error && (
        <div role="alert" className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg px-3 py-2">
          <AlertCircle size={14} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Timeout alert */}
      {timedOut && (
        <div role="alert" className="flex items-start gap-2 bg-amber-50 border border-amber-200 text-amber-700 text-xs rounded-lg px-3 py-2">
          <AlertCircle size={14} className="shrink-0 mt-0.5" />
          <span>Render is taking longer than expected. Please try again later.</span>
        </div>
      )}

      {/* Status section */}
      {metadata && (
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span>Status</span>
            <StatusBadge status={metadata.status} />
          </div>
          {metadata.error_message && (
            <p className="text-xs text-red-600">{metadata.error_message}</p>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex flex-col gap-2">
        <button
          onClick={triggerRender}
          disabled={isRendering}
          className="flex items-center justify-center gap-2 w-full px-3 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Play size={14} />
          {isRendering ? 'Rendering…' : 'Render Resume'}
        </button>

        {metadata?.status === 'completed' && (
          <>
            <button
              onClick={downloadPdf}
              className="flex items-center justify-center gap-2 w-full px-3 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
            >
              <Download size={14} />
              Download PDF
            </button>
          </>
        )}
      </div>
    </div>
  )
}
