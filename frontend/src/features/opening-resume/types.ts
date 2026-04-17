export interface OpeningResume {
  id: string
  job_opening_id: string
  source_job_profile_id: string | null
  created_at: string
  updated_at: string
}

export interface ORPersonal {
  id: string; resume_id: string; full_name: string | null; email: string | null;
  phone: string | null; location: string | null; linkedin_url: string | null;
  github_url: string | null; portfolio_url: string | null; summary: string | null;
  updated_at: string;
}

export interface OREducation {
  id: string; resume_id: string; institution: string; degree: string;
  field_of_study: string | null; start_date: string | null; end_date: string | null;
  gpa: string | null; bullet_points: string[];
}

export interface ORExperience {
  id: string; resume_id: string; company: string; title: string;
  location: string | null; start_date: string | null; end_date: string | null;
  is_current: boolean; bullet_points: string[];
}

export interface ORProject {
  id: string; resume_id: string; title: string; description: string | null;
  technologies: string[]; url: string | null; bullet_points: string[];
}

export interface ORResearch {
  id: string; resume_id: string; title: string; institution: string | null;
  journal: string | null; year: string | null; description: string | null;
  url: string | null; bullet_points: string[]; reference_links: string[];
}

export interface ORCertification {
  id: string; resume_id: string; name: string; issuing_organization: string | null;
  issue_date: string | null; expiry_date: string | null;
  credential_id: string | null; credential_url: string | null;
}

export interface ORSkills { skills: string[] }
