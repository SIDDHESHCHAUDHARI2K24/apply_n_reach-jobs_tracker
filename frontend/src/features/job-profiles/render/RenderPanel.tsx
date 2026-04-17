import { useJPLatexRender } from './useJPLatexRender'

interface Props { jobProfileId: string }

export function RenderPanel({ jobProfileId }: Props) {
  const { metadata, isRendering, error, timedOut, triggerRender, downloadPdf, openPdfInTab } = useJPLatexRender(jobProfileId)

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem' }}>
      <h3>Resume</h3>

      {error && <div role="alert" style={{ color: 'red', marginBottom: '0.5rem' }}>{error}</div>}
      {timedOut && (
        <div role="alert" style={{ color: '#d97706', marginBottom: '0.5rem' }}>
          Render is taking longer than expected. Please try again later.
        </div>
      )}

      {metadata && (
        <div style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>
          Status: <strong>{metadata.status}</strong>
          {metadata.error_message && <div style={{ color: 'red' }}>{metadata.error_message}</div>}
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button onClick={triggerRender} disabled={isRendering}>
          {isRendering ? 'Rendering\u2026' : 'Render Resume'}
        </button>

        {metadata?.status === 'completed' && (
          <>
            <button onClick={downloadPdf}>Download PDF</button>
            <button onClick={openPdfInTab}>Open in New Tab</button>
          </>
        )}
      </div>
    </div>
  )
}
