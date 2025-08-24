import httpx
from typing import Any, Dict, List
from app.core.config import settings

JSON = Dict[str, Any]

async def sb_get(table: str, params: Dict[str, str]) -> List[JSON]:
    async with httpx.AsyncClient(timeout=20.0) as c:
        r = await c.get(
            f"{settings.SUPABASE_URL}/rest/v1/{table}",
            headers={
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            },
            params=params
        )
        if r.status_code != 200:
            raise RuntimeError(f"DB GET {table}: {r.status_code} {r.text}")
        return r.json()

async def sb_post(table: str, rows: List[JSON]):
    async with httpx.AsyncClient(timeout=20.0) as c:
        r = await c.post(
            f"{settings.SUPABASE_URL}/rest/v1/{table}",
            headers={
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json=rows
        )
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(f"DB POST {table}: {r.status_code} {r.text}")

async def sb_patch(table: str, match: Dict[str, str], patch: Dict[str, Any]):
    async with httpx.AsyncClient(timeout=20.0) as c:
        r = await c.patch(
            f"{settings.SUPABASE_URL}/rest/v1/{table}",
            headers={
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            params=match,
            json=patch
        )
        if r.status_code not in (200, 204):
            raise RuntimeError(f"DB PATCH {table}: {r.status_code} {r.text}")

# Aliases for clarity with your identity.py
sb_insert = sb_post
sb_update = sb_patch
