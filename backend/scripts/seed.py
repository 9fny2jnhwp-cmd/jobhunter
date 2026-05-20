"""Seed sample jobs and a dev user. Run: python -m scripts.seed"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models import Application, ApplicationStatus, Job, User


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "dev@jobhunter.local"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email="dev@jobhunter.local",
                full_name="Dev User",
                supabase_id="dev-dev@jobhunter.local",
            )
            db.add(user)
            await db.flush()

        sample_jobs = [
            Job(
                title="Senior Full Stack Engineer",
                company="RemoteFlow Inc",
                location="Worldwide",
                remote=True,
                url="https://example.com/jobs/1",
                description="Build Next.js + FastAPI products for remote teams.",
                match_score=92,
                source="seed",
                posted_at=datetime.now(timezone.utc),
            ),
            Job(
                title="Backend Engineer (Python)",
                company="CloudHire",
                location="US / EU Remote",
                remote=True,
                url="https://example.com/jobs/2",
                description="FastAPI, PostgreSQL, Celery, LangGraph experience preferred.",
                match_score=88,
                source="seed",
                posted_at=datetime.now(timezone.utc),
            ),
            Job(
                title="AI Automation Engineer",
                company="ApplyBot",
                location="Remote",
                remote=True,
                url="https://example.com/jobs/3",
                description="LangGraph agents, resume tailoring, browser automation.",
                match_score=95,
                source="seed",
                posted_at=datetime.now(timezone.utc),
            ),
        ]

        for job in sample_jobs:
            existing = await db.execute(select(Job).where(Job.url == job.url))
            if not existing.scalar_one_or_none():
                db.add(job)

        await db.commit()

        jobs_result = await db.execute(select(Job).limit(2))
        jobs = jobs_result.scalars().all()
        for job in jobs:
            app_exists = await db.execute(
                select(Application).where(
                    Application.user_id == user.id, Application.job_id == job.id
                )
            )
            if not app_exists.scalar_one_or_none():
                db.add(
                    Application(
                        user_id=user.id,
                        job_id=job.id,
                        status=ApplicationStatus.APPLIED if job.match_score == 92 else ApplicationStatus.DRAFT,
                        applied_at=datetime.now(timezone.utc) if job.match_score == 92 else None,
                    )
                )

        await db.commit()
        print("Seed complete. Dev token: Bearer dev:dev@jobhunter.local")


if __name__ == "__main__":
    asyncio.run(seed())
