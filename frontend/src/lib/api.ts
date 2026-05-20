const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...init } = options;
  const headers: HeadersInit = {
    ...(init.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(init.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(
      typeof detail.detail === "string" ? detail.detail : JSON.stringify(detail),
      res.status
    );
  }

  return res.json() as Promise<T>;
}

export interface DashboardStats {
  total_applications: number;
  applied_this_week: number;
  interviews: number;
  avg_match_score: number | null;
  resumes_uploaded: number;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  remote: boolean;
  url: string | null;
  match_score: number | null;
  source: string | null;
}

export interface Resume {
  id: string;
  filename: string;
  mime_type: string;
  is_primary: boolean;
  parsed_json: {
    skills?: string[];
    experience_years?: number;
    job_titles?: string[];
  } | null;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
}

export interface JobMatchResult {
  job_id: string;
  match_score: number;
  reasoning: string;
  keywords: string[];
  cover_letter_hook: string;
}

export interface MatchAllResponse {
  matched: number;
  results: JobMatchResult[];
}

export interface CoverLetterResult {
  job_id: string;
  cover_letter: string;
  application_id: string | null;
}

export interface TailoredResumeResult {
  job_id: string;
  application_id: string | null;
  job_title: string;
  company: string;
  tailored_summary: string;
  bullet_highlights: string[];
  skills_to_emphasize: string[];
  original_filename: string;
}

export interface ApplicationPackageResult {
  application_id: string;
  job_id: string;
  cover_letter: string;
  tailored_resume: TailoredResumeResult | Record<string, unknown>;
}

export interface ApplicationDetail {
  id: string;
  job_id: string;
  job_title: string;
  company: string;
  status: string;
  cover_letter: string | null;
  tailored_resume: Record<string, unknown> | null;
  applied_at: string | null;
  created_at: string;
}
