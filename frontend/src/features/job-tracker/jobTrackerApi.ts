import { apiRequest } from '@core/http/client'
import type { JobOpening, CreateOpeningRequest, StatusHistoryEntry, ExtractionRun, ExtractedDetails } from './types'

export const jobTrackerApi = {
  list: (params?: { limit?: number; after_id?: string; status?: string; company?: string; role?: string }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.after_id) qs.set('after_id', params.after_id)
    if (params?.status) qs.set('status', params.status)
    if (params?.company) qs.set('company', params.company)
    if (params?.role) qs.set('role', params.role)
    const q = qs.toString()
    return apiRequest<JobOpening[]>(`/job-openings${q ? `?${q}` : ''}`)
  },
  get: (id: string) => apiRequest<JobOpening>(`/job-openings/${id}`),
  create: (data: CreateOpeningRequest) =>
    apiRequest<JobOpening>('/job-openings', { method: 'POST', body: data }),
  update: (id: string, data: Partial<CreateOpeningRequest>) =>
    apiRequest<JobOpening>(`/job-openings/${id}`, { method: 'PATCH', body: data }),
  remove: (id: string) =>
    apiRequest<void>(`/job-openings/${id}`, { method: 'DELETE' }),
  transitionStatus: (id: string, status: string) =>
    apiRequest<JobOpening>(`/job-openings/${id}/status`, { method: 'POST', body: { status } }),
  getStatusHistory: (id: string) =>
    apiRequest<StatusHistoryEntry[]>(`/job-openings/${id}/status-history`),

  // Ingestion
  refreshExtraction: () =>
    apiRequest<{ run_id: string }>('/extraction/refresh', { method: 'POST' }),
  getLatestExtracted: () =>
    apiRequest<ExtractedDetails | null>('/extracted-details/latest'),
  getExtractionRuns: () =>
    apiRequest<ExtractionRun[]>('/extraction-runs'),

  // Opening resume check
  getOpeningResume: (openingId: string) =>
    apiRequest<{ id: string } | null>(`/job-openings/${openingId}/resume`),
}
