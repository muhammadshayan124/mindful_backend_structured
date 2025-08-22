from typing import List, Literal, Optional
from pydantic import BaseModel, Field, constr

Role = Literal["user", "assistant"]
Triage = Literal["none", "low", "medium", "high"]

class Turn(BaseModel):
    role: Role
    content: constr(min_length=1, max_length=3000)

class ChatIn(BaseModel):
    child_id: str
    turns: List[Turn] = Field(min_length=1, max_length=12)

class ChatOut(BaseModel):
    reply: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    triage: Triage

class MoodIn(BaseModel):
    child_id: str
    mood: Literal["very_sad", "sad", "neutral", "happy", "very_happy"]
    note: Optional[constr(max_length=600)] = None

class JournalIn(BaseModel):
    child_id: str
    text: constr(min_length=1, max_length=4000)

class GameIn(BaseModel):
    child_id: str
    activity: constr(min_length=1, max_length=200)
    delta: int = 0

class LinkCodeCreateOut(BaseModel):
    code: str
    expires_at: str

class LinkCodeConsumeIn(BaseModel):
    code: str
    display_name: constr(min_length=1, max_length=80)

class ParentChild(BaseModel):
    child_id: str
    display_name: str

class DayPoint(BaseModel):
    day: str
    avg_sentiment: float
    high_risk_count: int
    wellbeing: int

class ChildOverview(BaseModel):
    child_id: str
    name: str
    risk: Triage
    last_7_days: List[DayPoint]

class ParentOverview(BaseModel):
    children: List[ChildOverview]
