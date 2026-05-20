from jose import JWTError, jwt

from app.config import get_settings


def decode_supabase_token(token: str) -> dict | None:
    """Decode and validate a Supabase access JWT (HS256)."""
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        return None
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_aud": True},
        )
    except JWTError:
        return None


async def resolve_bearer_token(token: str) -> tuple[str, str | None, str | None]:
    """Parse Bearer token into (supabase_id, email, full_name)."""
    from fastapi import HTTPException, status

    settings = get_settings()

    if settings.supabase_jwt_secret:
        payload = decode_supabase_token(token)
        if payload:
            try:
                return claims_from_payload(payload)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if token.startswith("dev:"):
        email = token[4:].strip()
        return f"dev-{email}", email, "Dev User"

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def claims_from_payload(payload: dict) -> tuple[str, str | None, str | None]:
    """Return (sub, email, full_name) from Supabase JWT claims."""
    sub = payload.get("sub")
    if not sub:
        raise ValueError("Missing sub in token")

    email = payload.get("email")
    meta = payload.get("user_metadata") or {}
    if not email:
        email = meta.get("email")
    full_name = meta.get("full_name") or meta.get("name")
    return sub, email, full_name
