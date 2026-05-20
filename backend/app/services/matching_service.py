from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.matching_graph import run_matching_pipeline
from app.config import get_settings
from app.models import Job, Resume
from app.schemas import JobMatchResult


async def get_primary_resume(db: AsyncSession, user_id: UUID) -> Resume | None:
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.is_primary.desc(), Resume.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def match_job_for_user(
    db: AsyncSession,
    user_id: UUID,
    job: Job,
    use_llm: bool | None = None,
) -> JobMatchResult:
    resume = await get_primary_resume(db, user_id)
    if not resume or not resume.parsed_text:
        raise ValueError("Upload a resume before running job matching")

    settings = get_settings()
    if use_llm is None:
        use_llm = bool(settings.anthropic_api_key or settings.openai_api_key)

    skills = (resume.parsed_json or {}).get("skills", [])
    state = await run_matching_pipeline(
        resume_text=resume.parsed_text,
        resume_skills=skills,
        job_title=job.title,
        job_description=job.description or "",
        company=job.company,
        use_llm=use_llm,
    )

    job.match_score = int(state.get("match_score", 0))
    await db.flush()

    return JobMatchResult(
        job_id=job.id,
        match_score=job.match_score,
        reasoning=state.get("reasoning", ""),
        keywords=state.get("keywords", []),
        cover_letter_hook=state.get("cover_letter_hook", ""),
    )


async def match_all_jobs_for_user(
    db: AsyncSession,
    user_id: UUID,
    use_llm: bool | None = None,
) -> list[JobMatchResult]:
    result = await db.execute(select(Job).where(Job.remote.is_(True)))
    jobs = result.scalars().all()
    matches: list[JobMatchResult] = []
    for job in jobs:
        try:
            m = await match_job_for_user(db, user_id, job, use_llm=use_llm)
            matches.append(m)
        except ValueError:
            raise
        except Exception:
            continue
    return matches
