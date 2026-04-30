export interface ProfileSummary {
  id: string
  user_id: string
  created_at: string
}

export interface PersonalDetails {
  id: string
  profile_id: string
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  summary: string | null
  created_at: string
  updated_at: string
}

export interface Education {
  id: string
  profile_id: string
  institution: string
  degree: string
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  gpa: string | null
  bullet_points: string[]
  reference_links?: string[]
  created_at: string
  updated_at: string
}

export interface Experience {
  id: string
  profile_id: string
  company: string
  title: string
  location: string | null
  start_date: string | null
  end_date: string | null
  is_current: boolean
  context: string | null
  bullet_points: string[]
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  profile_id: string
  title: string
  description: string | null
  technologies: string[]
  url: string | null
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
}

export interface Research {
  id: string
  profile_id: string
  title: string
  journal: string | null
  year: string | null
  description: string | null
  url: string | null
  created_at: string
  updated_at: string
}

export interface Certification {
  id: string
  profile_id: string
  name: string
  credential_url: string | null
  created_at: string
  updated_at: string
}

export interface SkillsData {
  technical: string[]
  competency: string[]
}
