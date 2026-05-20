# LangGraph Agents

## Phase 2 (implemented)

`backend/app/agents/matching_graph.py` — resume vs job scoring pipeline:

```
extract_requirements → score (heuristic | Claude/OpenAI)
```

API: `POST /api/v1/ai/match/{job_id}`, `POST /api/v1/ai/match-all`

## Phase 4 (planned)

```
JobSearchAgent → ResumeOptAgent → CoverLetterAgent
      ↓                ↓                   ↓
ScoringAgent → AutoApplyAgent → TrackingAgent
      ↓                ↓                   ↓
FeedbackAgent ← AnalyticsAgent ← NotifyAgent
```
