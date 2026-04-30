import { apiRequest } from '@core/http/client'
import type { JobOpening, CreateOpeningRequest, StatusHistoryEntry, ExtractionRun, ExtractedDetails } from './types'
import type {
  ExtractedDetailsResponse,
  ExtractionRunResponse,
  JobOpeningCreate,
  JobOpeningListResponse,
  JobOpeningResponse,
  JobOpeningStatus,
  JobOpeningStatusHistoryEntry,
  JobOpeningUpdate,
} from '@generated/contracts'

const toStringId = (id: number) => String(id)

const statusMapToUi: Record<JobOpeningStatus, JobOpening['status']> = {
  Interested: 'discovered',
  Applied: 'applied',
  Interviewing: 'interview',
  Offer: 'offer',
  Withdrawn: 'withdrawn',
  Rejected: 'rejected',
}

const statusMapToApi: Record<JobOpening['status'], JobOpeningStatus> = {
  discovered: 'Interested',
  applied: 'Applied',
  phone_screen: 'Interviewing',
  interview: 'Interviewing',
  offer: 'Offer',
  rejected: 'Rejected',
  withdrawn: 'Withdrawn',
}

function mapOpening(row: JobOpeningResponse): JobOpening {
  return {
    id: toStringId(row.id),
    user_id: toStringId(row.user_id),
    company: row.company_name,
    role: row.role_name,
    url: row.source_url ?? null,
    status: statusMapToUi[row.current_status],
    notes: row.notes ?? null,
    created_at: row.created_at ?? '',
    updated_at: row.updated_at ?? '',
  }
}

function mapHistory(row: JobOpeningStatusHistoryEntry): StatusHistoryEntry {
  return {
    id: toStringId(row.id),
    job_opening_id: toStringId(row.opening_id),
    status: statusMapToUi[row.to_status],
    changed_at: row.changed_at,
    notes: null,
  }
}

function mapExtractionRun(row: ExtractionRunResponse): ExtractionRun {
  const statusMap: Record<ExtractionRunResponse['status'], ExtractionRun['status']> = {
    queued: 'pending',
    running: 'processing',
    succeeded: 'completed',
    failed: 'failed',
  }
  return {
    id: toStringId(row.id),
    user_id: '',
    url: '',
    status: statusMap[row.status],
    error_message: row.error_message ?? null,
    created_at: row.created_at,
  }
}

function mapExtractedDetails(row: ExtractedDetailsResponse): ExtractedDetails {
  return {
    id: '',
    run_id: String(row.extraction_run_id),
    company: row.company_name ?? null,
    role: row.job_title ?? null,
    raw_text: row.description_summary ?? null,
    created_at: row.extracted_at,
  }
}

export const jobTrackerApi = {
  list: (params?: { limit?: number; after_id?: string; status?: string; company?: string; role?: string }) => {
    const qs = new URLSearchParams()
    if (params?.limit != null) qs.set('limit', String(params.limit))
    if (params?.after_id) qs.set('after_id', params.after_id)
    if (params?.status) qs.set('status', statusMapToApi[params.status as JobOpening['status']])
    if (params?.company) qs.set('company_name', params.company)
    if (params?.role) qs.set('role_name', params.role)
    const q = qs.toString()
    return apiRequest<JobOpeningListResponse>(`/job-openings${q ? `?${q}` : ''}`).then(response => ({
      items: response.items.map(mapOpening),
      has_more: response.has_more,
      next_cursor: response.next_cursor,
    }))
  },
  get: (id: string) => apiRequest<JobOpeningResponse>(`/job-openings/${id}`).then(mapOpening),
  create: (data: CreateOpeningRequest) =>
    apiRequest<JobOpeningResponse>('/job-openings', {
      method: 'POST',
      body: {
        source_url: data.url ?? null,
        company_name: data.company,
        role_name: data.role,
        notes: data.notes ?? null,
        initial_status: statusMapToApi[data.status ?? 'discovered'],
      } satisfies JobOpeningCreate,
    }).then(mapOpening),
  update: (id: string, data: Partial<CreateOpeningRequest>) =>
    apiRequest<JobOpeningResponse>(`/job-openings/${id}`, {
      method: 'PATCH',
      body: {
        source_url: data.url ?? undefined,
        company_name: data.company ?? undefined,
        role_name: data.role ?? undefined,
        notes: data.notes ?? undefined,
      } satisfies JobOpeningUpdate,
    }).then(mapOpening),
  remove: (id: string) =>
    apiRequest<void>(`/job-openings/${id}`, { method: 'DELETE' }),
  transitionStatus: (id: string, status: string) =>
    apiRequest<JobOpeningResponse>(`/job-openings/${id}/status`, {
      method: 'POST',
      body: { status: statusMapToApi[status as JobOpening['status']] },
    }).then(mapOpening),
  getStatusHistory: (id: string) =>
    apiRequest<JobOpeningStatusHistoryEntry[]>(`/job-openings/${id}/status-history`).then(rows => rows.map(mapHistory)),

  // Ingestion
  refreshExtraction: (openingId: string) =>
    apiRequest<{ run_id: number }>(`/job-openings/${openingId}/extraction/refresh`, { method: 'POST' }).then(result => ({ run_id: String(result.run_id) })),
  getLatestExtracted: (openingId: string) =>
    apiRequest<ExtractedDetailsResponse>(`/job-openings/${openingId}/extracted-details/latest`).then(mapExtractedDetails),
  getExtractionRuns: (openingId: string) =>
    apiRequest<ExtractionRunResponse[]>(`/job-openings/${openingId}/extraction-runs`).then(rows => rows.map(mapExtractionRun)),

  // Opening resume check
  getOpeningResume: (openingId: string) =>
    apiRequest<{ id: number }>(`/job-openings/${openingId}/resume`).then(result => ({ id: String(result.id) })),
}
