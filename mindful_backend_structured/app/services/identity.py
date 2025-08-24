import datetime
import secrets
from typing import Dict, Any, List
from app.services.supabase import sb_get, sb_post, sb_patch

def iso(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"

async def ensure_parent(user_id: str) -> str:
    rows = await sb_get("parents", {"select": "id", "user_id": f"eq.{user_id}"})
    if rows:
        return rows[0]["id"]
    await sb_post("parents", [{"user_id": user_id}])
    rows = await sb_get("parents", {"select": "id", "user_id": f"eq.{user_id}"})
    return rows[0]["id"]

async def ensure_child(user_id: str, display_name: str) -> str:
    rows = await sb_get("children", {"select": "id", "user_id": f"eq.{user_id}"})
    if rows:
        return rows[0]["id"]
    await sb_post("children", [{"user_id": user_id, "display_name": display_name}])
    rows = await sb_get("children", {"select": "id", "user_id": f"eq.{user_id}"})
    return rows[0]["id"]

async def create_link_code(parent_id: str, ttl_minutes: int = 1440) -> Dict[str, str]:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = "".join(secrets.choice(alphabet) for _ in range(6))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl_minutes)
    # Insert into link_codes, not family_links
    await sb_post("link_codes", [{
        "code": code,
        "parent_id": parent_id,
        "expires_at": iso(expires_at),
        "consumed": False
    }])
    return {"code": code, "expires_at": iso(expires_at)}

async def consume_link_code(code: str, child_id: str) -> Dict[str, Any]:
    links = await sb_get("link_codes", {"select": "code,parent_id,expires_at,consumed", "code": f"eq.{code}"})
    if not links:
        raise ValueError("Invalid code")
    lk = links[0]
    now_iso = iso(datetime.datetime.utcnow())
    if lk.get("consumed"):
        raise ValueError("Code already used")
    if lk["expires_at"] < now_iso:
        raise ValueError("Code expired")

    parent_id = lk["parent_id"]

    # Mark code as consumed
    await sb_patch("link_codes", {"code": f"eq.{code}"}, {"consumed": True})

    # Insert into family_links now that child exists
    await sb_post("family_links", [{
        "id": secrets.token_hex(16),
        "parent_id": parent_id,
        "child_id": child_id,
        "code": code,
        "expires_at": lk["expires_at"],
        "created_at": iso(datetime.datetime.utcnow())
    }])

    # Optionally, update the child row to link to parent
    await sb_patch("children", {"id": f"eq.{child_id}"}, {"parent_id": parent_id})

    return {"parent_id": parent_id}

async def list_children_for_parent(parent_id: str) -> List[Dict[str, Any]]:
    return await sb_get("children", {"select": "id,display_name", "parent_id": f"eq.{parent_id}"})
