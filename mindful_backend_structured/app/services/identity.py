import datetime
import secrets
from typing import Dict, Any, List
from app.services.supabase import sb_get, sb_post, sb_patch

def iso(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"

# Ensure the parent exists and return parent_id
async def ensure_parent(user_id: str) -> str:
    rows = await sb_get("profiles", {"select": "id", "id": f"eq.{user_id}"})
    if rows:
        return rows[0]["id"]
    # Insert parent into profiles table
    await sb_insert("profiles", [{"id": user_id}])
    rows = await sb_get("profiles", {"select": "id", "id": f"eq.{user_id}"})
    return rows[0]["id"]

# Ensure the child exists and return child_id
async def ensure_child(user_id: str, display_name: str) -> str:
    rows = await sb_get("children", {"select": "id", "user_id": f"eq.{user_id}"})
    if rows:
        return rows[0]["id"]
    await sb_insert("children", [{"user_id": user_id, "display_name": display_name}])
    rows = await sb_get("children", {"select": "id", "user_id": f"eq.{user_id}"})
    return rows[0]["id"]

# Create a new link code for a parent
async def create_link_code(user_id: str, ttl_minutes: int = 1440) -> Dict[str, str]:
    parent_id = await ensure_parent(user_id)
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = "".join(secrets.choice(alphabet) for _ in range(6))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl_minutes)
    
    await sb_insert("link_codes", [{
        "code": code,
        "parent_id": parent_id,
        "expires_at": iso(expires_at),
        "consumed": False
    }])

    return {"code": code, "expires_at": iso(expires_at)}

# Consume a link code for a child
async def consume_link_code(code: str, child_id: str) -> Dict[str, Any]:
    # Fetch link code
    link = await sb_get("link_codes", {
        "select": "code,parent_id,expires_at,consumed",
        "code": f"eq.{code}"
    })
    if not link:
        raise ValueError("Invalid code")
    
    lk = link[0]
    now_iso = iso(datetime.datetime.utcnow())

    if lk.get("consumed"):
        raise ValueError("Code already used")
    if lk["expires_at"] < now_iso:
        raise ValueError("Code expired")

    # Mark code as consumed
    await sb_update("link_codes", {"code": f"eq.{code}"}, {"consumed": True})

    # Link child to parent
    await sb_update("children", {"id": f"eq.{child_id}"}, {"parent_id": lk["parent_id"]})

    return {"parent_id": lk["parent_id"]}

# List children for a parent
async def list_children_for_parent(parent_id: str) -> List[Dict[str, Any]]:
    return await sb_get("children", {"select": "id,display_name", "parent_id": f"eq.{parent_id}"})
