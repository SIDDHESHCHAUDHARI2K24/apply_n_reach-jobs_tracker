export type JobProfileStatus = 'draft' | 'active' | 'archived'

export interface JobProfile {
  id: string
  user_id: string
  title: string
  status: JobProfileStatus
  created_at: string
  updated_at: string
}

export interface JPPersonal {
  id: string; job_profile_id: string; full_name: string | null; email: string | null;
  phone: string | null; location: string | null; linkedin_url: string | null;
  github_url: string | null; portfolio_url: string | null; summary: string | null;
  updated_at: string;
}

export interface JPEducation {
  id: string; job_profile_id: string; institution: string; degree: string;
  field_of_study: string | null; start_date: string | null; end_date: string | null;
  gpa: string | null; bullet_points: string[];
}

export interface JPExperience {
  id: string; job_profile_id: string; company: string; title: string;
  location: string | null; start_date: string | null; end_date: string | null;
  is_current: boolean; bullet_points: string[];
}

export interface JPProject {
  id: string; job_profile_id: string; title: string; description: string | null;
  technologies: string[]; url: string | null; start_date: string | null;
  end_date: string | null; bullet_points: string[];
}

export interface JPResearch {
  id: string; job_profile_id: string; title: string; institution: string | null;
  journal: string | null; year: string | null; description: string | null;
  url: string | null; bullet_points: string[]; reference_links: string[];
}

export interface JPCertification {
  id: string; job_profile_id: string; name: string; issuing_organization: string | null;
  issue_date: string | null; expiry_date: string | null; credential_id: string | null;
  credential_url: string | null;
}

export interface JPSkills { skills: string[] }

export type RenderStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface ResumeMetadata {
  job_profile_id: string
  status: RenderStatus
  template_name: string
  rendered_at: string
  layout_json: Record<string, unknown>
  error_message: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ImportResult {
  imported_count: number
  skipped_count: number
}

export interface CreateJobProfileRequest {
  title: string
  status?: JobProfileStatus
}
