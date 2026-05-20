from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Job, User
from app.schemas import JobMatchResult, MatchAllResponse
from app.services.matching_service import match_all_jobs_for_user, match_job_for_user

router = APIRouter()


@router.post("/match/{job_id}", response_model=JobMatchResult)
async def match_single_job(
    job_id: UUID,
    use_llm: bool | None = Query(None, description="Force LLM scoring when API keys exist"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    try:
        return await match_job_for_user(db, current_user.id, job, use_llm=use_llm)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/match-all", response_model=MatchAllResponse)
async def match_all_jobs(
    use_llm: bool | None = Query(None),
    background: bool = Query(False, description="Queue via Celery when true"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if background:
        from app.worker.celery_app import match_all_jobs_task

        match_all_jobs_task.delay(str(current_user.id), use_llm)
        return MatchAllResponse(matched=0, results=[])

    try:
        results = await match_all_jobs_for_user(db, current_user.id, use_llm=use_llm)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MatchAllResponse(matched=len(results), results=results)
