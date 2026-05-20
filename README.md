# JobHunter AI — Autonomous Remote Job Application Platform

A production-grade AI-powered platform that autonomously searches remote jobs, tailors resumes, generates cover letters, and auto-applies — built on Next.js + FastAPI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React, TailwindCSS, shadcn/ui, Framer Motion |
| Backend | Python FastAPI, Uvicorn, Pydantic |
| AI | Claude API (primary), OpenAI (fallback), LangGraph agents |
| Database | PostgreSQL via Supabase, Prisma ORM |
| Queue | Redis + Celery (background jobs) |
| Scraping | Playwright, Scrapy, rotating proxies |
| Auth | Supabase Auth + NextAuth |
| File Gen | WeasyPrint (PDF), python-docx (DOCX) |
| Vector DB | ChromaDB (local) / Pinecone (production) |
| Deploy | Docker Compose, Vercel (frontend), Railway (backend) |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  Dashboard │ Job Feed │ Resume Builder │ Analytics       │
└──────────────────────┬──────────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                          │
│  Auth │ Jobs │ Resume │ Applications │ AI │ Files        │
└───┬──────────────┬────────────────┬───────────────────┬─┘
    │              │                │                   │
┌───▼───┐   ┌──────▼──────┐  ┌────▼────┐  ┌──────────▼──┐
│Supabase│   │Redis+Celery │  │ChromaDB │  │  AI Agents  │
│  DB   │   │  Job Queue  │  │Vectors  │  │  LangGraph  │
└───────┘   └─────────────┘  └─────────┘  └─────────────┘
```

## Quickstart

```bash
git clone https://github.com/your-org/jobhunter-ai
cd jobhunter-ai

cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local development (without Docker)

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Database**

```bash
cd backend
alembic upgrade head
python -m scripts.seed
```

### Supabase Auth setup

1. Create a project at [supabase.com](https://supabase.com).
2. Copy **Project URL**, **anon key**, and **JWT Secret** into `.env` and `frontend/.env.local`.
3. Enable Email auth under Authentication → Providers.
4. Set Site URL to `http://localhost:3000` and redirect URL `http://localhost:3000/auth/callback`.
5. Sign up via the login page; the API auto-provisions users from the JWT.

Dev mode (`NEXT_PUBLIC_DEV_AUTH=true`) still works with `Bearer dev:<email>` when Supabase is not configured.

### AI job matching (Phase 2)

Upload a resume, then on **Job Feed** click **AI Match All Jobs**. With `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` set, LangGraph uses LLM scoring; otherwise heuristic matching runs.

```bash
POST /api/v1/ai/match-all?use_llm=true
POST /api/v1/ai/match/{job_id}
```

### Cover letters & resume tailoring

On **Job Feed**, each role has **Cover letter**, **Tailor resume**, and **Full package** actions. Results are saved as draft applications.

```bash
POST /api/v1/ai/cover-letter/{job_id}
POST /api/v1/ai/tailor-resume/{job_id}
POST /api/v1/ai/application-package/{job_id}
```

Run migration after pull: `cd backend && alembic upgrade head`

### Push to GitHub

```powershell
.\scripts\setup-github.ps1 -RepoUrl "https://github.com/YOUR_USER/jobhunter-ai.git"
```

## Phase Roadmap

| Phase | Features | Status |
|-------|----------|--------|
| 1 | Auth, Resume Upload, Parsing, Dashboard | Done |
| 2 | Resume Tailoring, Cover Letter Gen, AI Matching | Done |
| 3 | Auto-Apply Engine, Browser Automation | Planned |
| 4 | Multi-Agent Orchestration, Analytics, Learning | Planned |
