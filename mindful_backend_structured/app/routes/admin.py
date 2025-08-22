from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.deps.auth import supabase_user
from app.services.supabase import sb_get, sb_post

router = APIRouter(tags=["admin"])

@router.post("/api/admin/recompute")
async def recompute_daily(user=Depends(supabase_user)):
    cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
    ids = set()
    for t in ("chat_messages", "journals"):
        rows = await sb_get(t, {"select": "child_id", "created_at": "gte." + cutoff})
        ids |= {r["child_id"] for r in rows if r.get("child_id")}

    rows_out = []
    for cid in ids:
        chats = await sb_get("chat_messages", {"select": "created_at,sentiment,triage_level", "child_id": "eq." + cid, "created_at": "gte." + cutoff})
        journals = await sb_get("journals", {"select": "created_at,sentiment", "child_id": "eq." + cid, "created_at": "gte." + cutoff})
        by_day = {}
        for m in chats:
            d = m["created_at"][:10]
            by_day.setdefault(d, {"sents": [], "risk": 0})
            if m.get("sentiment") is not None: 
                by_day[d]["sents"].append(float(m["sentiment"]))
            if m.get("triage_level") in ("medium", "high"): 
                by_day[d]["risk"] += 1
        for j in journals:
            d = j["created_at"][:10]
            by_day.setdefault(d, {"sents": [], "risk": 0})
            if j.get("sentiment") is not None: 
                by_day[d]["sents"].append(float(j["sentiment"]))
        for day, agg in by_day.items():
            avg = (sum(agg["sents"]) / len(agg["sents"])) if agg["sents"] else 0.0
            wellbeing = max(0, min(100, round(((avg + 1) / 2) * 70 + 30)))
            rows_out.append({"child_id": cid, "day": day, "avg_sentiment": avg, "high_risk_count": agg["risk"], "wellbeing_score": wellbeing})

    if rows_out:
        await sb_post("sentiment_daily", rows_out)
    return {"ok": True, "children": len(ids)}
