export type OpeningStatus = 'discovered' | 'applied' | 'phone_screen' | 'interview' | 'offer' | 'rejected' | 'withdrawn'

export interface JobOpening {
  id: string
  user_id: string
  company: string
  role: string
  url: string | null
  status: OpeningStatus
  notes: string | null
  created_at: string
  updated_at: string
}

export interface StatusHistoryEntry {
  id: string
  job_opening_id: string
  status: OpeningStatus
  changed_at: string
  notes: string | null
}

export interface CreateOpeningRequest {
  company: string
  role: string
  url?: string
  status?: OpeningStatus
  notes?: string
}

export interface ExtractionRun {
  id: string
  user_id: string
  url: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message: string | null
  created_at: string
}

export interface ExtractedDetails {
  id: string
  run_id: string
  company: string | null
  role: string | null
  location: string | null
  required_skills: string[]
  raw_text: string | null
  created_at: string
}

export interface OpeningFilters {
  status?: OpeningStatus
  company?: string
  role?: string
}

export type EmailAgentRunStatus =
  | 'idle'
  | 'running'
  | 'paused'
  | 'succeeded'
  | 'failed'
  | 'cancelled'
  | 'timeout'

export interface EmailAgentStartRequest {
  recipient_type?: string
  raw_jd?: string
  raw_resume?: string
}

export interface EmailAgentRunResponse {
  run_id: string
  opening_id: string
  status: string
  message: string
}

export interface EmailAgentEvent {
  node?: string
  status?: string
  message?: string
  [key: string]: unknown
}

export interface EmailAgentStatusResponse {
  run_id: string | null
  opening_id: string
  agent_status: EmailAgentRunStatus | string
  current_node: string | null
  events: EmailAgentEvent[]
  error_message: string | null
  started_at: string | null
  completed_at: string | null
}

export interface EmailAgentRunListItem {
  id: string
  opening_id: string
  status: EmailAgentRunStatus | string
  current_node: string | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface EmailAgentResumeRequest {
  user_edits: Record<string, unknown>[]
}

export interface EmailAgentOutputResponse {
  generated_emails: Record<string, unknown>[]
  subject_lines: Record<string, unknown>[]
  followup_drafts: Record<string, unknown>[]
  outreach_status: string | null
}
