import re
from typing import List
from app.models.dto import Turn, Triage

PII_RE = re.compile(r"\b(\+?\d{7,13}|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b", re.I)

def redact(text: str) -> str:
    return PII_RE.sub("[redacted]", text)

async def analyze_sentiment(text: str) -> float:
    txt = text.lower()
    if any(w in txt for w in ["suicide", "kill myself", "self harm", "hopeless"]): 
        return -0.9
    if any(w in txt for w in ["sad", "upset", "angry", "hate", "bad"]): 
        return -0.4
    if any(w in txt for w in ["happy", "good", "great", "love", "excited"]): 
        return 0.5
    return 0.05

async def triage_text(text: str) -> Triage:
    txt = text.lower()
    if any(w in txt for w in ["kill myself", "suicide", "self harm", "hurt myself"]): 
        return "high"
    if any(w in txt for w in ["panic", "panic attack", "bully", "bullying", "anxious", "fear", "depressed"]): 
        return "medium"
    return "none"

async def summarize_user_text(turns: List[Turn]) -> str:
    return " ".join(t.content for t in turns if t.role == "user")[-2000:]
