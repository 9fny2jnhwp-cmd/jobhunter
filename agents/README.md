# LangGraph Agents

## Phase 2 (implemented)

`backend/app/agents/matching_graph.py` — resume vs job scoring pipeline:

```
extract_requirements → score (heuristic | Claude/OpenAI)
```

API: `POST /api/v1/ai/match/{job_id}`, `POST /api/v1/ai/match-all`

## Phase 2 — Tailoring (implemented)

`backend/app/agents/tailoring_graph.py` — LangGraph pipeline:

```
analyze_job → draft_cover_letter → tailor_resume
```

API:

- `POST /api/v1/ai/cover-letter/{job_id}`
- `POST /api/v1/ai/tailor-resume/{job_id}`
- `POST /api/v1/ai/application-package/{job_id}` (both in one run)

## Phase 4 (planned)

```
JobSearchAgent → ResumeOptAgent → CoverLetterAgent
      ↓                ↓                   ↓
ScoringAgent → AutoApplyAgent → TrackingAgent
      ↓                ↓                   ↓
FeedbackAgent ← AnalyticsAgent ← NotifyAgent
```
