import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Resume, User
from app.schemas import ResumeResponse
from app.services.resume_parser import extract_text, parse_resume_text

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())
    )
    return result.scalars().all()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    set_primary: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use PDF, DOCX, or TXT.",
        )

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 10 MB limit")

    uploads_dir = Path(settings.uploads_dir) / str(current_user.id)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "resume").suffix or ".bin"
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = uploads_dir / stored_name
    file_path.write_bytes(content)

    mime = file.content_type or "application/octet-stream"
    try:
        raw_text = extract_text(file_path, mime)
        parsed = parse_resume_text(raw_text)
        parsed_json = parsed.model_dump()
        parsed_text = parsed.raw_text
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {exc}",
        ) from exc

    if set_primary:
        await db.execute(
            update(Resume).where(Resume.user_id == current_user.id).values(is_primary=False)
        )

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or stored_name,
        file_path=str(file_path),
        mime_type=mime,
        parsed_text=parsed_text,
        parsed_json=parsed_json,
        is_primary=set_primary,
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume
