import { useState, useEffect } from 'react'
import { jobProfileApi } from '@features/job-profiles/jobProfileApi'
import { HttpError } from '@core/http/client'

interface Props {
  jobProfileId: string
  section: string
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

  if (isLoading) return <div>Loading {section}...</div>
  if (error) return <div role="alert" style={{ color: 'red' }}>{error} <button onClick={() => window.location.reload()}>Retry</button></div>

  const hasImport = ['education', 'experience', 'projects', 'research', 'certifications', 'skills'].includes(section)

  return (
    <div>
      {hasImport && (
        <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button onClick={importSection} disabled={isImporting}>
            {isImporting ? 'Importing...' : `Import ${section} from User Profile`}
          </button>
          {importResult && (
            <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              Imported: {importResult.imported_count}, Skipped: {importResult.skipped_count}
            </span>
          )}
        </div>
      )}
      <pre style={{ fontSize: '0.75rem', background: '#f9fafb', padding: '1rem', borderRadius: 4, overflow: 'auto', maxHeight: 400 }}>
        {JSON.stringify(data, null, 2)}
      </pre>
      <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
        Full section editors available in future release.
      </p>
    </div>
  )
}
