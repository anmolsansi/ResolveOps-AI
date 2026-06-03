---
name: testing-resolveops-backend
description: Test the ResolveOps AI backend API and frontend end-to-end. Use when verifying RAG, upload, eval, dashboard, or UI changes.
---

# Testing ResolveOps AI

## Local Setup

```bash
cd backend
source .venv/bin/activate  # or: pip install -e ".[dev]"
```

No external credentials needed for mock mode (default).

## Running Tests

```bash
# All tests (61 as of V2)
python -m pytest -v

# Lint
python -m ruff check .

# Typecheck (CI runs with `|| true`, so mypy never fails CI; a couple of
# pre-existing non-blocking errors exist in retrieval.py / eval.py)
python -m mypy app --ignore-missing-imports
```

## Backend for manual / UI testing (SQLite + mock)

```bash
cd backend
source .venv/bin/activate
# Create tables on a throwaway DB
DATABASE_URL="sqlite:///./test_e2e.db" python -c "
from app.core.database import Base, engine
import app.models.models
Base.metadata.create_all(engine)
"
# Run the API (mock providers => no OpenAI calls)
DATABASE_URL="sqlite:///./test_e2e.db" MOCK_PROVIDERS=true uvicorn app.main:app --host 0.0.0.0 --port 8000
```

To reset between runs: `Base.metadata.drop_all(engine)` then `create_all(engine)`.

## Frontend E2E (V2 has a real UI)

```bash
cd frontend && npm run dev   # serves http://localhost:5173, proxies API to :8000
```

Pages: `/` (dashboard charts), `/upload` (CSV + downloadable invalid rows),
`/tickets` + `/tickets/{id}` (detail), `/rag` (answer, citations, retrieval
debug panel), `/eval` (question CRUD, run eval, CSV/JSON export).

Seed CSV for tests: `test_upload.csv` at repo root (5 valid login tickets +
2 invalid rows). For browser file-dialog reliability, copy it to
`~/Desktop/test_upload.csv` — the dialog remembers that location.

Good full UI flow: upload CSV -> check dashboard charts -> RAG query
"How to fix login issues?" (expect cited answer, debug boosts) -> click a
citation -> eval add/edit/delete -> run eval + export -> dashboard trends ->
cross-domain billing query (expect fallback).

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/tickets/upload` | POST | Upload CSV (multipart file) |
| `/tickets/{id}` | GET | Ticket detail + chunks |
| `/rag/query` | POST | RAG query; chunks include nested `debug` (cosine_score, keyword_boost, keyword_hits, matched_tokens) |
| `/eval/run` | POST | Run eval (uses DEFAULT_EVAL_QUESTIONS if none passed) |
| `/eval/questions` | GET/POST/PUT/DELETE | Saved eval question CRUD |
| `/eval/runs/{run_id}/export?format=csv|json` | GET | Export results |
| `/dashboard/quality` | GET | Ingestion quality metrics |
| `/dashboard/retrieval` | GET | Retrieval/query metrics + trends |

Note: in `/rag/query` responses the per-chunk debug fields are nested under a
`debug` key, e.g. `retrieved_chunks[i].debug.keyword_boost` — not at the top level.

## Mock Mode Behavior (V2)

- Default: `MOCK_PROVIDERS=true`, `EMBEDDING_PROVIDER=mock`
- Mock embeddings are deterministic with low cosine similarity (~ -0.1 to 0.1)
- **Keyword boost (mock only) is FRACTIONAL OVERLAP**, capped at `MAX_KEYWORD_BOOST = 0.7`:
  roughly `(matching_query_tokens / total_query_tokens) * 0.7`. A single shared
  token in a multi-token query yields a partial boost (e.g. ~0.23-0.35), NOT a
  full one. (This replaced the old additive `0.4 per hit`.)
- Confidence threshold: 0.3 (`app/core/config.py: low_confidence_threshold`)
- Related query (strong keyword overlap) -> confidence >= 0.3 -> cited answer
- Unrelated query -> confidence < 0.3 -> fallback answer
- **Cross-domain no longer leaks**: a billing query against login-only tickets
  stays below 0.3 (only the shared token "error" gives a small fractional boost),
  returning the fallback with no citations. Use this as the regression check.

## Gotcha: UUID path params on SQLite

Models use `UUID(as_uuid=True)` PKs. FastAPI path params that feed ORM filters
MUST be typed `uuid.UUID`, not `str` — a `str` causes
`AttributeError: 'str' object has no attribute 'hex'` (500) on SQLite for
PUT/DELETE/export by id. Type them as `uuid.UUID` so FastAPI coerces the value.

## Docker Testing

```bash
docker compose up -d --build
curl -sf http://localhost:8000/health
docker compose down -v
```

The Dockerfile copies all source before `pip install .` (alembic needs to import
app modules). The image includes `curl` for healthchecks.

## Devin Secrets Needed

None for mock mode. For OpenAI provider testing, `OPENAI_API_KEY` would be needed.
