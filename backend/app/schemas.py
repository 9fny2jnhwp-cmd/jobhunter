from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    supabase_id: str | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeParsed(BaseModel):
    raw_text: str
    skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    job_titles: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)


class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    is_primary: bool
    parsed_text: str | None
    parsed_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    location: str | None
    remote: bool
    url: str | None
    match_score: int | None
    source: str | None
    posted_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: ApplicationStatus
    applied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_applications: int
    applied_this_week: int
    interviews: int
    avg_match_score: float | None
    resumes_uploaded: int


class TokenPayload(BaseModel):
    sub: str
    email: str | None = None


class JobMatchResult(BaseModel):
    job_id: UUID
    match_score: int
    reasoning: str
    keywords: list[str] = Field(default_factory=list)
    cover_letter_hook: str = ""


class MatchAllResponse(BaseModel):
    matched: int
    results: list[JobMatchResult]


class CoverLetterResult(BaseModel):
    job_id: UUID
    cover_letter: str
    application_id: UUID | None = None


class TailoredResumeResult(BaseModel):
    job_id: UUID
    application_id: UUID | None = None
    job_title: str
    company: str
    tailored_summary: str
    bullet_highlights: list[str] = Field(default_factory=list)
    skills_to_emphasize: list[str] = Field(default_factory=list)
    original_filename: str = ""


class ApplicationPackageResult(BaseModel):
    application_id: UUID
    job_id: UUID
    cover_letter: str
    tailored_resume: dict


class ApplicationDetailResponse(BaseModel):
    id: UUID
    job_id: UUID
    job_title: str
    company: str
    status: ApplicationStatus
    cover_letter: str | None
    tailored_resume: dict | None
    applied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
