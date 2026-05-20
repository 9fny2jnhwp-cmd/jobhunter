from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Application, Job, User
from app.schemas import ApplicationDetailResponse, ApplicationResponse

router = APIRouter()


@router.get("/", response_model=list[ApplicationDetailResponse])
async def list_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .where(Application.user_id == current_user.id)
        .options(selectinload(Application.job))
        .order_by(Application.created_at.desc())
    )
    apps = result.scalars().all()
    return [
        ApplicationDetailResponse(
            id=app.id,
            job_id=app.job_id,
            job_title=app.job.title,
            company=app.job.company,
            status=app.status,
            cover_letter=app.cover_letter,
            tailored_resume=app.tailored_resume,
            applied_at=app.applied_at,
            created_at=app.created_at,
        )
        for app in apps
    ]


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
        .options(selectinload(Application.job))
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return ApplicationDetailResponse(
        id=app.id,
        job_id=app.job_id,
        job_title=app.job.title,
        company=app.job.company,
        status=app.status,
        cover_letter=app.cover_letter,
        tailored_resume=app.tailored_resume,
        applied_at=app.applied_at,
        created_at=app.created_at,
    )
