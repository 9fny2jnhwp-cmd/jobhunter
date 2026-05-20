import json
import re

from app.config import get_settings


async def complete_text(prompt: str, system: str = "", max_tokens: int = 2048) -> str | None:
    """Call Claude or OpenAI for plain-text prose. Returns None if unavailable."""
    settings = get_settings()

    if settings.anthropic_api_key:
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens,
                system=system or "You are a professional career coach.",
                messages=[{"role": "user", "content": prompt}],
            )
            if msg.content:
                return msg.content[0].text.strip()
        except Exception:
            pass

    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system or "You are a professional career coach."},
                    {"role": "user", "content": prompt},
                ],
            )
            text = resp.choices[0].message.content
            return text.strip() if text else None
        except Exception:
            pass

    return None


async def complete_json(prompt: str, system: str = "") -> dict | None:
    """Call Claude or OpenAI and parse JSON from the response. Returns None if unavailable."""
    settings = get_settings()

    if settings.anthropic_api_key:
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1024,
                system=system or "Respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text if msg.content else ""
            return _parse_json(text)
        except Exception:
            pass

    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system or "Respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            text = resp.choices[0].message.content or ""
            return _parse_json(text)
        except Exception:
            pass

    return None


def _parse_json(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None
