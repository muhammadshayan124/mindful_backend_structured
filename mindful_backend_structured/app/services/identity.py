import uuid
from datetime import datetime
from app.services.supabase import sb_insert, sb_update

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
async def consume_link_code(code: str, child_id: str):
    # 1. Lookup code
    records = await sb_get(
        "link_codes",
        {"select": "code,parent_id,expires_at,consumed", "code": f"eq.{code}"}
    )
    if not records:
        raise ValueError("Invalid code")

    rec = records[0]
    if rec["consumed"]:
        raise ValueError("Code already used")
    if datetime.fromisoformat(rec["expires_at"]) < datetime.utcnow():
        raise ValueError("Code expired")

    parent_id = rec["parent_id"]

    # 2. Mark as consumed
    await sb_update("link_codes", {"consumed": True}, {"code": f"eq.{code}"})

    # 3. Insert into family_links
    await sb_insert("family_links", {
        "id": str(uuid.uuid4()),
        "parent_id": parent_id,
        "child_id": child_id,
        "code": code,
        "expires_at": rec["expires_at"],
        "created_at": datetime.utcnow().isoformat(),
    })

    return {"parent_id": parent_id}


