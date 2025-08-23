# app/core/config.py
import os
from pydantic import BaseModel

class Settings(BaseModel):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # ✅ use your Railway var name
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", "")  # comma-separated list
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
