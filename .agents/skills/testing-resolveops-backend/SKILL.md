---
name: testing-resolveops-backend
description: Test the ResolveOps AI backend API end-to-end. Use when verifying RAG, upload, eval, or dashboard changes.
---

# Testing ResolveOps AI Backend

## Local Setup

```bash
cd backend
source .venv/bin/activate  # or: pip install -e ".[dev]"
```

No external credentials needed for mock mode (default).

## Running Tests

```bash
# All tests
python -m pytest -v

# Lint
python -m ruff check .

# Typecheck
python -m mypy app --ignore-missing-imports
```

## E2E Testing via Shell

The backend is a FastAPI API — no UI changes to test visually. Use `TestClient` or `curl` against a local SQLite DB:

```bash
# Quick local backend for manual curl testing
DATABASE_URL="sqlite:///test.db" python -c "
from app.core.database import Base, engine
from app.models.models import *
Base.metadata.create_all(bind=engine)
"
DATABASE_URL="sqlite:///test.db" uvicorn app.main:app --port 8000
```

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/tickets/upload` | POST | Upload CSV (multipart file) |
| `/rag/query` | POST | RAG query with question, filters, top_k |
| `/eval/run` | POST | Run eval with questions list |
| `/dashboard/quality` | GET | Ingestion quality metrics |
| `/dashboard/retrieval` | GET | Retrieval/query metrics |

## Mock Mode Behavior

- Default: `MOCK_PROVIDERS=true`, `EMBEDDING_PROVIDER=mock`
- Mock embeddings use MD5 hashing (deterministic, low cosine similarity ~0.0-0.2)
- **Keyword boost** (mock only): adds 0.4 per matching content keyword to retrieval score
- Confidence threshold: 0.3 (configured in `app/core/config.py`)
- Related queries (keyword overlap with tickets) → confidence ≥ 0.3 → cited answer
- Unrelated queries (no keyword overlap) → confidence < 0.3 → fallback answer
- Cross-domain queries might match if tickets share vocabulary (e.g., "error" appears in both login and billing tickets)

## Testing RAG Confidence Changes

When testing retrieval/confidence changes:
1. Upload domain-specific tickets (e.g., all about "login" or all about "billing")
2. Query with a related question → expect confidence ≥ 0.3, citations > 0
3. Query with a completely unrelated question (e.g., "chocolate cake recipe") → expect confidence < 0.3, empty citations
4. Check cross-domain: query one domain against another domain's tickets → may or may not match depending on shared vocabulary

## Docker Testing

```bash
docker compose up -d --build
# Wait for backend healthcheck
curl -sf http://localhost:8000/health
# Teardown
docker compose down -v
```

The backend Dockerfile copies all source before `pip install .` (required for alembic to import app modules). The image includes `curl` for healthchecks.

## Devin Secrets Needed

None for mock mode testing. For OpenAI provider testing, `OPENAI_API_KEY` would be needed.
