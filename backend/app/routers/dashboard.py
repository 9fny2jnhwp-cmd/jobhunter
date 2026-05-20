from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Application, ApplicationStatus, Job, Resume, User
from app.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    total_apps = await db.scalar(
        select(func.count()).select_from(Application).where(Application.user_id == current_user.id)
    )
    applied_week = await db.scalar(
        select(func.count())
        .select_from(Application)
        .where(
            Application.user_id == current_user.id,
            Application.status == ApplicationStatus.APPLIED,
            Application.applied_at >= week_ago,
        )
    )
    interviews = await db.scalar(
        select(func.count())
        .select_from(Application)
        .where(
            Application.user_id == current_user.id,
            Application.status == ApplicationStatus.INTERVIEW,
        )
    )
    resume_count = await db.scalar(
        select(func.count()).select_from(Resume).where(Resume.user_id == current_user.id)
    )

    avg_score = await db.scalar(
        select(func.avg(Job.match_score))
        .select_from(Job)
        .join(Application, Application.job_id == Job.id)
        .where(Application.user_id == current_user.id, Job.match_score.isnot(None))
    )

    return DashboardStats(
        total_applications=total_apps or 0,
        applied_this_week=applied_week or 0,
        interviews=interviews or 0,
        avg_match_score=float(avg_score) if avg_score else None,
        resumes_uploaded=resume_count or 0,
    )
