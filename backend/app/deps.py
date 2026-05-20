from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services.supabase_auth import resolve_bearer_token

security = HTTPBearer(auto_error=False)


async def get_or_create_user(
    db: AsyncSession,
    supabase_id: str,
    email: str | None,
    full_name: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.supabase_id == supabase_id))
    user = result.scalar_one_or_none()

    if not user and email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and not user.supabase_id:
            user.supabase_id = supabase_id

    if not user:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email required for first-time sign-in",
            )
        user = User(email=email, full_name=full_name, supabase_id=supabase_id)
        db.add(user)
        await db.flush()
        await db.refresh(user)

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    sub, email, full_name = await resolve_bearer_token(credentials.credentials)
    return await get_or_create_user(db, sub, email, full_name)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
