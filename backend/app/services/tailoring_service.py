from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.matching_graph import run_matching_pipeline
from app.agents.tailoring_graph import run_tailoring_pipeline
from app.config import get_settings
from app.models import Application, ApplicationStatus, Job, Resume, User
from app.schemas import CoverLetterResult, TailoredResumeResult
from app.services.matching_service import get_primary_resume


async def get_job_and_resume(
    db: AsyncSession, user_id: UUID, job_id: UUID
) -> tuple[Job, Resume, User]:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise ValueError("Job not found")

    resume = await get_primary_resume(db, user_id)
    if not resume or not resume.parsed_text:
        raise ValueError("Upload a resume before generating tailored content")

    return job, resume, user


async def upsert_application_draft(
    db: AsyncSession,
    user_id: UUID,
    job_id: UUID,
    resume_id: UUID,
    *,
    cover_letter: str | None = None,
    tailored_resume: dict | None = None,
) -> Application:
    result = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.job_id == job_id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        app = Application(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=ApplicationStatus.DRAFT,
        )
        db.add(app)

    if cover_letter is not None:
        app.cover_letter = cover_letter
    if tailored_resume is not None:
        app.tailored_resume = tailored_resume
    app.resume_id = resume_id
    await db.flush()
    await db.refresh(app)
    return app


async def generate_cover_letter_for_job(
    db: AsyncSession,
    user_id: UUID,
    job_id: UUID,
    persist: bool = True,
) -> CoverLetterResult:
    job, resume, user = await get_job_and_resume(db, user_id, job_id)
    skills = (resume.parsed_json or {}).get("skills", [])

    settings = get_settings()
    hook = ""
    if settings.anthropic_api_key or settings.openai_api_key:
        match_state = await run_matching_pipeline(
            resume_text=resume.parsed_text,
            resume_skills=skills,
            job_title=job.title,
            job_description=job.description or "",
            company=job.company,
            use_llm=True,
        )
        hook = match_state.get("cover_letter_hook", "")

    state = await run_tailoring_pipeline(
        resume_text=resume.parsed_text,
        resume_skills=skills,
        candidate_name=user.full_name or user.email.split("@")[0],
        job_title=job.title,
        company=job.company,
        job_description=job.description or "",
        keywords=(resume.parsed_json or {}).get("skills", []),
        cover_letter_hook=hook,
    )

    letter = state.get("cover_letter", "")
    application_id = None
    if persist:
        app = await upsert_application_draft(
            db, user_id, job.id, resume.id, cover_letter=letter
        )
        application_id = app.id

    return CoverLetterResult(
        job_id=job.id,
        cover_letter=letter,
        application_id=application_id,
    )


async def tailor_resume_for_job(
    db: AsyncSession,
    user_id: UUID,
    job_id: UUID,
    persist: bool = True,
) -> TailoredResumeResult:
    job, resume, user = await get_job_and_resume(db, user_id, job_id)
    skills = (resume.parsed_json or {}).get("skills", [])

    state = await run_tailoring_pipeline(
        resume_text=resume.parsed_text,
        resume_skills=skills,
        candidate_name=user.full_name or user.email.split("@")[0],
        job_title=job.title,
        company=job.company,
        job_description=job.description or "",
    )

    tailored = {
        "job_id": str(job.id),
        "job_title": job.title,
        "company": job.company,
        "tailored_summary": state.get("tailored_summary", ""),
        "bullet_highlights": state.get("bullet_highlights", []),
        "skills_to_emphasize": state.get("skills_to_emphasize", []),
        "original_filename": resume.filename,
    }

    application_id = None
    if persist:
        app = await upsert_application_draft(
            db, user_id, job.id, resume.id, tailored_resume=tailored
        )
        application_id = app.id

    return TailoredResumeResult(
        job_id=job.id,
        application_id=application_id,
        job_title=tailored["job_title"],
        company=tailored["company"],
        tailored_summary=tailored["tailored_summary"],
        bullet_highlights=tailored["bullet_highlights"],
        skills_to_emphasize=tailored["skills_to_emphasize"],
        original_filename=tailored["original_filename"],
    )


async def generate_application_package(
    db: AsyncSession,
    user_id: UUID,
    job_id: UUID,
) -> dict:
    """Cover letter + tailored resume in one LangGraph run."""
    job, resume, user = await get_job_and_resume(db, user_id, job_id)
    skills = (resume.parsed_json or {}).get("skills", [])

    state = await run_tailoring_pipeline(
        resume_text=resume.parsed_text,
        resume_skills=skills,
        candidate_name=user.full_name or user.email.split("@")[0],
        job_title=job.title,
        company=job.company,
        job_description=job.description or "",
    )

    tailored = {
        "job_title": job.title,
        "company": job.company,
        "tailored_summary": state.get("tailored_summary", ""),
        "bullet_highlights": state.get("bullet_highlights", []),
        "skills_to_emphasize": state.get("skills_to_emphasize", []),
    }
    letter = state.get("cover_letter", "")

    app = await upsert_application_draft(
        db,
        user_id,
        job.id,
        resume.id,
        cover_letter=letter,
        tailored_resume=tailored,
    )

    return {
        "application_id": app.id,
        "job_id": job.id,
        "cover_letter": letter,
        "tailored_resume": tailored,
    }
