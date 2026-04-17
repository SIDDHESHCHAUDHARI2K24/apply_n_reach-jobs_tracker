import React, { useState } from 'react'
import { Globe } from 'lucide-react'
import type { Project } from '@features/user-profile/types'

type FormFields = {
  title: string
  description: string
  technologies: string
  url: string
  start_date: string
  end_date: string
  bullet_points: string
}

function toForm(item?: Project): FormFields {
  return {
    title: item?.title ?? '',
    description: item?.description ?? '',
    technologies: item?.technologies.join('\n') ?? '',
    url: item?.url ?? '',
    start_date: item?.start_date ?? '',
    end_date: item?.end_date ?? '',
    bullet_points: item?.bullet_points.join('\n') ?? '',
  }
}

function fromForm(form: FormFields): Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'> {
  return {
    title: form.title,
    description: form.description || null,
    technologies: form.technologies ? form.technologies.split('\n').filter(l => l.trim()) : [],
    url: form.url || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    bullet_points: form.bullet_points ? form.bullet_points.split('\n').filter(l => l.trim()) : [],
  }
}

interface Props {
  initial?: Project
  isSaving: boolean
  onSave: (data: Omit<Project, 'id' | 'profile_id' | 'created_at' | 'updated_at'>) => Promise<void>
  onCancel: () => void
}

export function ProjectForm({ initial, isSaving, onSave, onCancel }: Props) {
  const [form, setForm] = useState<FormFields>(toForm(initial))

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSave(fromForm(form))
  }

  const fieldClass = 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent'
  const labelClass = 'block text-sm font-medium text-slate-700'

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-2">
      {/* Title */}
      <div className="space-y-1">
        <label className={labelClass}>Title <span className="text-red-500">*</span></label>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          required
          placeholder="e.g. Personal Portfolio Website"
          className={fieldClass}
        />
      </div>

      {/* Description */}
      <div className="space-y-1">
        <label className={labelClass}>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          rows={3}
          placeholder="Brief overview of the project..."
          className={fieldClass}
        />
      </div>

      {/* Technologies */}
      <div className="space-y-1">
        <label className={labelClass}>Technologies <span className="text-xs font-normal text-slate-400">(one per line)</span></label>
        <textarea
          name="technologies"
          value={form.technologies}
          onChange={handleChange}
          rows={3}
          placeholder={"React\nTypeScript\nTailwind CSS"}
          className={fieldClass}
        />
      </div>

      {/* URL */}
      <div className="space-y-1">
        <label className={labelClass}>Project URL</label>
        <div className="relative">
          <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            name="url"
            value={form.url}
            onChange={handleChange}
            placeholder="https://github.com/..."
            className={`${fieldClass} pl-9`}
          />
        </div>
      </div>

      {/* Dates */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className={labelClass}>Start Date</label>
          <input
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            placeholder="YYYY-MM-DD"
            className={fieldClass}
          />
        </div>
        <div className="space-y-1">
          <label className={labelClass}>End Date</label>
          <input
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
            placeholder="YYYY-MM-DD or leave blank"
            className={fieldClass}
          />
        </div>
      </div>

      {/* Bullet Points */}
      <div className="space-y-1">
        <label className={labelClass}>Highlights <span className="text-xs font-normal text-slate-400">(one per line)</span></label>
        <textarea
          name="bullet_points"
          value={form.bullet_points}
          onChange={handleChange}
          rows={4}
          placeholder={"Built RESTful API with FastAPI\nAchieved 95% test coverage"}
          className={fieldClass}
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 pt-1">
        <button
          type="submit"
          disabled={isSaving}
          className="bg-sky-500 hover:bg-sky-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors disabled:opacity-50 text-sm"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="border border-slate-300 text-slate-600 hover:bg-slate-50 px-4 py-2 rounded-lg transition-colors text-sm"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
