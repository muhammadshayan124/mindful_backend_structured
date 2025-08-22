from fastapi import APIRouter
import time

router = APIRouter(tags=["health"])

@router.get("/healthz")
async def healthz():
    return {"ok": True, "ts": int(time.time())}
