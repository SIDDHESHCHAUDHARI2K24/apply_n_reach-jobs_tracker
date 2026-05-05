import { API_BASE_URL } from '@core/config/env'
import { apiRequest } from '@core/http/client'
import type {
  JobOpening,
  CreateOpeningRequest,
  StatusHistoryEntry,
  ExtractionRun,
  ExtractedDetails,
  EmailAgentStartRequest,
  EmailAgentRunResponse,
  EmailAgentStatusResponse,
  EmailAgentRunListItem,
  EmailAgentResumeRequest,
  EmailAgentOutputResponse,
} from './types'
import type {
  ExtractedDetailsResponse,
  ExtractionRunResponse,
  JobOpeningCreate,
  JobOpeningListResponse,
  JobOpeningResponse,
  JobOpeningStatus,
  JobOpeningStatusHistoryEntry,
  JobOpeningUpdate,
  ManualExtractedDetailsCreate,
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
    location: row.location ?? null,
    required_skills: row.required_skills ?? [],
    raw_text: row.description_summary ?? null,
    created_at: row.extracted_at,
  }
}

function mapEmailAgentRunResponse(row: { run_id: number; opening_id: number; status: string; message: string }): EmailAgentRunResponse {
  return {
    run_id: toStringId(row.run_id),
    opening_id: toStringId(row.opening_id),
    status: row.status,
    message: row.message,
  }
}

function mapEmailAgentStatus(row: {
  run_id: number | null
  opening_id: number
  agent_status: string
  current_node: string | null
  events?: Record<string, unknown>[]
  error_message: string | null
  started_at: string | null
  completed_at: string | null
}): EmailAgentStatusResponse {
  return {
    run_id: row.run_id == null ? null : toStringId(row.run_id),
    opening_id: toStringId(row.opening_id),
    agent_status: row.agent_status,
    current_node: row.current_node,
    events: row.events ?? [],
    error_message: row.error_message,
    started_at: row.started_at,
    completed_at: row.completed_at,
  }
}

function mapEmailAgentRunListItem(row: {
  id: number
  opening_id: number
  status: string
  current_node: string | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}): EmailAgentRunListItem {
  return {
    id: toStringId(row.id),
    opening_id: toStringId(row.opening_id),
    status: row.status,
    current_node: row.current_node,
    error_message: row.error_message,
    started_at: row.started_at,
    completed_at: row.completed_at,
    created_at: row.created_at,
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
    apiRequest<void>(`/job-openings/${id}?confirm=true`, { method: 'DELETE' }),
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

  saveManualExtractedDetails: (openingId: string, body: ManualExtractedDetailsCreate) =>
    apiRequest<ExtractedDetailsResponse>(`/job-openings/${openingId}/extracted-details/manual`, {
      method: 'POST',
      body,
    }).then(mapExtractedDetails),

  // Opening resume check
  getOpeningResume: (openingId: string) =>
    apiRequest<{ id: number }>(`/job-openings/${openingId}/resume`).then(result => ({ id: String(result.id) })),

  // Email agent
  startEmailAgentRun: (openingId: string, payload: EmailAgentStartRequest) =>
    apiRequest<{ run_id: number; opening_id: number; status: string; message: string }>(
      `/job-openings/${openingId}/email-agent/run`,
      {
        method: 'POST',
        body: payload,
      },
    ).then(mapEmailAgentRunResponse),
  getEmailAgentStatus: (openingId: string) =>
    apiRequest<{
      run_id: number | null
      opening_id: number
      agent_status: string
      current_node: string | null
      events?: Record<string, unknown>[]
      error_message: string | null
      started_at: string | null
      completed_at: string | null
    }>(`/job-openings/${openingId}/email-agent/status`).then(mapEmailAgentStatus),
  getEmailAgentRuns: (openingId: string) =>
    apiRequest<Array<{
      id: number
      opening_id: number
      status: string
      current_node: string | null
      error_message: string | null
      started_at: string | null
      completed_at: string | null
      created_at: string
    }>>(`/job-openings/${openingId}/email-agent/runs`).then(rows => rows.map(mapEmailAgentRunListItem)),
  resumeEmailAgent: (openingId: string, payload: EmailAgentResumeRequest) =>
    apiRequest<{ run_id: number; status: string; message: string }>(
      `/job-openings/${openingId}/email-agent/resume`,
      {
        method: 'POST',
        body: payload,
      },
    ).then(result => ({ run_id: toStringId(result.run_id), status: result.status, message: result.message })),
  getEmailAgentOutput: (openingId: string) =>
    apiRequest<EmailAgentOutputResponse>(`/job-openings/${openingId}/email-agent/output`),
  getEmailAgentStreamUrl: (openingId: string) => {
    const encodedId = encodeURIComponent(openingId)
    return `${API_BASE_URL}/job-openings/${encodedId}/email-agent/stream`
  },

  /** Resume tailoring LangGraph agent */
  startResumeAgent: (openingId: string) =>
    apiRequest<{ run_id: number; opening_id: number; status: string; message: string }>(
      `/job-openings/${openingId}/agent/run`,
      { method: 'POST' },
    ).then(mapEmailAgentRunResponse),
  getResumeAgentStatus: (openingId: string) =>
    apiRequest<{
      run_id: number | null
      opening_id: number
      agent_status: string
      current_node: string | null
      events?: Record<string, unknown>[]
      error_message: string | null
      started_at: string | null
      completed_at: string | null
    }>(`/job-openings/${openingId}/agent/status`).then(mapEmailAgentStatus),
  getResumeAgentStreamUrl: (openingId: string) => {
    const encodedId = encodeURIComponent(openingId)
    return `${API_BASE_URL}/job-openings/${encodedId}/agent/stream`
  },
}
