from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Dict, Any, List
from app.deps.auth import supabase_user
from app.models.dto import ChatIn, ChatOut, Turn
from app.services.analysis import analyze_sentiment, triage_text, summarize_user_text, redact
from app.services.openai_llm import chat_reply
from app.services.supabase import sb_post

router = APIRouter(tags=["chat"])

def normalize(body: Dict[str, Any]) -> ChatIn:
    if "child_id" in body and "turns" in body:
        return ChatIn(**body)
    if "childId" in body and "messages" in body:
        return ChatIn(child_id=str(body["childId"]), turns=[Turn(**m) for m in body["messages"]])
    if "user_input" in body and "conversation_id" in body:
        return ChatIn(child_id=str(body["conversation_id"]), turns=[Turn(role="user", content=str(body["user_input"]))])
    raise HTTPException(400, "Unrecognized chat payload")

async def persist_chat(child_id: str, turns: List[Turn], reply: str, sentiment: float, triage: str):
    rows = []
    for t in turns:
        if t.role == "user":
            rows.append({"child_id": child_id, "role": "user", "content": redact(t.content),
                        "sentiment": await analyze_sentiment(t.content), "triage_level": await triage_text(t.content)})
    rows.append({"child_id": child_id, "role": "assistant", "content": reply,
                "sentiment": sentiment, "triage_level": triage})
    if rows: 
        await sb_post("chat_messages", rows)

@router.post("/api/chat", response_model=ChatOut)
@router.post("/chat", response_model=ChatOut)
async def chat(request: Request, user=Depends(supabase_user)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")

    chat_data = normalize(body)
    if len(chat_data.turns) > 12: 
        raise HTTPException(400, "Too many turns (max 12)")
    if sum(len(t.content) for t in chat_data.turns) > 6000: 
        raise HTTPException(400, "Conversation too long (max 6000 chars)")

    reply = chat_reply(chat_data.turns)
    child_text = await summarize_user_text(chat_data.turns)
    sentiment = await analyze_sentiment(child_text)
    triage = await triage_text(child_text)

    try:
        await persist_chat(chat_data.child_id, chat_data.turns, reply, sentiment, triage)
    except Exception as e:
        print("persist chat error:", e)

    return ChatOut(reply=reply, sentiment=sentiment, triage=triage)
