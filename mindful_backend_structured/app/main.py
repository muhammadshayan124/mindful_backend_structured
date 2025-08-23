import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routes import health, chat, ingest, parent, linking, admin

setup_logging(settings.LOG_LEVEL)

app = FastAPI(title="Mindful Backend", version="1.0.0")

# ---------- CORS ----------
# Read allowed origins from env FRONTEND_ORIGINS as a comma-separated list.
# Example:
# FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://172.16.2.44:8080,https://your.lovable.dev
origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]

if origins:
    # Production-friendly: explicit list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,      # exact origins
        allow_credentials=True,     # we send Authorization bearer tokens
        allow_methods=["*"],        # includes OPTIONS for preflight
        allow_headers=["*"],        # includes Authorization, Content-Type, etc.
        expose_headers=["X-Request-Id"],  # optional, handy for tracing
    )
else:
    # Debug fallback: allow any origin by echoing it back (NOT "*" + credentials)
    # Use only if you haven't set FRONTEND_ORIGINS yet.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",    # echoes the Origin if it matches
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-Id"],
    )

# ---------- Request-ID middleware ----------
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response

app.add_middleware(RequestIdMiddleware)

# ---------- Routers ----------
app.include_router(health.router, prefix="")
app.include_router(chat.router, prefix="")
app.include_router(ingest.router, prefix="")
app.include_router(parent.router, prefix="")
app.include_router(linking.router, prefix="")
app.include_router(admin.router, prefix="")
