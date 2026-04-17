import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useJobOpenings } from './useJobOpenings'
import { StatusHistoryDrawer } from './StatusHistoryDrawer'
import type { OpeningStatus, JobOpening } from '@features/job-tracker/types'

const STATUS_OPTIONS: OpeningStatus[] = ['discovered', 'applied', 'phone_screen', 'interview', 'offer', 'rejected', 'withdrawn']

export function JobTrackerTable() {
  const { openings, isLoading, isSaving, error, hasMore, setFilters, loadMore, create, update, remove, transitionStatus } = useJobOpenings()
  const [historyOpeningId, setHistoryOpeningId] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({ company: '', role: '', url: '' })
  const [filterForm, setFilterForm] = useState({ company: '', role: '', status: '' as OpeningStatus | '' })
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState({ company: '', role: '', url: '' })

  function applyFilters() {
    setFilters({
      company: filterForm.company || undefined,
      role: filterForm.role || undefined,
      status: (filterForm.status || undefined) as OpeningStatus | undefined,
    })
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!createForm.company.trim() || !createForm.role.trim()) return
    try {
      await create({ company: createForm.company.trim(), role: createForm.role.trim(), url: createForm.url || undefined })
      setCreateForm({ company: '', role: '', url: '' })
      setShowCreate(false)
    } catch { /* error shown by hook */ }
  }

  async function handleStatusChange(opening: JobOpening, status: OpeningStatus) {
    try {
      await transitionStatus(opening.id, status)
    } catch { /* error shown by hook */ }
  }

  async function handleUpdate(id: string, e: React.FormEvent) {
    e.preventDefault()
    try {
      await update(id, { company: editForm.company.trim(), role: editForm.role.trim(), url: editForm.url || undefined })
      setEditingId(null)
    } catch { /* error shown by hook */ }
  }

  return (
    <div>
      {/* Filters */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <input placeholder="Company" value={filterForm.company} onChange={e => setFilterForm(f => ({ ...f, company: e.target.value }))} />
        <input placeholder="Role" value={filterForm.role} onChange={e => setFilterForm(f => ({ ...f, role: e.target.value }))} />
        <select value={filterForm.status} onChange={e => setFilterForm(f => ({ ...f, status: e.target.value as OpeningStatus | '' }))}>
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={applyFilters}>Filter</button>
        <button onClick={() => { setFilterForm({ company: '', role: '', status: '' }); setFilters({}) }}>Clear</button>
        <button onClick={() => setShowCreate(s => !s)} style={{ marginLeft: 'auto' }}>+ Add Opening</button>
      </div>

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <input required placeholder="Company" value={createForm.company} onChange={e => setCreateForm(f => ({ ...f, company: e.target.value }))} />
          <input required placeholder="Role" value={createForm.role} onChange={e => setCreateForm(f => ({ ...f, role: e.target.value }))} />
          <input placeholder="URL (optional)" value={createForm.url} onChange={e => setCreateForm(f => ({ ...f, url: e.target.value }))} />
          <button type="submit" disabled={isSaving}>Add</button>
          <button type="button" onClick={() => setShowCreate(false)}>Cancel</button>
        </form>
      )}

      {error && <div role="alert" style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
      {isLoading && openings.length === 0 && <div>Loading...</div>}

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {['Company', 'Role', 'Status', 'URL', 'Added', 'Updated', 'Actions'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '2px solid #e5e7eb' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {openings.map(opening => (
              <>
                <tr key={opening.id}>
                  <td style={{ padding: '0.5rem' }}>{opening.company}</td>
                  <td style={{ padding: '0.5rem' }}>{opening.role}</td>
                  <td style={{ padding: '0.5rem' }}>
                    <select value={opening.status} onChange={e => handleStatusChange(opening, e.target.value as OpeningStatus)} disabled={isSaving}>
                      {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td style={{ padding: '0.5rem' }}>
                    {opening.url ? <a href={opening.url} target="_blank" rel="noreferrer noopener">Link</a> : '—'}
                  </td>
                  <td style={{ padding: '0.5rem', fontSize: '0.875rem' }}>{new Date(opening.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: '0.5rem', fontSize: '0.875rem' }}>{new Date(opening.updated_at).toLocaleDateString()}</td>
                  <td style={{ padding: '0.5rem' }}>
                    <button onClick={() => setHistoryOpeningId(opening.id)}>History</button>
                    {' '}
                    <Link to={`/job-openings/${opening.id}/resume`}>Resume</Link>
                    {' '}
                    <button onClick={() => { setEditingId(opening.id); setEditForm({ company: opening.company, role: opening.role, url: opening.url ?? '' }) }}>Edit</button>
                    {' '}
                    <button onClick={() => {
                      if (window.confirm(`Delete opening at ${opening.company}?`)) {
                        remove(opening.id).catch(() => {})
                      }
                    }} disabled={isSaving}>Delete</button>
                  </td>
                </tr>
                {editingId === opening.id && (
                  <tr key={`${opening.id}-edit`}>
                    <td colSpan={7} style={{ padding: '0.5rem', background: '#f9fafb' }}>
                      <form onSubmit={e => handleUpdate(opening.id, e)} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <input value={editForm.company} onChange={e => setEditForm(f => ({ ...f, company: e.target.value }))} placeholder="Company" required />
                        <input value={editForm.role} onChange={e => setEditForm(f => ({ ...f, role: e.target.value }))} placeholder="Role" required />
                        <input value={editForm.url} onChange={e => setEditForm(f => ({ ...f, url: e.target.value }))} placeholder="URL" />
                        <button type="submit" disabled={isSaving}>Save</button>
                        <button type="button" onClick={() => setEditingId(null)}>Cancel</button>
                      </form>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {hasMore && <button onClick={loadMore} disabled={isLoading} style={{ marginTop: '1rem' }}>Load more</button>}

      {historyOpeningId && (
        <StatusHistoryDrawer openingId={historyOpeningId} onClose={() => setHistoryOpeningId(null)} />
      )}
    </div>
  )
}
