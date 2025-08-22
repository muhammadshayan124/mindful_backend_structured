from fastapi import APIRouter, Depends
from app.deps.auth import supabase_user
from app.models.dto import MoodIn, JournalIn, GameIn
from app.services.analysis import analyze_sentiment, redact
from app.services.supabase import sb_post

router = APIRouter(tags=["ingest"])

MOOD_MAP = {"very_sad": -2, "sad": -1, "neutral": 0, "happy": 1, "very_happy": 2}

@router.post("/api/ingest/mood")
async def ingest_mood(payload: MoodIn, user=Depends(supabase_user)):
    await sb_post("moods", [{
        "child_id": payload.child_id, "mood": payload.mood,
        "mood_score": MOOD_MAP[payload.mood], "note": payload.note
    }])
    return {"ok": True}

@router.post("/api/ingest/journal")
async def ingest_journal(payload: JournalIn, user=Depends(supabase_user)):
    s = await analyze_sentiment(payload.text)
    await sb_post("journals", [{
        "child_id": payload.child_id, "text": redact(payload.text), "sentiment": s
    }])
    return {"ok": True, "sentiment": s}

@router.post("/api/ingest/game")
async def ingest_game(payload: GameIn, user=Depends(supabase_user)):
    await sb_post("game_events", [{
        "child_id": payload.child_id, "activity": payload.activity, "delta": payload.delta
    }])
    return {"ok": True}
