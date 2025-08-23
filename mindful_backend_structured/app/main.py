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

# CORS
origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins #or ["http://localhost:5173", "http://127.0.0.1:5173"]
    ,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request-ID middleware
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response

app.add_middleware(RequestIdMiddleware)

# Routers
app.include_router(health.router, prefix="")
app.include_router(chat.router, prefix="")
app.include_router(ingest.router, prefix="")
app.include_router(parent.router, prefix="")
app.include_router(linking.router, prefix="")
app.include_router(admin.router, prefix="")

