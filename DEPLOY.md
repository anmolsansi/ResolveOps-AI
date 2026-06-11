# Deploying ResolveOps AI

This guide covers deploying ResolveOps AI to a single cloud target —
[Render](https://render.com) — using the included [`render.yaml`](./render.yaml)
blueprint. Render is free to start, supports managed PostgreSQL (with the
`pgvector` extension), and builds the backend straight from the existing
Dockerfile, so no Kubernetes is required.

## What the blueprint provisions

| Component | Render service | Notes |
| --- | --- | --- |
| Database | `resolveops-db` (PostgreSQL 16) | `DATABASE_URL` is injected into the backend |
| Backend | `resolveops-backend` (Docker web service) | Runs `alembic upgrade head` on boot via `backend/entrypoint.sh`, then Uvicorn on port 8000; health-checked at `/health` |
| Frontend | `resolveops-frontend` (static site) | `npm ci && npm run build`, served from `frontend/dist` with SPA rewrite |

## One-time deploy

1. Push this repository to GitHub/GitLab.
2. In Render: **New → Blueprint**, select the repo. Render reads `render.yaml`.
3. Approve the plan. Render creates the database, backend, and frontend.
4. When the backend is live, copy its URL (e.g.
   `https://resolveops-backend.onrender.com`) and set the frontend's
   `VITE_API_BASE_URL` env var to it, then trigger a frontend redeploy. The
   frontend is a build-time static bundle, so it must bake in the full backend
   URL (including `https://`).

## Configuration (env vars)

The backend reads these (all optional; sensible defaults shipped):

| Var | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | local Postgres | Connection string. Bare `postgres://` / `postgresql://` URLs are auto-coerced onto the psycopg v3 driver. |
| `SECRET_KEY` | dev placeholder | HMAC signing key for access tokens. **Generated automatically** by the blueprint. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `720` | Token lifetime. |
| `AUTH_REQUIRED` | `false` | Reserved flag; V5 governance endpoints always require a token, core endpoints stay open for the demo. |
| `VECTOR_BACKEND` | `auto` | `auto` uses pgvector on Postgres when the extension + package are present, else in-memory cosine fallback. Force with `pgvector` or `memory`. |
| `MOCK_PROVIDERS` | `true` | Keep `true` for a key-less demo. Set `false` + `OPENAI_API_KEY` for real embeddings/answers. |
| `LLM_PROVIDER` / `EMBEDDING_PROVIDER` | `mock` | Set to `openai` for production answers. |
| `OPENAI_API_KEY` | empty | Required only when `MOCK_PROVIDERS=false`. |

## Enabling pgvector in production

Render's managed Postgres supports `pgvector`. Migration `005` runs
`CREATE EXTENSION IF NOT EXISTS vector` (guarded — it is a no-op on SQLite and
where the extension is unavailable). With the extension enabled and the
`pgvector` Python package installed, `VECTOR_BACKEND=auto` will use indexed
nearest-neighbour retrieval; otherwise it transparently falls back to in-memory
cosine similarity. Check the live status at **Settings → Retrieval backend** in
the UI or `GET /settings/vector-backend`.

## Local production-like run

```bash
docker compose up --build
# backend  → http://localhost:8000  (migrations run automatically)
# frontend → http://localhost:5173
# db       → postgres:16 on 5432
```

## First login

The **first** account registered (UI: *Account* page, or `POST /auth/register`)
becomes a global **admin**. Subsequent self-registrations are `member`s; admins
manage roles, settings, retention, prompts, and audit logs.
