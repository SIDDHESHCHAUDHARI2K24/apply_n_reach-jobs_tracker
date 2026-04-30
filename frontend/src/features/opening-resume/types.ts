export interface OpeningResume {
  id: string
  job_opening_id: string
  source_job_profile_id: string | null
  status: string
  generated_at: string | null
}

export interface ORPersonal {
  id: string; resume_id: string; full_name: string | null; email: string | null;
  phone: string | null; location: string | null; linkedin_url: string | null;
  github_url: string | null; portfolio_url: string | null; summary: string | null;
  updated_at: string;
}

export interface OREducation {
  id: string; resume_id: string; institution: string; degree: string | null;
  field_of_study: string | null; start_date: string | null; end_date: string | null;
  gpa: string | null; description: string | null; display_order: number;
}

export interface ORExperience {
  id: string; resume_id: string; company: string; title: string;
  location: string | null; start_date: string | null; end_date: string | null;
  is_current: boolean; description: string | null; display_order: number;
}

export interface ORProject {
  id: string; resume_id: string; title: string; description: string | null;
  technologies: string[]; url: string | null; start_date: string | null; end_date: string | null;
  display_order: number;
}

export interface ORResearch {
  id: string; resume_id: string; title: string; publication: string | null;
  published_date: string | null; description: string | null;
  url: string | null; display_order: number;
}

export interface ORCertification {
  id: string; resume_id: string; name: string; issuing_organization: string | null;
  issue_date: string | null; expiry_date: string | null;
  credential_id: string | null; credential_url: string | null; display_order: number;
}

export interface ORSkillItem {
  id: string
  resume_id: string
  category: string
  name: string
  proficiency_level: string | null
  display_order: number
}
