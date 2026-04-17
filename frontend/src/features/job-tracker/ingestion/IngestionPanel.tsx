import { useEffect } from 'react'
import { useIngestion } from './useIngestion'

export function IngestionPanel() {
  const { isRefreshing, isInFlight, latestDetails, runs, error, refresh, loadRuns } = useIngestion()

  useEffect(() => {
    loadRuns()
  }, [loadRuns])

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem', marginBottom: '1rem' }}>
      <h3>Job Ingestion</h3>

      {/* COMPLIANCE NOTICE — required */}
      <div style={{ background: '#fef9c3', border: '1px solid #fde68a', borderRadius: 4, padding: '0.75rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
        <strong>Important:</strong> This feature does not scrape LinkedIn or any platform that prohibits automated data collection. Only use URLs from platforms that permit it. By using this feature, you confirm compliance with applicable Terms of Service.
      </div>

      {error && <div role="alert" style={{ color: 'red', marginBottom: '0.5rem' }}>{error}</div>}

      {isInFlight && (
        <div style={{ color: '#d97706', marginBottom: '0.5rem' }}>
          An extraction is already in progress. Please wait before starting another.
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <button onClick={refresh} disabled={isRefreshing || isInFlight}>
          {isRefreshing ? 'Starting extraction...' : 'Refresh / Extract New'}
        </button>
        <button onClick={loadRuns} disabled={isRefreshing}>
          Manual Refresh
        </button>
      </div>

      {latestDetails && (
        <div style={{ marginBottom: '1rem', fontSize: '0.875rem' }}>
          <strong>Latest extracted:</strong> {latestDetails.company ?? '—'} — {latestDetails.role ?? '—'}
        </div>
      )}

      {runs.length > 0 && (
        <div>
          <strong>Recent runs:</strong>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '0.5rem' }}>
            {runs.slice(0, 5).map(run => (
              <li key={run.id} style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                {run.status === 'failed' && <span style={{ color: 'red' }}>✗ </span>}
                {run.status === 'completed' && <span style={{ color: 'green' }}>✓ </span>}
                {run.status === 'processing' && <span>⟳ </span>}
                {run.status === 'pending' && <span>◌ </span>}
                <span style={{ fontFamily: 'monospace' }}>{run.url.slice(0, 60)}{run.url.length > 60 ? '…' : ''}</span>
                {run.error_message && <div style={{ color: 'red', marginLeft: '1rem' }}>{run.error_message}</div>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
