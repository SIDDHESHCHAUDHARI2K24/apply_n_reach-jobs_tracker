import { useState, useEffect } from 'react'
import { Download, AlertCircle, CheckCircle } from 'lucide-react'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

interface Props {
  jobProfileId: string
  section: string
}

// Helper: render a styled summary of section data
function SectionSummary({ section, data }: { section: string; data: unknown }) {
  if (data === null || data === undefined) {
    return <p className="text-sm text-slate-400">No data available.</p>
  }

  if (section === 'personal') {
    const p = data as Record<string, unknown>
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
        {!!p.full_name && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Name</span>
            <p className="text-sm text-slate-800">{String(p.full_name)}</p>
          </div>
        )}
        {!!p.email && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Email</span>
            <p className="text-sm text-slate-800">{String(p.email)}</p>
          </div>
        )}
        {!!p.phone && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Phone</span>
            <p className="text-sm text-slate-800">{String(p.phone)}</p>
          </div>
        )}
        {!!p.location && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Location</span>
            <p className="text-sm text-slate-800">{String(p.location)}</p>
          </div>
        )}
        {!!p.linkedin_url && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">LinkedIn</span>
            <p className="text-sm text-slate-800">
              <a href={String(p.linkedin_url)} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline">
                {String(p.linkedin_url)}
              </a>
            </p>
          </div>
        )}
        {!!p.github_url && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">GitHub</span>
            <p className="text-sm text-slate-800">
              <a href={String(p.github_url)} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline">
                {String(p.github_url)}
              </a>
            </p>
          </div>
        )}
        {!!p.portfolio_url && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Portfolio</span>
            <p className="text-sm text-slate-800">
              <a href={String(p.portfolio_url)} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline">
                {String(p.portfolio_url)}
              </a>
            </p>
          </div>
        )}
        {!!p.summary && (
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Summary</span>
            <p className="text-sm text-slate-800">{String(p.summary)}</p>
          </div>
        )}
        {!p.full_name && !p.email && !p.phone && !p.location && !p.linkedin_url && !p.github_url && !p.portfolio_url && !p.summary && (
          <p className="text-sm text-slate-400">No personal details saved yet.</p>
        )}
      </div>
    )
  }

  if (section === 'skills' && typeof data === 'object' && data !== null) {
    const list = Array.isArray((data as { skills?: unknown }).skills)
      ? ((data as { skills: unknown[] }).skills.filter(item => typeof item === 'string') as string[])
      : []
    return (
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">
          {list.length} item{list.length !== 1 ? 's' : ''}
        </p>
        {list.length === 0 ? (
          <p className="text-sm text-slate-400">No items yet. Import from your user profile to get started.</p>
        ) : (
          <div className="space-y-2">
            {list.slice(0, 8).map((skill, idx) => (
              <div key={`${skill}-${idx}`} className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3">
                <p className="text-sm font-medium text-slate-800">{skill}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  // Array sections
  if (Array.isArray(data)) {
    const items = data as Array<Record<string, unknown>>
    const preview = items.slice(0, 3)
    const labelKey = section === 'education'
      ? 'degree'
      : section === 'experience'
      ? 'company'
      : section === 'skills'
      ? 'category'
      : 'title'

    return (
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">
          {items.length} item{items.length !== 1 ? 's' : ''}
        </p>
        {preview.length === 0 ? (
          <p className="text-sm text-slate-400">No items yet. Import from your user profile to get started.</p>
        ) : (
          <div className="space-y-2">
            {preview.map((item, idx) => {
              const primary = String(item[labelKey] ?? item.title ?? item.name ?? 'Untitled')
              const secondaryRaw = section === 'education'
                ? item.institution
                : section === 'experience'
                ? item.role
                : item.description ?? item.summary ?? item.proficiency ?? null
              const secondary = secondaryRaw != null ? String(secondaryRaw) : null
              return (
                <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3">
                  <p className="text-sm font-medium text-slate-800">{primary}</p>
                  {secondary && (
                    <p className="text-xs text-slate-500 mt-0.5 truncate">{secondary}</p>
                  )}
                </div>
              )
            })}
            {items.length > 3 && (
              <p className="text-xs text-slate-400">+ {items.length - 3} more item{items.length - 3 !== 1 ? 's' : ''}</p>
            )}
          </div>
        )}
      </div>
    )
  }

  // Fallback: object with unknown shape
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
      <p className="text-sm text-slate-500">Data loaded. See raw data below.</p>
    </div>
  )
}

export function JPSectionContent({ jobProfileId, section }: Props) {
  const [data, setData] = useState<unknown>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [importResult, setImportResult] = useState<{ imported_count: number; skipped_count: number } | null>(null)
  const [isImporting, setIsImporting] = useState(false)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)

    const getters: Record<string, () => Promise<unknown>> = {
      personal: () => jobProfileApi.getPersonal(jobProfileId),
      education: () => jobProfileApi.getEducation(jobProfileId),
      experience: () => jobProfileApi.getExperience(jobProfileId),
      projects: () => jobProfileApi.getProjects(jobProfileId),
      research: () => jobProfileApi.getResearch(jobProfileId),
      certifications: () => jobProfileApi.getCertifications(jobProfileId),
      skills: () => jobProfileApi.getSkills(jobProfileId),
    }

    const getter = getters[section]
    if (!getter) { setIsLoading(false); return }

    getter()
      .then(d => { if (!cancelled) { setData(d); setIsLoading(false) } })
      .catch(err => { if (!cancelled) { setError(err instanceof HttpError ? err.message : 'Failed to load'); setIsLoading(false) } })

    return () => { cancelled = true }
  }, [jobProfileId, section])

  const importSection = async () => {
    setIsImporting(true)
    try {
      const importers: Record<string, () => Promise<{ imported_count: number; skipped_count: number }>> = {
        education: () => jobProfileApi.importEducation(jobProfileId),
        experience: () => jobProfileApi.importExperience(jobProfileId),
        projects: () => jobProfileApi.importProjects(jobProfileId),
        research: () => jobProfileApi.importResearch(jobProfileId),
        certifications: () => jobProfileApi.importCertifications(jobProfileId),
        skills: () => jobProfileApi.importSkills(jobProfileId),
      }
      const importer = importers[section]
      if (importer) {
        const result = await importer()
        setImportResult(result)
      }
    } catch (err) {
      setError(err instanceof HttpError ? err.message : 'Import failed')
    } finally {
      setIsImporting(false)
    }
  }

  if (isLoading) return (
    <div className="flex items-center gap-2 text-sm text-slate-400 py-8">
      <span className="animate-spin">⟳</span>
      Loading {section}...
    </div>
  )

  if (error) return (
    <div role="alert" className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
      <AlertCircle size={16} className="shrink-0 mt-0.5" />
      <div className="flex-1">
        <p>{error}</p>
      </div>
      <button
        onClick={() => window.location.reload()}
        className="text-red-600 hover:text-red-800 font-medium underline text-xs"
      >
        Retry
      </button>
    </div>
  )

  const hasImport = ['education', 'experience', 'projects', 'research', 'certifications', 'skills'].includes(section)

  return (
    <div className="space-y-4">
      {/* Import bar */}
      {hasImport && (
        <div className="flex items-center gap-3">
          <button
            onClick={importSection}
            disabled={isImporting}
            className="flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <Download size={15} />
            {isImporting ? 'Importing...' : `Import ${section} from User Profile`}
          </button>
          {importResult && (
            <span className="flex items-center gap-1.5 text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-3 py-1">
              <CheckCircle size={13} />
              Imported {importResult.imported_count}, skipped {importResult.skipped_count}
            </span>
          )}
        </div>
      )}

      {/* Styled summary */}
      <SectionSummary section={section} data={data} />

      {/* Raw data collapsible */}
      <details className="text-xs">
        <summary className="cursor-pointer text-slate-400 hover:text-slate-600 select-none py-1">Raw data</summary>
        <pre className="mt-2 bg-slate-50 border border-slate-200 text-slate-600 p-4 rounded-lg overflow-auto max-h-64">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>

      <p className="text-xs text-slate-400">Full section editors available in future release.</p>
    </div>
  )
}
