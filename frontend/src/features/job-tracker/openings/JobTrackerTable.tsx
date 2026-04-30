'use client'

import { Fragment, useState } from 'react'
import Link from 'next/link'
import { Clock, FileText, Pencil, Trash2 } from 'lucide-react'
import { useJobOpenings } from './useJobOpenings'
import { StatusHistoryDrawer } from './StatusHistoryDrawer'
import type { OpeningStatus, JobOpening } from '@features/job-tracker/types'

const STATUS_OPTIONS: OpeningStatus[] = ['discovered', 'applied', 'phone_screen', 'interview', 'offer', 'rejected', 'withdrawn']

const inputCls = 'px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none'

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
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
      {/* Filter bar */}
      <div className="px-5 py-4 border-b border-slate-100 flex flex-wrap items-center gap-2">
        <input
          className={inputCls}
          placeholder="Company"
          value={filterForm.company}
          onChange={e => setFilterForm(f => ({ ...f, company: e.target.value }))}
        />
        <input
          className={inputCls}
          placeholder="Role"
          value={filterForm.role}
          onChange={e => setFilterForm(f => ({ ...f, role: e.target.value }))}
        />
        <select
          className={inputCls}
          value={filterForm.status}
          onChange={e => setFilterForm(f => ({ ...f, status: e.target.value as OpeningStatus | '' }))}
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button
          onClick={applyFilters}
          className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Filter
        </button>
        <button
          onClick={() => { setFilterForm({ company: '', role: '', status: '' }); setFilters({}) }}
          className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
        >
          Clear
        </button>
        <button
          onClick={() => setShowCreate(s => !s)}
          className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium rounded-lg transition-colors ml-auto"
        >
          + Add Opening
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="px-5 py-4 bg-sky-50 border-b border-sky-100">
          <form onSubmit={handleCreate} className="flex flex-wrap gap-2 items-center">
            <input
              required
              className={inputCls}
              placeholder="Company"
              value={createForm.company}
              onChange={e => setCreateForm(f => ({ ...f, company: e.target.value }))}
            />
            <input
              required
              className={inputCls}
              placeholder="Role"
              value={createForm.role}
              onChange={e => setCreateForm(f => ({ ...f, role: e.target.value }))}
            />
            <input
              className={inputCls}
              placeholder="URL (optional)"
              value={createForm.url}
              onChange={e => setCreateForm(f => ({ ...f, url: e.target.value }))}
            />
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {error && (
        <div role="alert" className="mx-5 mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {error}
        </div>
      )}
      {isLoading && openings.length === 0 && (
        <div className="px-5 py-8 text-center text-slate-500 text-sm">Loading...</div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-slate-50">
              {['Company', 'Role', 'Status', 'URL', 'Added', 'Updated', 'Actions'].map(h => (
                <th
                  key={h}
                  className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide border-b border-slate-200"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {openings.map(opening => (
              <Fragment key={opening.id}>
                <tr className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-slate-800">
                    <Link
                      href={`/job-tracker/${opening.id}`}
                      className="hover:text-sky-600 hover:underline transition-colors"
                    >
                      {opening.company}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-700">{opening.role}</td>
                  <td className="px-4 py-3">
                    <select
                      className="text-xs border border-slate-200 rounded-md px-2 py-1 bg-white focus:ring-1 focus:ring-sky-500 focus:outline-none"
                      value={opening.status}
                      onChange={e => handleStatusChange(opening, e.target.value as OpeningStatus)}
                      disabled={isSaving}
                    >
                      {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {opening.url ? (
                      <a
                        href={opening.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="text-sky-500 hover:text-sky-600 font-medium"
                      >
                        ↗ Link
                      </a>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">{new Date(opening.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-sm text-slate-500">{new Date(opening.updated_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        title="Status History"
                        onClick={() => setHistoryOpeningId(opening.id)}
                        className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      >
                        <Clock className="w-4 h-4" />
                      </button>
                      <Link
                        href={`/job-openings/${opening.id}/resume`}
                        title="Resume"
                        className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      >
                        <FileText className="w-4 h-4" />
                      </Link>
                      <button
                        title="Edit"
                        onClick={() => { setEditingId(opening.id); setEditForm({ company: opening.company, role: opening.role, url: opening.url ?? '' }) }}
                        className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        title="Delete"
                        onClick={() => {
                          if (window.confirm(`Delete opening at ${opening.company}?`)) {
                            remove(opening.id).catch(() => {})
                          }
                        }}
                        disabled={isSaving}
                        className="p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 disabled:opacity-50 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                {editingId === opening.id && (
                  <tr>
                    <td colSpan={7} className="px-4 py-3 bg-sky-50 border-y border-sky-100">
                      <form onSubmit={e => handleUpdate(opening.id, e)} className="flex flex-wrap gap-2 items-center">
                        <input
                          className={inputCls}
                          value={editForm.company}
                          onChange={e => setEditForm(f => ({ ...f, company: e.target.value }))}
                          placeholder="Company"
                          required
                        />
                        <input
                          className={inputCls}
                          value={editForm.role}
                          onChange={e => setEditForm(f => ({ ...f, role: e.target.value }))}
                          placeholder="Role"
                          required
                        />
                        <input
                          className={inputCls}
                          value={editForm.url}
                          onChange={e => setEditForm(f => ({ ...f, url: e.target.value }))}
                          placeholder="URL"
                        />
                        <button
                          type="submit"
                          disabled={isSaving}
                          className="px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          onClick={() => setEditingId(null)}
                          className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
                        >
                          Cancel
                        </button>
                      </form>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {hasMore && (
        <div className="px-5 py-4 border-t border-slate-100">
          <button
            onClick={loadMore}
            disabled={isLoading}
            className="px-4 py-2 border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-50 text-slate-700 text-sm font-medium rounded-lg transition-colors"
          >
            Load more
          </button>
        </div>
      )}

      {historyOpeningId && (
        <StatusHistoryDrawer openingId={historyOpeningId} onClose={() => setHistoryOpeningId(null)} />
      )}
    </div>
  )
}
