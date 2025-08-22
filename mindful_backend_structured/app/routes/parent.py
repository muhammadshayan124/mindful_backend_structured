from fastapi import APIRouter, Depends, Query
from typing import List
from app.deps.auth import supabase_user, user_id_from
from app.models.dto import ParentChild, ParentOverview, ChildOverview, DayPoint
from app.services.identity import ensure_parent, list_children_for_parent
from app.services.supabase import sb_get

router = APIRouter(tags=["parent"])

@router.get("/api/parent/children", response_model=List[ParentChild])
async def parent_children(user=Depends(supabase_user)):
    parent_id = await ensure_parent(user_id_from(user))
    kids = await list_children_for_parent(parent_id)
    return [{"child_id": r["id"], "display_name": r["display_name"]} for r in kids]

@router.get("/api/parent/overview", response_model=ParentOverview)
async def parent_overview(days: int = Query(7, ge=1, le=30), user=Depends(supabase_user)):
    parent_id = await ensure_parent(user_id_from(user))
    kids = await list_children_for_parent(parent_id)
    result: List[ChildOverview] = []
    for k in kids:
        cid = k["id"]
        pts = await sb_get("sentiment_daily", {
            "select": "day,avg_sentiment,high_risk_count,wellbeing_score",
            "child_id": "eq." + cid, "order": "day.desc", "limit": str(days)
        })
        pts = list(reversed(pts))
        risk = "low"
        if pts:
            last = pts[-1]
            if (last.get("high_risk_count") or 0) > 0: 
                risk = "medium"
            if (last.get("avg_sentiment") or 0) < -0.3: 
                risk = "high"
        result.append(ChildOverview(
            child_id=cid, name=k["display_name"], risk=risk,
            last_7_days=[DayPoint(day=p["day"], avg_sentiment=p.get("avg_sentiment") or 0.0,
                                 high_risk_count=p.get("high_risk_count") or 0,
                                 wellbeing=int(p.get("wellbeing_score") or 0)) for p in pts]
        ))
    return {"children": result}

@router.get("/api/parent/child/{child_id}/timeline")
async def parent_child_timeline(child_id: str, days: int = Query(7, ge=1, le=30), user=Depends(supabase_user)):
    # NOTE: For full production, verify child_id belongs to this parent_id before returning.
    moods = await sb_get("moods", {"select": "created_at,mood,mood_score,note", "child_id": "eq." + child_id, "order": "created_at.desc", "limit": str(days * 10)})
    journals = await sb_get("journals", {"select": "created_at,text,sentiment", "child_id": "eq." + child_id, "order": "created_at.desc", "limit": str(days * 10)})
    chats = await sb_get("chat_messages", {"select": "created_at,role,content,sentiment,triage_level", "child_id": "eq." + child_id, "order": "created_at.desc", "limit": str(days * 20)})
    games = await sb_get("game_events", {"select": "created_at,activity,delta", "child_id": "eq." + child_id, "order": "created_at.desc", "limit": str(days * 20)})
    events = []
    events += [{"type": "mood", **m} for m in moods]
    events += [{"type": "journal", **j} for j in journals]
    events += [{"type": "chat", **c} for c in chats]
    events += [{"type": "game", **g} for g in games]
    return events
