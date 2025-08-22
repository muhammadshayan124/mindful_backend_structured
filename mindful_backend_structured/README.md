# Mindful Backend — Structured (FastAPI + Supabase)

Production-ready, **modular** backend for your child therapeutic chatbot + parent analytics. 
This version splits the code into clear packages (core, deps, models, routes, services).

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then edit values
uvicorn app.main:app --reload --port 8000
```

Health check: http://localhost:8000/healthz

## Deploy (Railway)

Add env vars from .env.example in Railway → Variables

Railway uses the included Procfile:

```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Postman

Import `postman_collection.json`. Set collection variables:
- `baseUrl` → your server URL
- `token` → Supabase access token (parent/child)
- `childId` → the child's UUID after you link

## Structure

```
app/
  core/        # config, logging
  deps/        # dependencies (auth)
  models/      # Pydantic DTOs
  routes/      # API routes (health, chat, ingest, parent, linking, admin)
  services/    # supabase, analysis, openai, identity
  main.py      # app factory, CORS, request-id, router mounting
migrations/    # SQL schema + indexes
Procfile
Dockerfile
requirements.txt
.env.example
postman_collection.json
```
