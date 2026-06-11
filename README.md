# ResolveOps AI

[![CI](https://github.com/anmolsansi/ResolveOps-AI/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/anmolsansi/ResolveOps-AI/actions/workflows/ci.yml)

AI-powered support intelligence platform that ingests historical support tickets, enables RAG-based question answering with citations, and provides ingestion quality and retrieval metrics dashboards.

## V1 MVP Validation

V1 is considered complete when the CI workflow is green and the Docker smoke path passes from a clean startup.

V1 smoke coverage:

- Backend health check
- Frontend React shell reachability
- CSV upload with valid rows, invalid rows, duplicate tracking, chunking, and embeddings
- Ticket list and ticket detail with chunk previews
- RAG query with citations, confidence, latency, cost, query ID, and quality scores
- Low-confidence RAG fallback with no citations
- Dashboard quality and retrieval metrics
- Eval run creation and listing
- Docker startup with Alembic migrations before Uvicorn

Run V1 validation locally:

```bash
docker compose down -v
docker compose up -d --build
python3 scripts/wait_for_api.py
python3 scripts/generate_sample_tickets.py --count 80 --include-invalid
python3 scripts/v1_api_smoke.py --base-url http://localhost:8000 --frontend-url http://localhost:5173 --csv scripts/sample_tickets.csv
```

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  React + TS  │     │   FastAPI    │     │   Database   │
│  Vite dev    │     │   Uvicorn    │     │              │
│  port 5173   │     │   port 8000  │     │   port 5432  │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────┴─────┐
                     │ Providers │
                     │ Mock/Real │
                     └───────────┘
```

## Folder Structure

```
backend/           FastAPI backend application
  app/
    api/           API route handlers
    core/          Config and database setup
    models/        SQLAlchemy models
    schemas/       Pydantic request/response schemas
    services/      Business logic and providers
  alembic/         Database migrations
  tests/           Backend tests
frontend/          React TypeScript frontend
  src/
    api/           API client and types
    components/    Shared UI components
    pages/         Page components
scripts/           Utility scripts
docker-compose.yml Docker Compose for local development
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://resolveops:resolveops@localhost:5432/resolveops` |
| `BACKEND_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | Frontend dev server port | `5173` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | empty |
| `LLM_PROVIDER` | LLM provider (`mock` or `openai`) | `mock` |
| `EMBEDDING_PROVIDER` | Embedding provider (`mock` or `openai`) | `mock` |
| `MOCK_PROVIDERS` | Force mock providers | `true` |
| `VITE_API_BASE_URL` | Backend URL for frontend | `http://localhost:8000` |
| `SECRET_KEY` | HMAC signing key for access tokens | `dev-insecure-change-me` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (minutes) | `720` |
| `AUTH_REQUIRED` | Reserved flag for gating (V5 governance endpoints always require a token) | `false` |
| `VECTOR_BACKEND` | Retrieval backend: `auto`, `pgvector`, or `memory` | `auto` |
| `PII_REDACTION_ENABLED` | Redact PII on ingestion (also runtime-configurable) | `false` |
| `RETENTION_RAG_QUERY_DAYS` | RAG query retention window in days (`0` = keep forever) | `0` |
| `RETENTION_AUDIT_LOG_DAYS` | Audit log retention window in days (`0` = keep forever) | `0` |

## Local Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+

### Database

```bash
# Create database
createdb resolveops
# Or with Docker for just the database:
docker run -d --name resolveops-db -p 5432:5432 \
  -e POSTGRES_DB=resolveops \
  -e POSTGRES_USER=resolveops \
  -e POSTGRES_PASSWORD=resolveops \
  postgres:16-alpine
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Local Setup (With Docker)

```bash
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: localhost:5432

## Sample Data

Generate sample support tickets:

```bash
python scripts/generate_sample_tickets.py
# Custom count:
python scripts/generate_sample_tickets.py --count 100
# Include intentionally invalid rows:
python scripts/generate_sample_tickets.py --include-invalid
```

Output: `scripts/sample_tickets.csv`

## Demo Flow

1. **Start services** (Docker or local setup above)
2. **Generate sample CSV**: `python scripts/generate_sample_tickets.py`
3. **Upload CSV**: Go to http://localhost:5173/upload and upload the CSV
4. **View quality metrics**: Check http://localhost:5173/ for ingestion stats
5. **Browse tickets**: Navigate to http://localhost:5173/tickets
6. **Ask a RAG question**: Go to http://localhost:5173/rag and ask "How to fix a billing error?" — confirm cited ticket IDs are shown
7. **Test low-confidence**: Ask an unrelated question like "What is quantum physics?" — confirm the not-enough-context response
8. **Run an eval**: Go to http://localhost:5173/eval and click "Run Eval"
9. **View metrics**: Return to dashboard to see retrieval metrics updated

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/tickets/upload` | Upload CSV of support tickets |
| `GET` | `/tickets` | List tickets with filters and pagination |
| `GET` | `/tickets/{id}` | Get ticket detail with chunk previews |
| `POST` | `/rag/query` | Ask a question with optional filters (returns quality scores) |
| `POST` | `/rag/queries/{id}/feedback` | Submit human feedback (helpful / not_helpful / wrong_citation) |
| `GET` | `/dashboard/quality` | Ingestion quality metrics |
| `GET` | `/dashboard/retrieval` | RAG retrieval metrics + latency p50/p95/p99 + quality averages |
| `GET` | `/dashboard/cost` | Cost tracking broken down by provider/model |
| `GET` | `/dashboard/quality-by-area` | Answer-quality breakdown per product area |
| `GET` | `/dashboard/failed-queries` | Failed-query review queue (low confidence / no citations / negative feedback) |
| `POST` | `/eval/run` | Run evaluation with default or custom questions |
| `POST` | `/eval/compare` | Regression eval comparing two retrieval/generation configs |
| `GET` | `/eval/runs` | List past evaluation runs |
| `POST` | `/connectors` | Register a Zendesk/Freshdesk/Intercom connector |
| `GET` | `/connectors` | List connectors |
| `DELETE` | `/connectors/{id}` | Delete a connector and its jobs |
| `POST` | `/connectors/{id}/sync` | Incremental (cursor-based) sync from a connector |
| `POST` | `/connectors/{id}/jobs` | Schedule a recurring ingestion job |
| `GET` | `/connectors/jobs` | List scheduled ingestion jobs |
| `POST` | `/connectors/jobs/run-due` | Run all due scheduled jobs |
| `GET` | `/connectors/duplicates` | Semantic duplicate clusters across tickets |
| `POST` | `/assist/draft` | Suggested reply + escalation + tier guidance for a live ticket |
| `POST` | `/kb/generate` | Generate KB articles from resolved tickets |
| `GET` | `/kb/articles` | List generated KB articles |
| `GET` | `/sla/risks` | Open tickets ranked by SLA breach risk |
| `POST` | `/auth/register` | Register a user (first user becomes admin) |
| `POST` | `/auth/login` | Log in, returns a signed access token |
| `GET` | `/auth/me` | Current authenticated user |
| `GET` | `/auth/users` · `PUT /auth/users/{id}/role` | List users / change role (admin) |
| `GET`/`POST` | `/workspaces` · `/workspaces/{id}/members` | Workspaces and membership management |
| `GET` | `/audit` | Audit log of governance events (admin) |
| `POST` | `/pii/scan` | Detect and redact PII in text |
| `GET`/`PUT` | `/settings` | Read / update runtime model & governance settings |
| `GET` | `/settings/vector-backend` | Active retrieval backend (pgvector vs memory) |
| `GET`/`POST` | `/retention` · `/retention/run` | Preview / execute retention purge (admin) |
| `GET`/`POST` | `/prompts` · `/prompts/{id}/activate` | Versioned prompt management |
| `GET`/`POST` | `/jobs` · `/jobs/process-pending` | Background job queue (ingestion/embeddings) |

### Enterprise (V5)

Security, scale, and governance:

- **Auth + RBAC**: stdlib PBKDF2 password hashing and HMAC-signed access tokens; global roles (admin / member / viewer). The first registered user becomes admin. Surfaced in the **Account** page. Core demo endpoints stay open; V5 governance endpoints require a token.
- **Workspaces/teams**: per-workspace membership and roles. Surfaced in the **Workspaces** page.
- **Audit logs**: immutable record of logins, role changes, settings updates, retention runs, and prompt changes. Surfaced in the **Audit** page.
- **PII detection & redaction**: regex-based detection (email, phone, SSN, credit card, IP) with redaction, optionally applied on ingestion. Surfaced in the **PII** page.
- **Configurable retention**: per-resource retention windows for RAG queries and audit logs, with preview and purge. Surfaced in **Settings**.
- **pgvector-backed retrieval**: indexed nearest-neighbour search on PostgreSQL when the `vector` extension and package are available, with transparent in-memory cosine fallback otherwise (`VECTOR_BACKEND=auto`).
- **Background job queue**: in-process queue with handlers for embedding backfill, retention runs, PII redaction, and connector sync. Surfaced in the **Jobs** page.
- **Model/provider settings**: runtime provider/model/threshold configuration. Surfaced in **Settings**.
- **Prompt/version management**: versioned system prompts with single-active selection, applied to RAG and Assist answers. Surfaced in the **Prompts** page.
- **Cloud deployment**: one-command [Render](./DEPLOY.md) blueprint (`render.yaml`) provisioning Postgres + backend + frontend.

### Workflow integration (V4)

Makes the platform useful for real support teams:

- **Connectors**: pluggable Zendesk / Freshdesk / Intercom import abstraction with deterministic mock sources (real providers slot in via API credentials). Surfaced in the **Connectors** page.
- **Scheduled ingestion + incremental sync**: connectors track a cursor so each sync imports only new tickets; recurring jobs run on an interval via `/connectors/jobs/run-due`.
- **Semantic de-duplication**: tickets are de-duplicated on import (cosine similarity over embeddings) and near-duplicate clusters are surfaced for review.
- **Live ticket assist**: grounded suggested reply, an escalation recommendation (answer / ask clarification / route to human), customer-tier-aware guidance, and separate customer-facing vs. internal-note modes. Surfaced in the **Assist** page.
- **Knowledge base generation**: resolved tickets are clustered by product area + issue type into KB articles with common resolution steps. Surfaced in the **Knowledge Base** page.
- **SLA risk detection**: open tickets are scored for SLA breach risk (priority- and tier-weighted). Surfaced in the **SLA Risk** page.

### Reliability platform (V3)

Beyond RAG, the app scores and observes answer quality:

- **Answer-quality metrics** computed per query with deterministic token-overlap heuristics (work in mock mode, no model calls): hallucination risk, citation coverage, retrieval precision, answer completeness.
- **Observability**: cost tracking by provider/model, latency percentiles (p50/p95/p99), per-product-area quality breakdown.
- **Human-in-the-loop**: feedback buttons (helpful / not helpful / wrong citation) and a failed-query review queue.
- **Regression testing**: compare two configs (top-k / threshold) side by side via `/eval/compare`.

These are surfaced in the **Reliability** page in the frontend.

## Test and Validation Commands

### Backend

```bash
cd backend
source .venv/bin/activate

# Run tests
python -m pytest -v

# Lint
python -m ruff check .

# Type check
python -m mypy app || true
```

### Frontend

```bash
cd frontend

# Build
npm run build

# Lint
npm run lint

# Type check
npm run typecheck
```

### Docker Smoke Validation

```bash
python3 scripts/v1_api_smoke.py --base-url http://localhost:8000 --frontend-url http://localhost:5173 --csv scripts/sample_tickets.csv
python3 scripts/v3_api_smoke.py --base-url http://localhost:8000 --csv scripts/sample_tickets.csv
```

## Troubleshooting

- **Backend won't start**: Ensure PostgreSQL is running and `DATABASE_URL` is correct
- **Frontend API errors**: Check that the backend is running on port 8000 and CORS is enabled
- **Migration errors**: Run `alembic upgrade head` from the `backend/` directory
- **Mock provider**: No API key needed — the app uses deterministic mock providers by default

## Known Limitations

This is a portfolio project. V5 adds enterprise-grade auth/RBAC, workspaces,
audit logs, PII redaction, retention, pgvector-backed retrieval, a background
job queue, and a Render deployment blueprint. Remaining gaps:

- Support-tool connectors (Zendesk/Freshdesk/Intercom) ship with deterministic **mock** sources for demo; wiring real vendor APIs requires adding credentials and the live `fetch_since` implementation
- Scheduled ingestion jobs and the background job queue run when triggered (`/connectors/jobs/run-due`, `/jobs/process-pending`); there is no always-on worker/scheduler process yet
- pgvector retrieval activates only on PostgreSQL with the `vector` extension + package installed; SQLite and key-less demo runs use the in-memory cosine fallback
- `auth_required` is wired for V5 governance endpoints; core demo endpoints (tickets, RAG, dashboard) remain open so the demo works key-less
- `mypy` is non-blocking in CI (`python -m mypy app || true`), so type errors do not fail the build; making it blocking is planned
- Mock providers return deterministic (not AI-generated) answers by default
- No real-time updates (polling only)
- No drag-and-drop file upload
