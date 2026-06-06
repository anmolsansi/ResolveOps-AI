# ResolveOps AI

AI-powered support intelligence platform that ingests historical support tickets, enables RAG-based question answering with citations, and provides ingestion quality and retrieval metrics dashboards.

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL   │
│  React + TS  │     │   FastAPI    │     │   Database    │
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

## Troubleshooting

- **Backend won't start**: Ensure PostgreSQL is running and `DATABASE_URL` is correct
- **Frontend API errors**: Check that the backend is running on port 8000 and CORS is enabled
- **Migration errors**: Run `alembic upgrade head` from the `backend/` directory
- **Mock provider**: No API key needed — the app uses deterministic mock providers by default

## Known Limitations

This is a portfolio MVP, not a production-grade deployment. Current gaps:

- No authentication or authorization
- No production support-tool integrations (e.g. Zendesk, Freshdesk, Intercom); ingestion is CSV-only
- No background job queue — CSV processing and embedding generation run inline in the request
- No cloud deployment configuration
- Vector similarity uses cosine similarity on JSON-stored embeddings (not pgvector)
- `mypy` is non-blocking in CI (`python -m mypy app || true`), so type errors do not fail the build; making it blocking is planned
- Mock providers return deterministic (not AI-generated) answers by default
- No real-time updates (polling only)
- No drag-and-drop file upload
