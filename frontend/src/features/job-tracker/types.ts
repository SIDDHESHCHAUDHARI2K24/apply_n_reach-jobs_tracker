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
  raw_text: string | null
  created_at: string
}

export interface OpeningFilters {
  status?: OpeningStatus
  company?: string
  role?: string
}
