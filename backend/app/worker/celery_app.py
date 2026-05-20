import asyncio
from uuid import UUID

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "jobhunter",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="app.worker.parse_resume_async")
def parse_resume_async(resume_id: str) -> dict:
    return {"resume_id": resume_id, "status": "queued"}


@celery_app.task(name="app.worker.match_all_jobs_task")
def match_all_jobs_task(user_id: str, use_llm: bool | None = None) -> dict:
    from app.database import AsyncSessionLocal
    from app.services.matching_service import match_all_jobs_for_user

    async def _run() -> int:
        async with AsyncSessionLocal() as db:
            try:
                results = await match_all_jobs_for_user(db, UUID(user_id), use_llm=use_llm)
                await db.commit()
                return len(results)
            except Exception:
                await db.rollback()
                raise

    matched = asyncio.run(_run())
    return {"user_id": user_id, "matched": matched, "status": "complete"}
