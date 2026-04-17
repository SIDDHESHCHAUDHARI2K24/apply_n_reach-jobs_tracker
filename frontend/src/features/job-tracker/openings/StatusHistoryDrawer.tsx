import { useEffect, useState } from 'react'
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
    <div style={{ position: 'fixed', right: 0, top: 0, bottom: 0, width: 320, background: 'white', boxShadow: '-2px 0 8px rgba(0,0,0,0.1)', padding: '1rem', zIndex: 1000 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0 }}>Status History</h3>
        <button onClick={onClose}>×</button>
      </div>
      {error && <div role="alert">{error}</div>}
      {isLoading && <div>Loading...</div>}
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {history.map(entry => (
          <li key={entry.id} style={{ marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid #e5e7eb' }}>
            <div style={{ fontWeight: 600 }}>{entry.status}</div>
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{new Date(entry.changed_at).toLocaleString()}</div>
            {entry.notes && <div style={{ fontSize: '0.875rem' }}>{entry.notes}</div>}
          </li>
        ))}
      </ul>
    </div>
  )
}
