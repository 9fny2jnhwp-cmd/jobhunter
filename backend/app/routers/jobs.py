from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_optional_user
from app.models import Job, User
from app.schemas import JobResponse

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    remote_only: bool = Query(True),
    min_score: int | None = Query(None, ge=0, le=100),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User | None = Depends(get_optional_user),
):
    query = select(Job).order_by(Job.match_score.desc().nullslast(), Job.created_at.desc())
    if remote_only:
        query = query.where(Job.remote.is_(True))
    if min_score is not None:
        query = query.where(Job.match_score >= min_score)
    query = query.limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID

    from fastapi import HTTPException, status

    result = await db.execute(select(Job).where(Job.id == UUID(job_id)))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
