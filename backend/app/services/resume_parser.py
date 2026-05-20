import re
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.schemas import ResumeParsed

SKILL_KEYWORDS = {
    "python",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "fastapi",
    "postgresql",
    "aws",
    "docker",
    "kubernetes",
    "machine learning",
    "langchain",
    "sql",
    "node",
    "java",
    "go",
    "rust",
    "tailwind",
    "graphql",
    "redis",
    "celery",
    "playwright",
}


def extract_text_from_pdf(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def extract_text_from_docx(data: bytes) -> str:
    doc = Document(BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(file_path: Path, mime_type: str) -> str:
    data = file_path.read_bytes()
    if mime_type == "application/pdf" or file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(data)
    if mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ) or file_path.suffix.lower() in (".docx", ".doc"):
        return extract_text_from_docx(data)
    return data.decode("utf-8", errors="ignore")


def _extract_skills(text: str) -> list[str]:
    lower = text.lower()
    found = [s for s in SKILL_KEYWORDS if s in lower]
    return sorted(found, key=str.lower)


def _extract_job_titles(text: str) -> list[str]:
    patterns = [
        r"(?i)(senior|lead|staff|principal|junior)?\s*(software|full[- ]?stack|backend|frontend|data|ml|devops)\s*(engineer|developer|architect)",
        r"(?i)(product|project)\s*manager",
    ]
    titles: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            titles.add(match.group(0).strip())
    return list(titles)[:10]


def _extract_education(text: str) -> list[str]:
    pattern = r"(?i)(b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|ph\.?d\.?|bachelor|master|doctorate)[^\n]{0,80}"
    return [m.group(0).strip() for m in re.finditer(pattern, text)][:5]


def _estimate_experience_years(text: str) -> int | None:
    years = [int(y) for y in re.findall(r"(?i)(\d+)\+?\s*years?\s+(?:of\s+)?experience", text)]
    if years:
        return max(years)
    date_ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text, re.I)
    if date_ranges:
        starts = [int(s) for s, _ in date_ranges]
        return max(2026 - min(starts), 0)
    return None


def parse_resume_text(text: str) -> ResumeParsed:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return ResumeParsed(
        raw_text=text[:50000],
        skills=_extract_skills(cleaned),
        experience_years=_estimate_experience_years(cleaned),
        job_titles=_extract_job_titles(cleaned),
        education=_extract_education(cleaned),
    )
