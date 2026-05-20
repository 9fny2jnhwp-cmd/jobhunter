"""LangGraph pipeline for cover letter + resume tailoring."""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.services.ai_client import complete_json, complete_text


class TailoringState(TypedDict, total=False):
    resume_text: str
    resume_skills: list[str]
    candidate_name: str
    job_title: str
    company: str
    job_description: str
    keywords: list[str]
    cover_letter_hook: str
    job_analysis: str
    cover_letter: str
    tailored_summary: str
    bullet_highlights: list[str]
    skills_to_emphasize: list[str]


def analyze_job(state: TailoringState) -> TailoringState:
    desc = (state.get("job_description") or "")[:2000]
    title = state.get("job_title", "")
    company = state.get("company", "")
    analysis = f"Role: {title} at {company}. Key focus areas from posting: {desc[:500]}..."
    return {**state, "job_analysis": analysis}


async def draft_cover_letter(state: TailoringState) -> TailoringState:
    prompt = f"""Write a concise, professional cover letter (3-4 paragraphs, ~250 words).

Candidate: {state.get('candidate_name', 'Applicant')}
Role: {state.get('job_title')} at {state.get('company')}

Job description excerpt:
{(state.get('job_description') or '')[:2500]}

Resume excerpt:
{(state.get('resume_text') or '')[:2000]}

Skills: {', '.join(state.get('resume_skills') or [])}
Hook to weave in: {state.get('cover_letter_hook', '')}
Keywords to include naturally: {', '.join(state.get('keywords') or [])}

Do not invent employers or degrees not in the resume. Sign off professionally."""

    letter = await complete_text(prompt, system="You write tailored cover letters for remote tech roles.")
    if not letter:
        letter = _fallback_cover_letter(state)
    return {**state, "cover_letter": letter}


async def tailor_resume_content(state: TailoringState) -> TailoringState:
    prompt = f"""Tailor this resume for the job. Return JSON only:
{{
  "tailored_summary": "<2-3 sentence professional summary>",
  "bullet_highlights": ["<achievement bullet>", ...],
  "skills_to_emphasize": ["<skill>", ...]
}}

Job: {state.get('job_title')} at {state.get('company')}
Description: {(state.get('job_description') or '')[:2500]}
Resume: {(state.get('resume_text') or '')[:3000]}
Target keywords: {state.get('keywords') or state.get('resume_skills') or []}"""

    data = await complete_json(prompt, system="You optimize resumes for ATS and recruiters.")
    if not data:
        skills = state.get("keywords") or state.get("resume_skills") or []
        return {
            **state,
            "tailored_summary": (
                f"Experienced professional targeting the {state.get('job_title')} role at "
                f"{state.get('company')}, emphasizing {', '.join(skills[:5])}."
            ),
            "bullet_highlights": [
                f"Aligned experience with {state.get('job_title')} requirements",
                "Proven delivery in remote, cross-functional environments",
            ],
            "skills_to_emphasize": skills[:8],
        }

    return {
        **state,
        "tailored_summary": str(data.get("tailored_summary", "")),
        "bullet_highlights": list(data.get("bullet_highlights") or [])[:6],
        "skills_to_emphasize": list(data.get("skills_to_emphasize") or [])[:10],
    }


def _fallback_cover_letter(state: TailoringState) -> str:
    name = state.get("candidate_name") or "Applicant"
    title = state.get("job_title", "the role")
    company = state.get("company", "your company")
    skills = ", ".join((state.get("resume_skills") or [])[:5])
    hook = state.get("cover_letter_hook") or f"I am excited to apply for {title}."

    return f"""Dear Hiring Manager,

{hook}

My background includes strengths in {skills or 'software development and collaboration'}, which align closely with the {title} position at {company}. I am motivated by remote teams that value ownership, clear communication, and measurable impact.

I would welcome the opportunity to discuss how my experience can support your goals. Thank you for your consideration.

Best regards,
{name}"""


def build_tailoring_graph():
    graph = StateGraph(TailoringState)
    graph.add_node("analyze_job", analyze_job)
    graph.add_node("draft_cover_letter", draft_cover_letter)
    graph.add_node("tailor_resume", tailor_resume_content)
    graph.set_entry_point("analyze_job")
    graph.add_edge("analyze_job", "draft_cover_letter")
    graph.add_edge("draft_cover_letter", "tailor_resume")
    graph.add_edge("tailor_resume", END)
    return graph.compile()


async def run_tailoring_pipeline(
    resume_text: str,
    resume_skills: list[str],
    candidate_name: str,
    job_title: str,
    company: str,
    job_description: str,
    keywords: list[str] | None = None,
    cover_letter_hook: str = "",
) -> TailoringState:
    graph = build_tailoring_graph()
    initial: TailoringState = {
        "resume_text": resume_text,
        "resume_skills": resume_skills,
        "candidate_name": candidate_name,
        "job_title": job_title,
        "company": company,
        "job_description": job_description,
        "keywords": keywords or resume_skills,
        "cover_letter_hook": cover_letter_hook,
    }
    return await graph.ainvoke(initial)
