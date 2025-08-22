import os
from typing import List
from openai import OpenAI
from app.core.config import settings
from app.models.dto import Turn
from app.services.analysis import redact

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _to_messages(turns: List[Turn]):
    msgs = [{"role": "system", "content": (
        "You are a supportive, kid-friendly helper (ages 6–14). "
        "Use short sentences, validate feelings, suggest simple, safe coping games. "
        "Never provide medical advice. Avoid PII. Keep it cheerful and calming."
    )}]
    for t in turns:
        msgs.append({"role": t.role, "content": redact(t.content)})
    return msgs

def chat_reply(turns: List[Turn]) -> str:
    api_key = settings.OPENAI_API_KEY
    last = next((t.content for t in reversed(turns) if t.role == "user"), "")
    if not api_key:
        return f"Thanks for sharing! I'm here with you. You said: {redact(last)}"

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=_to_messages(turns),
        temperature=0.4,
        max_tokens=250,
    )
    return resp.choices[0].message.content.strip()
