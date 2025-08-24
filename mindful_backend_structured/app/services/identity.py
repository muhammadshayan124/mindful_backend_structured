import uuid
import datetime
from app.deps.supabase import supabase

# Ensure the user is a parent
async def ensure_parent(user_id: str) -> str:
    # In your case, a parent is just a supabase user id
    # You could enforce "role = parent" if you store it elsewhere
    return user_id

# Ensure the user is a child
async def ensure_child(user_id: str, display_name: str) -> str:
    # Similar, but ensure a "child" row exists
    # For now, just return uid. If you store children separately, insert/find here
    return user_id

# Create a new link code for a parent
async def create_link_code(parent_id: str, ttl_minutes: int = 1440) -> dict:
    code = str(uuid.uuid4())[:8]  # short random code
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(minutes=ttl_minutes)

    # Insert into LinkCodes
    result = supabase.table("LinkCodes").insert({
        "code": code,
        "parent_id": parent_id,
        "created_at": now.isoformat(),
        "expired_at": expires_at.isoformat(),
        "consumed": False
    }).execute()

    return {
        "code": code,
        "parent_id": parent_id,
        "expired_at": expires_at.isoformat()
    }

# Consume a link code for a child
async def consume_link_code(code: str, child_id: str) -> dict:
    now = datetime.datetime.utcnow()

    # Look up code in LinkCodes
    result = supabase.table("LinkCodes").select("*").eq("code", code).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError("Invalid code")

    code_row = result.data[0]

    if code_row.get("consumed"):
        raise ValueError("Code already used")

    if code_row.get("expired_at") and now > datetime.datetime.fromisoformat(code_row["expired_at"]):
        raise ValueError("Code expired")

    parent_id = code_row["parent_id"]

    # Insert into FamilyLinks
    link_result = supabase.table("FamilyLinks").insert({
        "parent_id": parent_id,
        "child_id": child_id,
        "created_at": now.isoformat(),
        "code": code,
        "expired_at": code_row["expired_at"]
    }).execute()

    # Mark the code as consumed
    supabase.table("LinkCodes").update({"consumed": True}).eq("code", code).execute()

    return {"parent_id": parent_id, "child_id": child_id}
