from fastapi import Header, HTTPException
import httpx
from app.core.config import settings

async def supabase_user(Authorization: str = Header(...)):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = Authorization.split(" ", 1)[1]
    async with httpx.AsyncClient(base_url=settings.SUPABASE_URL, headers={
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
    }, timeout=20.0) as c:
        r = await c.get("/auth/v1/user", headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            raise HTTPException(401, "Invalid token")
        return r.json()

def user_id_from(user: dict) -> str:
    return user.get("id") or user.get("user", {}).get("id")
