"""
LangGraph pipeline: analyze resume vs job → score → suggest tailoring keywords.
Falls back to heuristics when no AI API key is configured.
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.services.ai_client import complete_json
from app.services.resume_parser import SKILL_KEYWORDS


class MatchState(TypedDict, total=False):
    resume_text: str
    resume_skills: list[str]
    job_title: str
    job_description: str
    company: str
    requirements: list[str]
    match_score: int
    reasoning: str
    keywords: list[str]
    cover_letter_hook: str


def extract_requirements(state: MatchState) -> MatchState:
    desc = state.get("job_description") or ""
    title = state.get("job_title") or ""
    combined = f"{title}\n{desc}".lower()

    reqs: list[str] = []
    for skill in SKILL_KEYWORDS:
        if skill in combined:
            reqs.append(skill)

    import re

    for m in re.finditer(r"(?i)(?:required|must have)[:\s]+([^\n.]{10,120})", desc):
        reqs.append(m.group(1).strip()[:80])

    return {**state, "requirements": reqs[:15]}


def score_match_heuristic(state: MatchState) -> MatchState:
    resume = (state.get("resume_text") or "").lower()
    skills = set(s.lower() for s in state.get("resume_skills") or [])
    reqs = state.get("requirements") or []

    if not reqs:
        score = 70
        reasoning = "No explicit requirements parsed; baseline fit assumed."
    else:
        hits = sum(1 for r in reqs if r.lower() in resume or r.lower() in skills)
        score = min(100, int(40 + (hits / max(len(reqs), 1)) * 60))
        reasoning = f"Matched {hits}/{len(reqs)} parsed requirements against resume."

    missing = [r for r in reqs if r.lower() not in resume and r.lower() not in skills][:8]
    keywords = list({*(state.get("resume_skills") or [])[:5], *missing})[:12]

    return {
        **state,
        "match_score": score,
        "reasoning": reasoning,
        "keywords": keywords,
        "cover_letter_hook": f"Strong alignment with {state.get('job_title', 'this role')} at {state.get('company', 'the company')}.",
    }


async def score_match_llm(state: MatchState) -> MatchState:
    prompt = f"""Score how well this resume fits the job (0-100).

Job: {state.get('job_title')} at {state.get('company')}
Description:
{(state.get('job_description') or '')[:3000]}

Resume excerpt:
{(state.get('resume_text') or '')[:3000]}

Skills on resume: {', '.join(state.get('resume_skills') or [])}

Return JSON:
{{"match_score": <int>, "reasoning": "<1-2 sentences>", "keywords": ["<skill to emphasize>", ...], "cover_letter_hook": "<one sentence>"}}"""

    result = await complete_json(prompt, system="You are a technical recruiter. Output JSON only.")
    if not result:
        return score_match_heuristic(state)

    return {
        **state,
        "match_score": int(result.get("match_score", 70)),
        "reasoning": str(result.get("reasoning", "")),
        "keywords": list(result.get("keywords") or [])[:12],
        "cover_letter_hook": str(result.get("cover_letter_hook", "")),
    }


def build_matching_graph():
    graph = StateGraph(MatchState)
    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("score_heuristic", score_match_heuristic)
    graph.set_entry_point("extract_requirements")
    graph.add_edge("extract_requirements", "score_heuristic")
    graph.add_edge("score_heuristic", END)
    return graph.compile()


def build_matching_graph_with_llm():
    graph = StateGraph(MatchState)

    async def llm_node(state: MatchState) -> MatchState:
        return await score_match_llm(state)

    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("score_llm", llm_node)
    graph.set_entry_point("extract_requirements")
    graph.add_edge("extract_requirements", "score_llm")
    graph.add_edge("score_llm", END)
    return graph.compile()


async def run_matching_pipeline(
    resume_text: str,
    resume_skills: list[str],
    job_title: str,
    job_description: str,
    company: str,
    use_llm: bool = False,
) -> MatchState:
    initial: MatchState = {
        "resume_text": resume_text,
        "resume_skills": resume_skills,
        "job_title": job_title,
        "job_description": job_description,
        "company": company,
    }

    if use_llm:
        graph = build_matching_graph_with_llm()
        return await graph.ainvoke(initial)

    graph = build_matching_graph()
    return graph.invoke(initial)
